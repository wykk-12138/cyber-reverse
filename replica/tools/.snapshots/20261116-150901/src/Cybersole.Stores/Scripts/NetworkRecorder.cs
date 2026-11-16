using System.Text.Json;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Records the network traffic of a storefront so a flow can be written against what the
/// site actually does instead of what its HTML suggests.
///
/// Why this exists: Farfetch, Goat and Scheels have no recoverable endpoint strings in the
/// binary (only display names), and guessing their JSON shapes produced the same class of
/// mistake as guessing the UI did — plausible, wrong, and impossible to notice without a
/// real run. Recording fixes that: load the page in <see cref="ChromiumBridge"/>, let the
/// site make its own calls, and read them back.
///
/// Usage:
/// <code>
/// await using var rec = await NetworkRecorder.BeginAsync();
/// await rec.VisitAsync("https://www.goat.com/sneakers/....");
/// await rec.WaitAsync(TimeSpan.FromSeconds(5));
/// foreach (var call in rec.Calls) Console.WriteLine(call);
/// </code>
/// </summary>
public sealed class NetworkRecorder : IAsyncDisposable
{
    private readonly ChromiumBridge _bridge;
    private readonly List<RecordedCall> _calls = new();

    private NetworkRecorder(ChromiumBridge bridge) => _bridge = bridge;

    /// <summary>Everything seen so far, oldest first.</summary>
    public IReadOnlyList<RecordedCall> Calls => _calls;

    /// <summary>
    /// Launch a browser with the Network domain on, ready to record.
    ///
    /// <paramref name="headed"/> defaults to true here: a headless session with a throwaway
    /// profile is what goat.com and scheels.com 403, so the recorder starts in the mode that
    /// actually gets traffic. Pass false when the target does not bot-detect.
    /// </summary>
    public static async Task<NetworkRecorder> BeginAsync(string? executable = null,
        bool headed = true, string? profilePath = null, CancellationToken ct = default)
    {
        var bridge = await ChromiumBridge.LaunchAsync(executable, 0, headed, profilePath, ct)
            .ConfigureAwait(false);

        // Network.enable is what makes Chromium push requestWillBeSent / responseReceived.
        await bridge.SendAsync("Network.enable", new { maxTotalBufferSize = 8 << 20 }, ct)
            .ConfigureAwait(false);

        return new NetworkRecorder(bridge);
    }

    /// <summary>Navigate and let the page's own XHRs fire.</summary>
    public async Task VisitAsync(string url, CancellationToken ct = default)
    {
        await _bridge.NavigateAsync(url, ct).ConfigureAwait(false);
        await HarvestAsync(ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Poll for a while so late XHRs (lazy product data, price feeds) land before the caller
    /// reads <see cref="Calls"/>.
    /// </summary>
    public async Task WaitAsync(TimeSpan duration, CancellationToken ct = default)
    {
        var deadline = DateTime.UtcNow + duration;

        while (DateTime.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            await Task.Delay(400, ct).ConfigureAwait(false);
            await HarvestAsync(ct).ConfigureAwait(false);
        }
    }

    /// <summary>Run an expression in the page (e.g. click "add to cart") and harvest what it triggers.</summary>
    public async Task<string?> RunAsync(string expression, CancellationToken ct = default)
    {
        var result = await _bridge.EvaluateAsync(expression, ct).ConfigureAwait(false);
        await HarvestAsync(ct).ConfigureAwait(false);
        return result;
    }

    /// <summary>
    /// Click at a point through CDP so the event carries <c>isTrusted: true</c>.
    ///
    /// The difference matters: <c>el.click()</c> from <c>RunAsync</c> dispatches a synthetic event
    /// with <c>isTrusted: false</c>, and bot walls check exactly that. Offspring was the case that
    /// forced this — its page arrives complete (192 KB from NetClient) but its DOM stays at 11
    /// divs, and adding the usual anti-automation launch flags changed <c>navigator.webdriver</c>
    /// to false without making the page render. So the refusal is downstream of the JS environment
    /// and this is the next candidate: real input events.
    ///
    /// Coordinates are CSS pixels in the viewport. A click is four CDP calls in order:
    /// mouseMoved → mousePressed → mouseReleased with clickCount, which is what a real pointer
    /// produces.
    /// </summary>
    public async Task MouseClickAsync(double x, double y, CancellationToken ct = default)
    {
        await _bridge.SendAsync("Input.dispatchMouseEvent", new
        {
            type = "mouseMoved", x, y, button = "none", buttons = 0,
        }, ct).ConfigureAwait(false);

        await _bridge.SendAsync("Input.dispatchMouseEvent", new
        {
            type = "mousePressed", x, y, button = "left", buttons = 1, clickCount = 1,
        }, ct).ConfigureAwait(false);

        // a real press is not instantaneous; some walls time it
        await Task.Delay(60, ct).ConfigureAwait(false);

        await _bridge.SendAsync("Input.dispatchMouseEvent", new
        {
            type = "mouseReleased", x, y, button = "left", buttons = 0, clickCount = 1,
        }, ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Find an element by CSS selector and click its centre through CDP, so the event is trusted.
    /// Returns the element's box, or null when nothing matched.
    /// </summary>
    public async Task<string?> MouseClickAsync(string selector, CancellationToken ct = default)
    {
        var box = await _bridge.EvaluateAsync($$"""
            (() => {
              const el = document.querySelector({{System.Text.Json.JsonSerializer.Serialize(selector)}});
              if (!el) return null;
              el.scrollIntoView({ block: 'center' });
              const r = el.getBoundingClientRect();
              return JSON.stringify({
                x: Math.round(r.left + r.width / 2),
                y: Math.round(r.top + r.height / 2),
                w: Math.round(r.width),
                h: Math.round(r.height)
              });
            })()
            """, ct).ConfigureAwait(false);

        if (string.IsNullOrEmpty(box)) return null;

        var doc = System.Text.Json.JsonDocument.Parse(box);
        var x = doc.RootElement.GetProperty("x").GetDouble();
        var y = doc.RootElement.GetProperty("y").GetDouble();

        await MouseClickAsync(x, y, ct).ConfigureAwait(false);
        await HarvestAsync(ct).ConfigureAwait(false);

        return box;
    }

    /// <summary>Move the pointer without pressing — some walls require a move before a click.</summary>
    public async Task MouseMoveAsync(double x, double y, CancellationToken ct = default) =>
        await _bridge.SendAsync("Input.dispatchMouseEvent", new
        {
            type = "mouseMoved", x, y, button = "none", buttons = 0,
        }, ct).ConfigureAwait(false);

    /// <summary>
    /// Read every link the rendered page actually contains.
    ///
    /// This is the answer to "where are the product URLs": storefront grids are built by
    /// JavaScript, so the static HTML has none — a 326 KB Casio category page carried only
    /// navigation and asset hrefs. After the page has rendered, the anchors are there, and
    /// reading them beats guessing path shapes (HBX's /products/{slug} turned out to be 404).
    ///
    /// Returns absolute URLs, de-duplicated, in document order.
    /// </summary>
    public async Task<List<string>> CollectLinksAsync(CancellationToken ct = default)
    {
        const string script = """
            JSON.stringify(
              Array.from(document.querySelectorAll('a[href]'))
                   .map(a => a.href)
                   .filter(h => h.startsWith('http'))
            )
            """;

        var raw = await _bridge.EvaluateAsync(script, ct).ConfigureAwait(false);
        if (string.IsNullOrWhiteSpace(raw)) return new List<string>();

        // Runtime.evaluate hands back a JSON-encoded string; unwrap then parse
        var json = raw.Trim();
        if (json.StartsWith('"') && json.EndsWith('"'))
            json = JsonSerializer.Deserialize<string>(json) ?? "[]";

        try
        {
            using var doc = JsonDocument.Parse(json);
            if (doc.RootElement.ValueKind != JsonValueKind.Array) return new List<string>();

            return doc.RootElement.EnumerateArray()
                .Select(e => e.GetString())
                .Where(s => !string.IsNullOrEmpty(s))
                .Select(s => s!)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
        }
        catch (JsonException)
        {
            return new List<string>();
        }
    }

    /// <summary>
    /// Links that look like a product detail page rather than navigation, a category, or a
    /// policy page. Heuristic on purpose: the caller still has to try one and see.
    /// </summary>
    public static IEnumerable<string> Productish(IEnumerable<string> links)
    {
        var skip = new[]
        {
            "/cart", "/checkout", "/login", "/account", "/sign-", "/help", "/policies",
            "/about", "/careers", "/returns", "/tracking", "/stores", "/brands",
        };

        return links.Where(h =>
        {
            var path = Uri.TryCreate(h, UriKind.Absolute, out var u) ? u.AbsolutePath : h;
            if (skip.Any(s => path.Contains(s, StringComparison.OrdinalIgnoreCase))) return false;

            // a product path usually has an id-ish tail: digits, or a trailing number
            return path.Contains("/p/", StringComparison.OrdinalIgnoreCase)
                   || path.Contains("/product", StringComparison.OrdinalIgnoreCase)
                   || path.Contains("/item", StringComparison.OrdinalIgnoreCase)
                   || path.Contains("/shop/", StringComparison.OrdinalIgnoreCase)
                   || System.Text.RegularExpressions.Regex.IsMatch(path, @"[-/]\d{4,}(\.html)?$");
        });
    }

    /// <summary>Pull new Network events out of the bridge's event buffer into <see cref="Calls"/>.</summary>
    private async Task HarvestAsync(CancellationToken ct = default)
    {
        // The bridge only reads its socket while a command is in flight, so a cheap no-op
        // command is what flushes any events the page has queued since the last call.
        try
        {
            await _bridge.SendAsync("Runtime.evaluate",
                new { expression = "1" }, ct).ConfigureAwait(false);
        }
        catch (Exception) { /* page mid-navigation; the events will come next round */ }

        foreach (var evt in _bridge.Events.ToArray())
        {
            if (!evt.TryGetProperty("method", out var methodProp)) continue;

            var method = methodProp.GetString();
            if (method is not ("Network.requestWillBeSent" or "Network.responseReceived")) continue;

            if (!evt.TryGetProperty("params", out var p)) continue;

            var requestId = p.TryGetProperty("requestId", out var rid) ? rid.GetString() : null;
            if (requestId is null) continue;

            if (method == "Network.requestWillBeSent")
            {
                if (!p.TryGetProperty("request", out var req)) continue;

                _calls.Add(new RecordedCall
                {
                    RequestId = requestId,
                    Method = req.TryGetProperty("method", out var m) ? m.GetString() : null,
                    Url = req.TryGetProperty("url", out var u) ? u.GetString() : null,
                    ResourceType = p.TryGetProperty("type", out var t) ? t.GetString() : null,
                    RequestHeaders = Snapshot(req, "headers"),
                });
            }
            else
            {
                if (!p.TryGetProperty("response", out var res)) continue;

                var existing = _calls.FirstOrDefault(c => c.RequestId == requestId);
                if (existing is null)
                {
                    existing = new RecordedCall { RequestId = requestId };
                    _calls.Add(existing);
                }

                existing.Status = res.TryGetProperty("status", out var s) ? s.GetInt32() : null;
                existing.MimeType = res.TryGetProperty("mimeType", out var mt) ? mt.GetString() : null;
                existing.ResponseHeaders = Snapshot(res, "headers");
            }
        }

        // the bridge never clears its own buffer; drop what we have consumed
        _bridge.Events.Clear();
    }

    private static Dictionary<string, string>? Snapshot(JsonElement parent, string property)
    {
        if (!parent.TryGetProperty(property, out var headers)) return null;
        if (headers.ValueKind != JsonValueKind.Object) return null;

        var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var h in headers.EnumerateObject())
            map[h.Name] = h.Value.ToString();

        return map.Count > 0 ? map : null;
    }

    /// <summary>Only the calls worth writing a flow against: XHR/fetch JSON, no assets.</summary>
    public IEnumerable<RecordedCall> ApiCalls => _calls.Where(c =>
        c.Url is not null &&
        !c.Url.Contains(".js", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".css", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".png", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".jpg", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".webp", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".svg", StringComparison.OrdinalIgnoreCase) &&
        !c.Url.Contains(".woff", StringComparison.OrdinalIgnoreCase));

    /// <summary>Render the recording as one line per call, ready to paste into a note.</summary>
    public string Describe()
    {
        var lines = new List<string>();

        foreach (var c in ApiCalls)
        {
            var status = c.Status?.ToString() ?? "---";
            lines.Add($"{status}  {c.Method ?? "?"}  {c.Url}");

            if (c.RequestHeaders is { Count: > 0 })
            {
                foreach (var (k, v) in c.RequestHeaders
                             .Where(kv => kv.Key.StartsWith("x-", StringComparison.OrdinalIgnoreCase)
                                          || kv.Key.Equals("content-type", StringComparison.OrdinalIgnoreCase)))
                    lines.Add($"      > {k}: {v}");
            }
        }

        return string.Join(Environment.NewLine, lines);
    }

    public async ValueTask DisposeAsync() => await _bridge.DisposeAsync().ConfigureAwait(false);
}

/// <summary>One request/response pair seen while recording.</summary>
public sealed class RecordedCall
{
    public string RequestId { get; set; } = string.Empty;
    public string? Method { get; set; }
    public string? Url { get; set; }
    public string? ResourceType { get; set; }
    public int? Status { get; set; }
    public string? MimeType { get; set; }
    public Dictionary<string, string>? RequestHeaders { get; set; }
    public Dictionary<string, string>? ResponseHeaders { get; set; }

    public override string ToString() =>
        $"{Status?.ToString() ?? "---"}  {Method ?? "?"}  {Url}";
}
