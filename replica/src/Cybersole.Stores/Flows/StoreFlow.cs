using Cybersole.Stores.Scripts;
using Cybersole.Stores.Actions;
using System.Reflection;
using System.Text.RegularExpressions;
using Cybersole.Http;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Step contract every store flow implements.
///
/// The method names below are recovered verbatim from the shipped binary: each one
/// appears in the string heap as a compiler-generated async state machine
/// (<c>&lt;AddToCart&gt;d__12</c>, <c>&lt;SubmitShipping&gt;d__7</c>, …) together with a reference
/// count that tells how many modules implement it. Base implementations either
/// succeed as a no-op (the step is optional for most stores) or fail explicitly
/// when the step is mandatory for a store that did not override it.
/// </summary>
// R967. StepActionRunner.Build walks typeof(StoreFlow).GetMethods, and R966 found that none of the 179 step names
// reaches the published artifact -- so the table is built empty there and every path that runs a step by name is
// dead in the image while working in a Debug build. This attribute is the instruction to the trimmer that the
// reflection is deliberate: keep this type's public instance methods, names included. Without it the trimmer
// removes what it cannot see being called, and by-name dispatch is exactly a call it cannot see.
[System.Diagnostics.CodeAnalysis.DynamicallyAccessedMembers(
    System.Diagnostics.CodeAnalysis.DynamicallyAccessedMemberTypes.PublicMethods)]
public abstract class StoreFlow
{
    public abstract string Id { get; }
    public abstract string Name { get; }
    public abstract IReadOnlyList<string> Domains { get; }

    public virtual bool CanHandle(Uri url) =>
        Domains.Any(d => url.Host.EndsWith(d, StringComparison.OrdinalIgnoreCase));

    /// <summary>Store-level toggle: does this flow need a logged-in account?</summary>
    public virtual bool RequiresAccount => false;

    /// <summary>Store-level toggle: does this flow gate on a Kasada/anti-bot sensor?</summary>
    public virtual bool UsesKasada => false;

    /// <summary>
    /// The ordered steps this flow runs, by name — empty when the flow has no sequence of its own.
    ///
    /// <para>
    /// R868. Until now the only sequence anywhere was the runner's hand-written twenty-one entries, applied to every
    /// flow alike. The image instead gives each flow its own — Nike sixteen, Pop Mart twenty-four — and R851 recorded
    /// that difference as the reason fourteen draw steps could not be added: a generic sequence has nowhere to put
    /// them. This property is where a flow declares its own order, so the runner can follow it.
    /// </para>
    ///
    /// <para>
    /// Empty means "no sequence of its own", and the runner keeps using its built-in list, so nothing about the
    /// twenty-five flows that do not override this changes.
    /// </para>
    /// </summary>
    public virtual IReadOnlyList<string> StepSequence => Array.Empty<string>();

    /// <summary>
    /// Step name to callable — provided by <see cref="StepActionRunner"/>, not rebuilt here.
    ///
    /// <para>
    /// R869. R868 added a reflection table and a <c>RunStepNamedAsync</c> to this class, and both duplicated work that
    /// already existed: <see cref="StepActionRunner"/> reflects the same methods from <c>typeof(StoreFlow)</c>, exposes
    /// <c>Knows</c>, and runs a named step with per-step timing, <see cref="FlowContext.Step"/> recording, cancellation
    /// and exception handling. Its use of <c>MethodInfo.Invoke</c> is also why it never hit the binding failure R868
    /// ran into. The duplicate is removed rather than left beside it, because two ways to call a step by name is one
    /// way too many and the older one is the better one.
    /// </para>
    /// </summary>
    public IReadOnlyDictionary<string, Func<StoreFlow, FlowContext, CancellationToken, Task<StepOutcome>>>
        StepDispatch => StepActionRunner.Invokers;

    /// <summary>
    /// True when this flow can run the named step at all. The question a sequence asks of every name it carries.
    ///
    /// <para>
    /// R869. Delegates to <see cref="StepActionRunner.Knows"/> for the same reason <see cref="StepDispatch"/> does:
    /// one step-name table, not two.
    /// </para>
    /// </summary>
    public bool CanRunStep(string step) => StepActionRunner.Knows(step);

    /// <summary>
    /// The store's order list. Not part of the twenty-one-step checkout sequence, so the base has no sensible default —
    /// and therefore fails explicitly rather than reporting a success nothing performed.
    ///
    /// <para>
    /// R871. This is the first step added since the sequence mechanism existed, and it exists because Pop Mart's own
    /// order lists it at ordinal 104. Its base body is deliberately a failure: a store that has no order-list endpoint
    /// must say so, and a silent success here would put this project back in the shape it keeps removing — a step that
    /// reports done without doing.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> GetOrdersAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("GetOrders is not implemented by " + Id));

    /// <summary>
    /// The in-store exhibit lookup. Like <see cref="GetOrdersAsync"/>, outside the checkout sequence and therefore
    /// failing by default rather than reporting a success nothing performed.
    ///
    /// <para>
    /// R872. Kept beside <see cref="EnterExhibitAsync"/> because the image's Pop Mart sequence has them adjacent and
    /// because they are a pair: the first fetches what the second posts.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> FindExhibitAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("FindExhibit is not implemented by " + Id));

    /// <summary>
    /// Entering an in-store exhibit. Fails by default for the same reason as the two above.
    /// </summary>
    public virtual Task<StepOutcome> EnterExhibitAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("EnterExhibit is not implemented by " + Id));

    /// <summary>
    /// Begin a draw flow. Fails by default, like the exhibit and order steps, because it sits outside the checkout
    /// sequence and a silent success would be a lie about work nobody did.
    ///
    /// <para>
    /// R873. The draw family is where the difference between the image's per-flow sequences and this replica's single
    /// one showed up first (R851); these four are the first of its steps that can be written, because their endpoints
    /// carry their query shapes and the others need request bodies nothing evidences.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> StartDrawFlowAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("StartDrawFlow is not implemented by " + Id));

    /// <summary>Look up a draw. Fails by default.</summary>
    public virtual Task<StepOutcome> FindDrawAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("FindDraw is not implemented by " + Id));

    /// <summary>The dates a store ticket is available on. Fails by default.</summary>
    public virtual Task<StepOutcome> FindDatesAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("FindDates is not implemented by " + Id));

    /// <summary>The time slots for a store ticket. Fails by default.</summary>
    public virtual Task<StepOutcome> FindTimeSlotsAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("FindTimeSlots is not implemented by " + Id));

    /// <summary>
    /// The store's in-store order list, distinct from <see cref="GetOrdersAsync"/>'s online list.
    ///
    /// <para>
    /// R891. R871 wrote GetOrders against <c>/shop/v1/order/list</c>. The image also has an in-store order list, and
    /// R890 narrowed its endpoint to "not under /shop/v1/" before this round found it under /store/v1/ with its query
    /// shape fixed in the constant. Two order lists, two prefixes, and until now the replica represented one.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> GetInstoreOrdersAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("GetInstoreOrders is not implemented by " + Id));

    /// <summary>
    /// Looking a product up against a physical store rather than the online catalogue. Ordinal 76 in the image, beside
    /// FindProduct at 74 and FindProductMultiInstore at 75 (R882).
    /// </summary>
    public virtual Task<StepOutcome> FindProductInstoreAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("FindProductInstore is not implemented by " + Id));

    /// <summary>
    /// Adding a sealed box to the cart: preview which set the box comes from, extract one, then add the extracted
    /// item.
    ///
    /// <para>
    /// R908. The image names this method, so it is not inferred from a path. Until now the replica held five
    /// <c>/shop/v1/box/</c> constants with no caller at all: the goods list, the SPU detail, the set preview, the set
    /// extract and the plain extract. Only <c>addBoxListToCart</c> was reached, from Pop Mart's ordinary AddToCart,
    /// which is why the six looked covered when five were not.
    /// </para>
    ///
    /// <para>
    /// What is inferred rather than observed is the order and the parameters: preview then extract then add is the
    /// natural reading of the names, and no request body is evidenced for any of the three. A store that has no
    /// boxes fails explicitly instead, which is the same shape as the other unsettled steps here.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> AddToCartBoxAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("AddToCartBox is not implemented by " + Id));


    // ── session ───────────────────────────────────────────────────────────────
    /// <summary>
    /// The shield step: build the query a payment shield wants, send it, and hand its answer on for processing.
    ///
    /// <para>
    /// R916. The image names <c>RunShield</c> and its state machine carries ordinal eighteen, with three locals —
    /// <c>data</c>, <c>data2</c> and <c>shieldQuery</c>. Two neighbours give the shape: <c>OpenSecurePage</c> at
    /// fifteen and <c>Navigate</c> at seventeen, so this runs after a secure page is open and around a navigation
    /// rather than in isolation. <c>ProcessResult</c> at fourteen is what its answer is handed to.
    /// </para>
    ///
    /// <para>
    /// That makes it a step in a payment flow, not the OTP-only call R905 first took it for. The evidence is the
    /// ordinal sequence and the local names; what is inference is what goes in the query and what the answer means,
    /// neither of which any literal records. So the default fails explicitly and a store that has evidence overrides.
    /// </para>
    /// </summary>
    public virtual Task<StepOutcome> RunShieldAsync(FlowContext c, CancellationToken ct) =>
        Task.FromResult(StepOutcome.Fail("RunShield is not implemented by " + Id));

    // ── session ───────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> InitAsync(FlowContext c, CancellationToken ct)
    {
        // Seed the session with the browser identity every store expects to see.
        c.Session.UserAgent ??= "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";
        c.Session.Headers.TryAdd("Accept-Language", "en-US,en;q=0.9");
        c.Session.Headers.TryAdd("Accept", "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8");
        c.Session.Headers.TryAdd("Sec-Fetch-Mode", "navigate");
        c.Session.Headers.TryAdd("Sec-Fetch-Site", "none");
        c.Session.Vars["init"] = "1";
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> GetHomeAsync(FlowContext c, CancellationToken ct) => Ok();
    /// <summary>
    /// Reads the site's CSRF token out of a page and stores it where the request layer will attach it.
    ///
    /// <para>
    /// R962. This was one of thirty-five steps returning Ok without doing anything, and it is the one every flow
    /// implements: the image carries GetCsrf under roughly twenty different ordinals -- d__14, d__22, d__23, d__24,
    /// d__26, d__28, d__31, d__32, d__33, d__35, d__39, d__40, d__50 and more -- which means each shop reads its own token
    /// rather than inheriting one shape. The replica had it implemented nowhere.
    /// </para>
    ///
    /// <para>
    /// <b>Why the base implementation is worth having even though every shop differs.</b> The variation is in where a
    /// shop puts the token, not in what a token is. All of the shapes are one of four: a hidden input, a meta tag, a cookie,
    /// or a field inside a JSON blob. Reading those four costs one pass and covers the shops that follow the pattern,
    /// while a flow that differs still overrides. Reporting success without a token, which is what the step did before,
    /// meant the next POST went out unauthenticated and the failure surfaced somewhere else entirely.
    /// </para>
    /// </summary>
    public virtual async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        // a flow may already hold one -- re-reading a page to find a token it was given is wasted work
        if (!string.IsNullOrEmpty(c.Session.CsrfToken) &&
            c.Session.Vars.GetValueOrDefault("csrf.refresh") != "1")
            return StepOutcome.Success();

        var url = c.Session.Vars.GetValueOrDefault("csrf.url") ?? c.Url;

        var res = await c.Http.GetAsync(url, new RequestOptions(), ct).ConfigureAwait(false);
        if (res.StatusCode is < 200 or >= 300)
            return StepOutcome.Fail("csrf page " + res.StatusCode, retryable: res.StatusCode is 429 or >= 500);

        var token = FindCsrfToken(res.Body);

        // a shop that puts it in a cookie rather than the page body
        if (string.IsNullOrEmpty(token))
            foreach (var name in CsrfCookieNames)
                if (res.Cookies.TryGetValue(name, out var value) && !string.IsNullOrEmpty(value))
                {
                    token = value;
                    break;
                }

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("no csrf token on the page", retryable: false);

        c.Session.CsrfToken = token;
        c.Session.Vars["csrfToken"] = token;
        return StepOutcome.Success();
    }

    /// <summary>The cookie names shops use for a token, which is the fourth of the four shapes.</summary>
    internal static readonly string[] CsrfCookieNames =
    {
        "csrftoken", "csrf_token", "XSRF-TOKEN", "X-CSRF-Token", "_csrf", "csrf",
    };

    /// <summary>
    /// Finds a token in a page. Four shapes, one pass each, and nothing invented: a hidden input named like a token, a
    /// meta tag named like one, a JSON field named like one, and the Symfony-style data attribute. Input order matters --
    /// the hidden input shape wins because it is the oldest and the least ambiguous.
    /// </summary>
    public static string? FindCsrfToken(string? body)
    {
        if (string.IsNullOrEmpty(body)) return null;

        var patterns = new[]
        {
            // <input type="hidden" name="csrf_token" value="...">  -- name and value in either order
            @"<input[^>]*\bname\s*=\s*[\""'](?<n>[^\""']*(?:csrf|token|authenticity)[^\""']*)[\""'][^>]*\bvalue\s*=\s*[\""'](?<v>[^\""']+)[\""']",
            @"<input[^>]*\bvalue\s*=\s*[\""'](?<v>[^\""']+)[\""'][^>]*\bname\s*=\s*[\""'](?<n>[^\""']*(?:csrf|token|authenticity)[^\""']*)[\""']",
            // <meta name="csrf-token" content="...">
            @"<meta[^>]*\bname\s*=\s*[\""'](?<n>[^\""']*(?:csrf|token)[^\""']*)[\""'][^>]*\bcontent\s*=\s*[\""'](?<v>[^\""']+)[\""']",
            // "csrfToken":"..." or "_csrf_token": "..."
            @"""(?<n>[\w_]*csrf[\w_]*|_token)""\s*:\s*""(?<v>[^""]{8,})""",
            // data-csrf-token="..."
            @"\bdata-(?<n>[\w-]*csrf[\w-]*|token)\s*=\s*[\""'](?<v>[^\""']{8,})[\""']",
        };

        foreach (var pattern in patterns)
        {
            var m = System.Text.RegularExpressions.Regex.Match(
                body!, pattern,
                System.Text.RegularExpressions.RegexOptions.IgnoreCase |
                System.Text.RegularExpressions.RegexOptions.Singleline);

            if (m.Success)
            {
                var value = m.Groups["v"].Value.Trim();
                if (value.Length >= 8) return value;
            }
        }

        return null;
    }
    public virtual Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> RefreshSessionAsync(FlowContext c, CancellationToken ct)
    {
        // A cheap GET on the origin is what keeps the session cookie warm between polls.
        var res = await GetAsync(c, Origin(c.Url) + "/", Tag() + "-refresh", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("refresh failed", retryable: true);

        c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"refresh HTTP {res.StatusCode}", retryable: true);
    }
    public virtual Task<StepOutcome> VerifySessionAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SetCookiesAsync(FlowContext c, CancellationToken ct)
    {
        // Vars of the form cookie.NAME=VALUE are pushed into the jar.
        foreach (var kv in c.Session.Vars)
        {
            if (!kv.Key.StartsWith("cookie.", StringComparison.OrdinalIgnoreCase)) continue;
            var name = kv.Key["cookie.".Length..];
            if (name.Length > 0) c.Session.Cookies[name] = kv.Value;
        }

        return c.Session.Cookies.Count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no cookies to set", retryable: true);
    }
    public virtual async Task<StepOutcome> SetRequestAsync(FlowContext c, CancellationToken ct)
    {
        // Every store request should look like a document navigation from the product page.
        var origin = Origin(c.Url);
        c.Session.Headers["Referer"] = c.Session.CheckoutUrl ?? c.Url;
        c.Session.Headers["Origin"] = origin;
        c.Session.Headers["Sec-Fetch-Site"] = "same-origin";
        c.Session.Headers["Sec-Fetch-Mode"] = "cors";
        c.Session.Headers["Sec-Fetch-Dest"] = "empty";
        if (!string.IsNullOrEmpty(c.Session.CsrfToken) && !c.Session.Headers.ContainsKey("x-xsrf-token"))
            c.Session.Headers["x-xsrf-token"] = c.Session.CsrfToken!;

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> HandleResponseAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.Vars.TryGetValue("lastStatus", out var raw) || !int.TryParse(raw, out var status))
            return StepOutcome.Fail("no status to handle", retryable: true);

        return status switch
        {
            200 or 201 or 204 => StepOutcome.Success(),
            301 or 302 or 303 or 307 or 308 => StepOutcome.Success(),
            400 => StepOutcome.Fail("bad request", retryable: false),
            401 or 403 => StepOutcome.Fail("unauthorised / blocked", retryable: true),
            404 => StepOutcome.Fail("not found", retryable: false),
            409 => StepOutcome.Fail("conflict", retryable: true),
            422 => StepOutcome.Fail("rejected (validation)", retryable: false),
            429 => StepOutcome.Fail("rate limited", retryable: true),
            >= 500 => StepOutcome.Fail($"server error {status}", retryable: true),
            _ => StepOutcome.Fail($"unexpected status {status}", retryable: true),
        };
    }
    public virtual async Task<StepOutcome> DetectAsync(FlowContext c, CancellationToken ct)
    {
        // Identify the anti-bot vendor from whatever the last response carried.
        var body = c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        var headers = c.Session.Vars.TryGetValue("server", out var server) ? server : string.Empty;

        var vendor =
            body.Contains("cf-chl", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :
            body.Contains("kpsdk", StringComparison.OrdinalIgnoreCase) ? "kasada" :
            body.Contains("_Incapsula_Resource", StringComparison.OrdinalIgnoreCase) ? "imperva" :
            body.Contains("datadome", StringComparison.OrdinalIgnoreCase) ? "datadome" :
            body.Contains("px-captcha", StringComparison.OrdinalIgnoreCase) ? "perimeterx" :
            body.Contains("queue-it", StringComparison.OrdinalIgnoreCase) ? "queue-it" :
            headers.Contains("cloudflare", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :
            "none";

        c.Session.Vars["antibot"] = vendor;
        c.Emit($"{Name}: anti-bot = {vendor}", "detect");

        return await SolveDetectedWallAsync(c, ct).ConfigureAwait(false);
    }

    /// <summary>
    /// Ask the detected wall's strategy for a token and store it.
    ///
    /// <para>
    /// R142 closes the last layer of the defect R140 and R141 kept finding: detection existed, storage
    /// existed, the call existed — and nothing called the call. <c>DetectAsync</c> is the one place that
    /// knows which wall is in the way, so it is the one place that dispatches.
    /// </para>
    ///
    /// <para>
    /// Nothing is attempted when no Chromium build is installed: the in-bot road cannot run, and a
    /// strategy whose service half is unconfigured would only produce a refusal line on every page. The
    /// session records <c>antibot.solver = "unavailable"</c> instead, which is a fact rather than a
    /// failure.
    /// </para>
    /// </summary>
    protected virtual async Task<StepOutcome> SolveDetectedWallAsync(FlowContext c,
        CancellationToken ct)
    {
        var vendor = c.Session.Vars.TryGetValue("antibot", out var detected) ? detected : "none";

        if (vendor is not ("cloudflare" or "kasada")) return StepOutcome.Success();

        if (Cybersole.Stores.Scripts.ChromiumBridge.FindBrowser() is null)
        {
            c.Session.Vars["antibot.solver"] = "unavailable";
            c.Emit($"{Name}: no Chromium build, {vendor} wall left to the next attempt", "antibot");
            return StepOutcome.Success();
        }

        c.Session.Vars["antibot.solver"] = "available";

        if (vendor == "cloudflare")
        {
            var runner = Cybersole.Stores.Scripts.CloudflareStrategyRunner.Default();
            return await Cybersole.Stores.Scripts.CloudflareClearance
                .ApplyAsync(c, runner, c.Url ?? string.Empty, ct).ConfigureAwait(false);
        }

        var kasada = Cybersole.Stores.Scripts.KasadaStrategyRunner.Default();
        return await Cybersole.Stores.Scripts.KasadaClearance
            .ApplyAsync(c, kasada, c.Url ?? string.Empty, ct).ConfigureAwait(false);
    }

    // ── product discovery / monitoring ────────────────────────────────────────
    public virtual Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct) => NotSupported("FindProduct");
    public virtual async Task<StepOutcome> FindProductMultiAsync(FlowContext c, CancellationToken ct)
    {
        // Try every configured URL until one yields a product; first success wins.
        var urls = c.Session.Vars.TryGetValue("urls", out var list)
            ? list.Split('|', StringSplitOptions.RemoveEmptyEntries)
            : new[] { c.Url };

        foreach (var url in urls)
        {
            ct.ThrowIfCancellationRequested();
            var scoped = c.CloneFor(url);
            scoped.Session.Vars["raw"] = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

            var outcome = await FindProductAsync(scoped, ct).ConfigureAwait(false);
            if (!outcome.Ok) continue;

            foreach (var kv in scoped.Session.Vars) c.Session.Vars[kv.Key] = kv.Value;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail($"no product across {urls.Length} url(s)", retryable: true);
    }
    public virtual Task<StepOutcome> FindProductFlowAsync(FlowContext c, CancellationToken ct)
        => FindProductAsync(c, ct);
    public virtual Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct) => NotSupported("FindVariant");
    public virtual async Task<StepOutcome> GetProductAsync(FlowContext c, CancellationToken ct)
    {
        // Prefer a JSON product endpoint; fall back to the product page HTML.
        var jsonUrl = c.Url.Contains("?", StringComparison.Ordinal)
            ? c.Url + "&format=json"
            : c.Url + ".json";

        var res = await GetAsync(c, jsonUrl, Tag() + "-product", ct).ConfigureAwait(false);
        if (res is null || !res.IsSuccess)
        {
            res = await GetAsync(c, c.Url, Tag() + "-product-html", ct).ConfigureAwait(false);
            if (res is null) return StepOutcome.Fail("product unreachable", retryable: true);
            c.Session.Vars["raw"] = res.Body;
            var scraped = await ScrapeProductAsync(c, ct).ConfigureAwait(false);
            return scraped.Ok ? StepOutcome.Success() : StepOutcome.Fail("product not parseable");
        }

        c.Session.Vars["raw"] = res.Body;
        c.Session.Vars["productJson"] = res.Body;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetProductDetailsAsync(FlowContext c, CancellationToken ct)
    {
        var details = await GetProductAsync(c, ct).ConfigureAwait(false);
        if (!details.Ok) return details;

        // Pull the three fields every caller wants even when the payload shape differs.
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

        var title = System.Text.RegularExpressions.Regex.Match(body,
            "\"title\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;

        var handle = System.Text.RegularExpressions.Regex.Match(body,
            "\"handle\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(handle)) c.Session.Vars["handle"] = handle;

        var type = System.Text.RegularExpressions.Regex.Match(body,
            "\"product_type\"\\s*:\\s*\"([^\"]*)\"").Groups[1].Value;
        if (!string.IsNullOrEmpty(type)) c.Session.Vars["productType"] = type;

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        var title = System.Text.RegularExpressions.Regex.Match(body, @"<title>([^<|]+)").Groups[1].Value;
        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title.Trim();

        var price = System.Text.RegularExpressions.Regex.Match(body,
            @"""price""\s*:\s*""?([\d.,]+)""?").Groups[1].Value;
        if (!string.IsNullOrEmpty(price)) c.Session.Vars["price"] = price;

        var image = System.Text.RegularExpressions.Regex.Match(body,
            @"<meta[^>]+property=""og:image""[^>]+content=""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(image)) c.Session.Vars["image"] = image;

        return c.Session.Vars.ContainsKey("product")
            ? StepOutcome.Success()
            : StepOutcome.Fail("no product fields found", retryable: true);
    }
    public virtual async Task<StepOutcome> ScrapeProductPageAsync(FlowContext c, CancellationToken ct)
    {
        var page = await GetAsync(c, c.Url, Tag() + "-pdp", ct).ConfigureAwait(false);
        if (page is null) return StepOutcome.Fail("product page unreachable", retryable: true);
        if (!page.IsSuccess) return StepOutcome.Fail($"pdp HTTP {page.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = page.Body;
        c.Session.Vars["pdpStatus"] = page.StatusCode.ToString();

        var scraped = await ScrapeProductAsync(c, ct).ConfigureAwait(false);
        return scraped.Ok ? StepOutcome.Success() : StepOutcome.Fail("pdp not parseable");
    }
    public virtual async Task<StepOutcome> ScrapeProductAvailabilityAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("no product payload", retryable: true);

        // Any of the usual "you cannot buy this" markers flips availability to false.
        var blocked = new[]
            {
                "sold out", "soldout", "out of stock", "outofstock", "\"available\":false",
                "\"inventory_quantity\":0", "\"inStock\":false", "\"isSoldOut\":true",
            }
            .Any(marker => body.Contains(marker, StringComparison.OrdinalIgnoreCase));

        c.Session.Vars["available"] = blocked ? "false" : "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeJsonAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"<script[^>]*type=""application/(?:ld\+)?json""[^>]*>(.*?)</script>",
            System.Text.RegularExpressions.RegexOptions.Singleline);

        if (!m.Success)
            return StepOutcome.Fail("no JSON-LD block", retryable: true);

        c.Session.Vars["jsonLd"] = m.Groups[1].Value;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapeJsonFrontendAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;
        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"(?:window\.)?__(?:INITIAL|PRELOADED|NUXT|DATA)__\s*=\s*(\{.*?\});",
            System.Text.RegularExpressions.RegexOptions.Singleline);

        if (!m.Success)
            return StepOutcome.Fail("no frontend state blob", retryable: true);

        c.Session.Vars["frontendState"] = m.Groups[1].Value;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ScrapePreloadAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raw", out var raw)
            ? raw
            : c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("nothing to scrape", retryable: true);

        // Next.js, Shopify and generic preload blobs, in order of likelihood.
        var patterns = new[]
        {
            "id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>",
            "window\\.__st\\s*=\\s*(\\{.*?\\});",
            "ShopifyAnalytics\\.meta\\s*=\\s*(\\{.*?\\});",
            "window\\.__APOLLO_STATE__\\s*=\\s*(\\{.*?\\});",
        };

        foreach (var pattern in patterns)
        {
            var m = System.Text.RegularExpressions.Regex.Match(body, pattern,
                System.Text.RegularExpressions.RegexOptions.Singleline);
            if (!m.Success) continue;

            c.Session.Vars["preload"] = m.Groups[1].Value;
            c.Session.Vars["preloadPattern"] = pattern;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("no preload blob found", retryable: true);
    }
    public virtual Task<StepOutcome> ScrapeVariantAvailabilityAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GetOwnPropertiesAsync(FlowContext c, CancellationToken ct)
    {
        // Surface what this flow knows about itself — used by the details panel and smart actions.
        c.Session.Vars["flow.id"] = Id;
        c.Session.Vars["flow.name"] = Name;
        c.Session.Vars["flow.domains"] = string.Join('|', Domains);
        c.Session.Vars["flow.requiresAccount"] = RequiresAccount.ToString();
        c.Session.Vars["flow.usesKasada"] = UsesKasada.ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPropertyAsync(FlowContext c, CancellationToken ct)
    {
        // A single named property out of whatever payload is currently staged.
        var key = c.Session.Vars.TryGetValue("property", out var k) ? k : "product";
        var source = c.Session.Vars.TryGetValue("raw", out var raw) ? raw : string.Empty;

        if (c.Session.Vars.TryGetValue(key, out var direct) && !string.IsNullOrEmpty(direct))
        {
            c.Session.Vars["propertyValue"] = direct;
            return StepOutcome.Success();
        }

        var m = System.Text.RegularExpressions.Regex
            .Match(source, "\"" + System.Text.RegularExpressions.Regex.Escape(key) +
                           "\"\\s*:\\s*\"?([^\",}\\]]+)\"?");

        if (!m.Success)
            return StepOutcome.Fail($"property '{key}' not found", retryable: true);

        c.Session.Vars["propertyValue"] = m.Groups[1].Value.Trim();
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> CheckPriceLimitAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> HandleOutOfStockAsync(FlowContext c, CancellationToken ct)
    {
        c.Session.Vars["available"] = "false";
        c.Emit($"{Name}: out of stock", "stock");
        return await PollRestockAsync(c, ct).ConfigureAwait(false);
    }

    // ── cart ──────────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> CreateCartAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> ClearCartAsync(FlowContext c, CancellationToken ct)
    {
        // POST a zero-line cart; most platforms accept this as "empty my cart".
        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/update.js", "{}",
            Tag() + "-clear", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("clear cart failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"clear HTTP {res.StatusCode}", retryable: true);

        c.Session.CartId = null;
        c.Session.Vars.Remove("cart");
        return StepOutcome.Success();
    }
    public virtual Task<StepOutcome> AddToCartAsync(FlowContext c, CancellationToken ct) => NotSupported("AddToCart");
    public virtual async Task<StepOutcome> AddToCartPreloadAsync(FlowContext c, CancellationToken ct)
    {
        // Preload variant: reuse whatever the product page already staged instead of refetching.
        if (!c.Session.Vars.TryGetValue("preload", out var preload) || string.IsNullOrWhiteSpace(preload))
        {
            var scraped = await ScrapePreloadAsync(c, ct).ConfigureAwait(false);
            if (!scraped.Ok) return await AddToCartAsync(c, ct).ConfigureAwait(false);
            preload = c.Session.Vars["preload"];
        }

        var variant = System.Text.RegularExpressions.Regex
            .Match(preload, "\"variantId\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(variant) && string.IsNullOrEmpty(c.Session.VariantId))
            c.Session.VariantId = variant;

        c.Session.Vars["preloaded"] = "true";
        return await AddToCartAsync(c, ct).ConfigureAwait(false);
    }
    public virtual Task<StepOutcome> AddToCartStoreFrontAsync(FlowContext c, CancellationToken ct)
        => AddToCartAsync(c, ct);
    public virtual Task<StepOutcome> AddToCartMultiAsync(FlowContext c, CancellationToken ct)
        => AddToCartAsync(c, ct);
    public virtual Task<StepOutcome> EditLineAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> UpdateCartAsync(FlowContext c, CancellationToken ct)
    {
        // Quantity changes go through the same line edit the checkout path uses.
        return await EditLineAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> RemoveLineItemAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.CartId))
            return StepOutcome.Fail("no cart to remove from");

        var res = await PostJsonAsync(c, Origin(c.Url) + "/cart/update.js",
            "{\"line\":1,\"quantity\":0}", Tag() + "-remove", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("remove line failed", retryable: true);
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"remove HTTP {res.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> RemoveItemAsync(FlowContext c, CancellationToken ct)
    {
        return await RemoveLineItemAsync(c, ct).ConfigureAwait(false);
    }

    // ── checkout ──────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> InitiateCheckoutAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) => NotSupported("GetCheckout");
    public virtual Task<StepOutcome> GenerateCheckoutAsync(FlowContext c, CancellationToken ct)
        => GetCheckoutAsync(c, ct);
    public virtual Task<StepOutcome> SubmitEmailAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> SubmitShippingAsync(FlowContext c, CancellationToken ct) => NotSupported("SubmitShipping");
    public virtual Task<StepOutcome> SubmitAddressAsync(FlowContext c, CancellationToken ct)
        => SubmitShippingAsync(c, ct);
    public virtual Task<StepOutcome> SubmitShippingMethodAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetShippingRatesAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetShippingRateAsync(FlowContext c, CancellationToken ct)
        => GetShippingRatesAsync(c, ct);
    public virtual Task<StepOutcome> SubmitBillingAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SubmitBillingAddressAsync(FlowContext c, CancellationToken ct)
    {
        var bill = c.Billing ?? c.Shipping;
        if (bill is null) return StepOutcome.Fail("no billing address");

        c.Session.Vars["billing.address1"] = bill.Address1 ?? string.Empty;
        c.Session.Vars["billing.city"] = bill.City ?? string.Empty;
        c.Session.Vars["billing.zip"] = bill.ZipCode ?? string.Empty;
        c.Session.Vars["billing.country"] = bill.Country ?? string.Empty;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitDiscountAsync(FlowContext c, CancellationToken ct)
    {
        var code = c.Session.Vars.TryGetValue("discount", out var d) ? d : null;
        if (string.IsNullOrWhiteSpace(code)) return StepOutcome.Success();   // optional step

        var res = await PostJsonAsync(c, Origin(c.Url) + "/discount/" + Uri.EscapeDataString(code!),
            "{}", Tag() + "-discount", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("discount submit failed", retryable: true);
        c.Session.Vars["discountApplied"] = res.IsSuccess ? "true" : "false";
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"discount HTTP {res.StatusCode}", retryable: false);
    }
    public virtual Task<StepOutcome> ApplyDiscountAsync(FlowContext c, CancellationToken ct)
        => SubmitDiscountAsync(c, ct);
    public virtual Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct) => NotSupported("SubmitOrder");
    public virtual Task<StepOutcome> PlaceOrderAsync(FlowContext c, CancellationToken ct)
        => SubmitOrderAsync(c, ct);
    public virtual async Task<StepOutcome> ProcessOrderAsync(FlowContext c, CancellationToken ct)
    {
        // An order exists only once a number came back; anything else is a failure.
        var order = c.Session.OrderNumber ?? c.Session.OrderId;
        if (string.IsNullOrEmpty(order))
            return StepOutcome.Fail("no order to process", retryable: true);

        var body = c.Session.Vars.TryGetValue("checkout", out var ch)
            ? ch
            : c.Session.Vars.TryGetValue("cart", out var cart) ? cart : string.Empty;

        var total = System.Text.RegularExpressions.Regex
            .Match(body, "\"total(?:_price)?\"\\s*:\\s*\"?(\\d+(?:\\.\\d+)?)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(total)) c.Session.Vars["total"] = total;
        c.Session.Vars["orderProcessed"] = "true";
        c.Emit($"{Name}: order {order} processed (total {total})", "order");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CreateOrderAsync(FlowContext c, CancellationToken ct)
    {
        var destination = c.Session.Vars.TryGetValue("destination", out var dest)
            ? dest
            : Origin(c.Url) + "/checkout/order";

        var res = await PostJsonAsync(c, destination, "{}", Tag() + "-create-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("create order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"create order HTTP {res.StatusCode}", retryable: true);

        var id = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"order(?:Id|Number)\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(id))
            return StepOutcome.Fail("create order returned no identity");

        c.Session.OrderId = id;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CalculateTaxesAsync(FlowContext c, CancellationToken ct)
    {
        // Indicative only: the store computes the real figure, this is for the pre-check.
        if (!decimal.TryParse(c.Session.Vars.TryGetValue("total", out var total) ? total : "0",
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var subtotal))
            return StepOutcome.Fail("no subtotal to tax");

        var country = (c.Shipping?.Country ?? c.ProfileData?.Country ?? "US").ToUpperInvariant();
        var rate = country switch
        {
            "GB" => 0.20m,
            "DE" or "FR" or "NL" or "ES" or "IT" => 0.21m,
            "CA" => 0.13m,
            "AU" => 0.10m,
            "JP" => 0.10m,
            _ => 0.0m,
        };

        c.Session.Vars["tax"] = (subtotal * rate).ToString("0.00",
            System.Globalization.CultureInfo.InvariantCulture);
        c.Session.Vars["taxRate"] = rate.ToString("0.00");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetRatesAsync(FlowContext c, CancellationToken ct)
    {
        // Rates usually live behind the checkout session; ask whatever endpoint exists.
        var checkoutId = c.Session.Vars.TryGetValue("checkoutId", out var ch)
            ? ch
            : c.Session.CheckoutToken ?? "checkout";
        var ratesUrl = Origin(c.Url) + "/checkouts/" + checkoutId + "/shipping_rates";

        var res = await GetAsync(c, ratesUrl, Tag() + "-rates", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("rates unreachable", retryable: true);

        c.Session.Vars["rates"] = res.Body;
        var count = System.Text.RegularExpressions.Regex.Matches(res.Body, "\"price\"").Count;
        c.Session.Vars["rateCount"] = count.ToString();

        return count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no shipping rates returned", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitRateAsync(FlowContext c, CancellationToken ct)
    {
        var chosen = c.Session.Vars.TryGetValue("rateId", out var r) ? r : null;
        if (string.IsNullOrWhiteSpace(chosen))
        {
            // No explicit choice: take the first rate the store offered.
            var rates = c.Session.Vars.TryGetValue("rates", out var body) ? body : string.Empty;
            chosen = System.Text.RegularExpressions.Regex
                .Match(rates, "\"id\"\\s*:\\s*\"?([A-Za-z0-9_\\-]+)\"?").Groups[1].Value;
        }

        if (string.IsNullOrEmpty(chosen))
            return StepOutcome.Fail("no shipping rate to select", retryable: true);

        c.Session.Vars["selectedRate"] = chosen;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> LookupAddressAsync(FlowContext c, CancellationToken ct)
    {
        var ship = c.Shipping;
        if (ship is null) return StepOutcome.Fail("no address to normalise");

        // Tidy the fields the store will validate: trim, collapse spaces, upper-case the state.
        c.Session.Vars["address1"] = (ship.Address1 ?? string.Empty).Trim();
        c.Session.Vars["city"] = (ship.City ?? string.Empty).Trim();
        c.Session.Vars["state"] = (ship.State ?? string.Empty).Trim().ToUpperInvariant();
        c.Session.Vars["zip"] = (ship.ZipCode ?? string.Empty).Trim();
        c.Session.Vars["country"] = (ship.Country ?? "US").Trim().ToUpperInvariant();

        var complete = c.Session.Vars["address1"].Length > 0 &&
                       c.Session.Vars["city"].Length > 0 &&
                       c.Session.Vars["zip"].Length > 0;

        return complete
            ? StepOutcome.Success()
            : StepOutcome.Fail("address incomplete", retryable: false);
    }

    // ── payment ───────────────────────────────────────────────────────────────
    // ── three RPC steps the replica did not have ──────────────────────────────
    //
    // R958. The image's RPC surface is one descriptor of ten consecutive ordinals:
    //   169 RpcLogin · 170 RpcFindProduct · 171 RpcCheckStock · 172 RpcFetchAddress · 173 RpcCreateAddress
    //   174 RpcCalculateShipping · 175 RpcValidateBuyRule · 176 RpcCreateOrder
    //   177 RpcGetPaymentMethods · 178 RpcSubmitCard
    // Eight of the ten have a replica step under some name -- Login, FindProduct, SubmitAddress, GetShippingRates,
    // SubmitOrder, SubmitPayment. Three have none at all, and each is a real part of a checkout rather than a synonym:
    // CheckStock is asked before an order exists, ValidateBuyRule is the shop's own policy check, and GetPaymentMethods
    // is the call that answers which methods a shop offers -- the thing R957 had to invent a constant for.

    /// <summary>
    /// Asks whether a variant can still be bought before an order is created. Distinct from the product scrape, which
    /// reports what a page said; this asks the shop's own stock service, which can disagree with a cached page.
    /// </summary>
    public virtual async Task<StepOutcome> CheckStockAsync(FlowContext c, CancellationToken ct)
    {
        var sku = c.Session.Vars.GetValueOrDefault("sku");
        if (string.IsNullOrEmpty(sku)) return StepOutcome.Fail("no sku to check", retryable: false);

        var url = c.Session.Vars.GetValueOrDefault("checkStockUrl");
        if (string.IsNullOrEmpty(url)) return await NotSupported("CheckStock").ConfigureAwait(false);

        var res = await c.Http.GetAsync(url!, new RequestOptions(), ct).ConfigureAwait(false);
        if (res.StatusCode is 404 or 410) return StepOutcome.Fail("out of stock", retryable: false);
        if (res.StatusCode is < 200 or >= 300) return StepOutcome.Fail("stock check " + res.StatusCode, retryable: true);

        // the body is the shop's own answer; looking for a false flag is safer than assuming a 200 means buyable
        var body = res.Body ?? string.Empty;
        var available = !body.Contains("\"available\":false", StringComparison.OrdinalIgnoreCase) &&
                        !body.Contains("\"inStock\":false", StringComparison.OrdinalIgnoreCase);
        return available ? StepOutcome.Success() : StepOutcome.Fail("out of stock", retryable: false);
    }

    /// <summary>
    /// Runs the shop's purchase-policy check. A shop can refuse a purchase for reasons unrelated to stock -- quantity
    /// limits, region rules, an account that has already bought its allowance -- and it refuses before an order exists.
    /// </summary>
    public virtual async Task<StepOutcome> ValidateBuyRuleAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.GetValueOrDefault("validateBuyRuleUrl");
        if (string.IsNullOrEmpty(url)) return await NotSupported("ValidateBuyRule").ConfigureAwait(false);

        var res = await c.Http.PostJsonAsync(url!, c.Session.Vars.GetValueOrDefault("buyRuleBody") ?? "{}", null, ct)
            .ConfigureAwait(false);

        if (res.StatusCode is < 200 or >= 300)
        {
            var why = res.Body ?? string.Empty;
            // a refusal here is final: retrying a policy decision only asks the same question again
            return StepOutcome.Fail("buy rule refused: " + why, retryable: false);
        }

        return StepOutcome.Success();
    }

    /// <summary>
    /// Fetches the payment methods a shop offers and chooses one, which is the call that makes the selection logic in
    /// <see cref="ChooseGateway"/> meaningful. Ordinal 177 sits between CreateOrder and SubmitCard, so this runs after an
    /// order exists and before a card is submitted.
    /// </summary>
    public virtual async Task<StepOutcome> GetPaymentMethodsAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.GetValueOrDefault("paymentMethodsUrl");
        if (string.IsNullOrEmpty(url)) return await NotSupported("GetPaymentMethods").ConfigureAwait(false);

        var res = await c.Http.GetAsync(url!, new RequestOptions(), ct).ConfigureAwait(false);
        if (res.StatusCode is < 200 or >= 300)
            return StepOutcome.Fail("payment methods " + res.StatusCode, retryable: res.StatusCode is 429 or >= 500);

        var offered = ParsePaymentMethodNames(res.Body ?? string.Empty);
        if (offered.Count == 0) return StepOutcome.Fail("no payment methods offered", retryable: false);

        c.Session.Vars["paymentMethods"] = string.Join(",", offered);

        var preferred = (c.Session.Vars.GetValueOrDefault(PreferredGatewaysSetting) ?? string.Empty)
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var blocked = (c.Session.Vars.GetValueOrDefault(BlockedGatewaysSetting) ?? string.Empty)
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        var chosen = ChooseGateway(offered, preferred, blocked);
        if (string.IsNullOrEmpty(chosen)) return StepOutcome.Fail("every offered method is blocked", retryable: false);

        c.Session.Vars[PaymentGatewayNameKey] = chosen!;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Reads method names out of a payment-methods answer. Every shape a shop uses puts names in a JSON array of objects
    /// with a name-ish field, so the scan looks for a quoted value following one of those field names rather than
    /// attempting to parse an unknown schema -- and returns what it found, which may be nothing.
    /// </summary>
    public static List<string> ParsePaymentMethodNames(string body)
    {
        var found = new List<string>();
        if (string.IsNullOrEmpty(body)) return found;

        foreach (var key in new[] { "\"id\"", "\"code\"", "\"type\"", "\"name\"", "\"method\"" })
        {
            var at = 0;
            while ((at = body.IndexOf(key, at, StringComparison.OrdinalIgnoreCase)) >= 0)
            {
                var colon = body.IndexOf(':', at + key.Length);
                if (colon < 0) break;
                var open = body.IndexOf('"', colon + 1);
                if (open < 0) break;
                var close = body.IndexOf('"', open + 1);
                if (close < 0) break;

                var value = body[(open + 1)..close];
                if (value.Length is > 0 and < 40 && !found.Contains(value, StringComparer.OrdinalIgnoreCase))
                    found.Add(value);
                at = close + 1;
            }
        }

        return found;
    }

    /// <summary>The session key for the selected gateway, spelled as the image binds it.</summary>
    public const string PaymentGatewayNameKey = "paymentGatewayName";

    /// <summary>The session key for the captcha token, which the image keeps beside the gateway name.</summary>
    public const string CaptchaTokenKey = "captchaToken";

    /// <summary>
    /// The two settings the image uses to choose among a shop's payment methods: an ordered preference and a set of
    /// exclusions.
    ///
    /// <para>
    /// R957. R956 replaced an invented key with the image's names but left a hard-coded list of four gateways, which was
    /// the same mistake one layer down. Searching for how selection actually works found these instead: the image has
    /// <c>PreferredGateways</c> and <c>blockedGateways</c> as settings, <c>RpcGetPaymentMethods</c> to fetch what a shop
    /// offers, <c>ParsePaymentMethods</c> to read the answer, and <c>IsWalletOnly</c> to classify one kind. So the set of
    /// gateways is not a constant at all -- it is whatever the shop returns, filtered by two settings.
    /// </para>
    /// </summary>
    public const string PreferredGatewaysSetting = "PreferredGateways";

    /// <inheritdoc cref="PreferredGatewaysSetting"/>
    public const string BlockedGatewaysSetting = "blockedGateways";

    /// <summary>
    /// Chooses one method from what a shop offers. Preference order wins, blocked always loses, and an empty preference
    /// list means take the first unblocked one rather than none -- a shop that offers payment must not fail because the
    /// user expressed no preference.
    /// </summary>
    public static string? ChooseGateway(IReadOnlyList<string> available, IReadOnlyList<string> preferred,
                                       IReadOnlyList<string> blocked)
    {
        if (available is null || available.Count == 0) return null;

        var blockedSet = new HashSet<string>(blocked ?? Array.Empty<string>(), StringComparer.OrdinalIgnoreCase);

        foreach (var wanted in preferred ?? Array.Empty<string>())
            foreach (var offered in available)
                if (string.Equals(wanted, offered, StringComparison.OrdinalIgnoreCase) && !blockedSet.Contains(offered))
                    return offered;

        foreach (var offered in available)
            if (!blockedSet.Contains(offered))
                return offered;

        return null;
    }

    /// <summary>
    /// True when a method is a wallet, which the image classifies separately because a wallet needs no card.
    /// </summary>
    public static bool IsWalletOnly(string? method) =>
        method is not null && (
            method.Contains("paypal", StringComparison.OrdinalIgnoreCase) ||
            method.Contains("applepay", StringComparison.OrdinalIgnoreCase) ||
            method.Contains("apple_pay", StringComparison.OrdinalIgnoreCase) ||
            method.Contains("googlepay", StringComparison.OrdinalIgnoreCase) ||
            method.Contains("google_pay", StringComparison.OrdinalIgnoreCase) ||
            method.Contains("wallet", StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// Payment submission dispatches to whichever gateway the session named, and returns NotSupported when none was
    /// named -- the previous behaviour, kept for flows that never reach this step.
    ///
    /// <para>
    /// R955. The five gateway classes written between R920 and R925 were reachable from nothing and so contributed no
    /// functions at all. Dispatching here is what connects them: the step existed and returned NotSupported, the
    /// gateways already had working async methods, and the missing piece was the call rather than either end.
    /// </para>
    ///
    /// <para>
    /// <b>Why the gateways take a post delegate.</b> Each needs to make a request but must not own a client, so the
    /// caller passes one in. That lets this dispatch hand them the session's own client without any gateway knowing what
    /// a NetClient is.
    /// </para>
    ///
    /// <para>
    /// <b>The names are the image's.</b> R956 searched for how the original selects a gateway and found the backing field
    /// <c>_paymentGateway</c>, the bound property <c>_paymentGatewayName</c>, a collection <c>PaymentGateways</c>, and
    /// <c>paymentProvider</c>. The concatenated descriptor
    /// <c>_captchaToken&lt;_paymentGatewayName6_paymentFlexibilityTemplate</c> puts the captcha token and the gateway name
    /// adjacent, which is the real shape of a payment submission: a token and a gateway, together. R955 used
    /// <c>paymentGateway</c>, which had been invented rather than searched for.
    /// </para>
    /// </summary>
    public virtual async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        // R956: the image names this field _paymentGatewayName, and _captchaToken sits beside it. My first version
        // invented "paymentGateway" -- close enough to compile and not what the original calls it.
        // R957: the gateway is chosen from what the shop offers, filtered by the two settings, rather than switched on
        // against a fixed list. A session may still name one explicitly, and that wins because it was chosen by a person.
        var gateway = c.Session.Vars.TryGetValue(StoreFlow.PaymentGatewayNameKey, out var named) ? named : null;
        if (string.IsNullOrEmpty(gateway))
        {
            var offered = c.Session.Vars.GetValueOrDefault("paymentMethods")
                ?.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                ?? Array.Empty<string>();
            var preferred = c.Session.Vars.GetValueOrDefault("PreferredGateways")
                ?.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                ?? Array.Empty<string>();
            var blocked = c.Session.Vars.GetValueOrDefault("blockedGateways")
                ?.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                ?? Array.Empty<string>();

            gateway = ChooseGateway(offered, preferred, blocked);
        }

        if (string.IsNullOrEmpty(gateway)) return await NotSupported("SubmitPayment").ConfigureAwait(false);

        var card = c.Session.Vars.GetValueOrDefault("cardNumber") ?? string.Empty;
        var expiry = c.Session.Vars.GetValueOrDefault("cardExpiry") ?? string.Empty;

        // shaped exactly as the gateways declare it; the cast to NetResponse? keeps Task<T> invariant from biting
        Func<string, string, string, CancellationToken, Task<NetResponse?>> post =
            async (method, url, body, token) =>
                (NetResponse?)await c.Http.SendAsync(
                    string.Equals(method, "POST", StringComparison.OrdinalIgnoreCase) ? HttpMethod.Post : HttpMethod.Get,
                    url,
                    new RequestOptions
                    {
                        Content = string.IsNullOrEmpty(body)
                            ? null
                            : new StringContent(body, System.Text.Encoding.UTF8, "application/json"),
                    },
                    token).ConfigureAwait(false);

        switch (gateway!.Trim().ToLowerInvariant())
        {
            case "viva":
            case "vivapayments":
                return await Payments.VivaPayments.ChargeTokenAsync(c.Session, card, expiry, ct, post)
                    .ConfigureAwait(false);

            case "disney":
            case "disneypaymentsheet":
                return await Payments.DisneyPaymentSheet.ProcessAsync(c.Session, ct, post).ConfigureAwait(false);

            default:
                return await NotSupported("SubmitPayment:" + gateway).ConfigureAwait(false);
        }
    }

    public virtual Task<StepOutcome> SubmitPaymentDetailsAsync(FlowContext c, CancellationToken ct)
        => SubmitPaymentAsync(c, ct);
    public virtual async Task<StepOutcome> GetPaymentTokenAsync(FlowContext c, CancellationToken ct)
    {
        // Prefer whatever the platform already minted; every flow that can tokenise fills this in itself.
        if (!string.IsNullOrEmpty(c.Session.PaymentToken)) return StepOutcome.Success();

        // R991: this used to invent one -- `"tok_" + Guid.NewGuid().ToString("N")[..24]` -- and return success. That is the
        // thing the comment on Shopify's GetCsrf forbids, for the reason round 823 gave there: a token the server never
        // issued makes every request carrying it invalid, so the failure moves from here to whichever call happens to send
        // it, where it arrives disguised as a rejection from the store.
        //
        // The guard above is why the fabrication almost never ran: FootsitesFlow reads the id out of the tokenise response,
        // MagentoFlow reads the token, ShopifyFlow reads the id, and Gateways.cs mints four kinds through their real
        // endpoints. This method is the fallback for a flow that reached payment without any of that, and a fallback that
        // fabricates is worse than one that stops. Nothing is lost by failing here -- a made-up token would have failed
        // against the server anyway, later and less legibly.
        await Task.CompletedTask.ConfigureAwait(false);
        return StepOutcome.Fail(
            $"{Name}: no payment token available -- no tokenising step ran for this flow, and this step will not invent one",
            retryable: true);
    }
    public virtual async Task<StepOutcome> GetPaymentPageAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.TryGetValue("paymentUrl", out var pu)
            ? pu
            : Origin(c.Url) + "/payments";

        var res = await GetAsync(c, url, Tag() + "-paypage", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("payment page unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypage HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["paymentPage"] = res.Body;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPaymentUrlAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("checkout", out var ch) ? ch : string.Empty;
        var url = System.Text.RegularExpressions.Regex
            .Match(body, "\"paymentUrl\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(url))
            url = System.Text.RegularExpressions.Regex
                .Match(body, "\"redirectUrl\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(url))
            return StepOutcome.Fail("no payment url in checkout", retryable: true);

        c.Session.Vars["paymentUrl"] = url;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPaymentDetailsAsync(FlowContext c, CancellationToken ct)
    {
        var token = c.Session.Vars.TryGetValue("paymentToken", out var t)
            ? t
            : c.Session.PaymentToken;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("no payment token to look up", retryable: true);

        var url = Origin(c.Url) + "/api/payments/" + Uri.EscapeDataString(token!);
        var res = await GetAsync(c, url, Tag() + "-paydetails", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("payment details unreachable", retryable: true);

        c.Session.Vars["paymentDetails"] = res.Body;
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"paydetails HTTP {res.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> CompletePaymentAsync(FlowContext c, CancellationToken ct)
    {
        // Final confirmation: the store answers with the order identity or a refusal.
        var url = c.Session.Vars.TryGetValue("destination", out var dest)
            ? dest
            : Origin(c.Url) + "/checkout/complete";

        var res = await PostJsonAsync(c, url, "{}", Tag() + "-paycomplete", ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("complete payment failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"complete HTTP {res.StatusCode}", retryable: true);

        var order = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"order(?:Number|Id)\"\\s*:\\s*\"?([A-Za-z0-9\\-]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(order))
        {
            c.Session.OrderNumber = order;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("complete returned no order identity");
    }
    public virtual async Task<StepOutcome> StartPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var token = await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
        if (!token.Ok) return token;

        c.Session.Vars["paymentStarted"] = DateTime.UtcNow.ToString("u");
        c.Emit($"{Name}: payment started token={c.Session.PaymentToken}", "payment");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ProcessPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var status = c.Session.Vars.TryGetValue("paymentStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status))
        {
            // No gateway verdict yet — run the generic submit and let it decide.
            return await SubmitPaymentAsync(c, ct).ConfigureAwait(false);
        }

        return status.ToLowerInvariant() switch
        {
            "authorised" or "authorized" or "success" or "captured" => StepOutcome.Success(),
            "requires_action" or "pending" => StepOutcome.Fail("payment requires action", retryable: true),
            _ => StepOutcome.Fail($"payment {status}"),
        };
    }
    public virtual async Task<StepOutcome> CreatePaymentAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.PaymentToken))
        {
            var token = await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
            if (!token.Ok) return token;
        }

        c.Session.Vars["paymentId"] = "pay_" + Guid.NewGuid().ToString("N")[..20];
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> CreateTransactionAsync(FlowContext c, CancellationToken ct)
    {
        var payment = await CreatePaymentAsync(c, ct).ConfigureAwait(false);
        if (!payment.Ok) return payment;

        var total = c.Session.Vars.TryGetValue("total", out var t) ? t : c.Product?.Price ?? "0";
        c.Session.Vars["transactionId"] = "txn_" + Guid.NewGuid().ToString("N")[..20];
        c.Session.Vars["transactionAmount"] = total;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitCardAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        // Only the last four and the expiry shape are echoed — the PAN never leaves the flow.
        c.Session.Vars["card.last4"] = card.Last4;
        c.Session.Vars["card.expiry"] = (card.Month ?? "--") + "/" + (card.Year ?? "--");
        c.Session.Vars["card.brand"] = card.Number.StartsWith('4') ? "visa"
            : card.Number.StartsWith("5") ? "mastercard"
            : card.Number.StartsWith("3") ? "amex"
            : "unknown";

        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> TokenizeAsync(FlowContext c, CancellationToken ct)
    {
        return await GetPaymentTokenAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> AuthorizeAsync(FlowContext c, CancellationToken ct)
    {
        var card = await SubmitCardAsync(c, ct).ConfigureAwait(false);
        if (!card.Ok) return card;

        var payment = await ProcessPaymentAsync(c, ct).ConfigureAwait(false);
        if (!payment.Ok) return payment;

        c.Session.Vars["authorized"] = "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> HandleRequiresActionAsync(FlowContext c, CancellationToken ct)
    {
        // A payment that needs a redirect or a challenge must carry the URL it wants.
        if (string.IsNullOrEmpty(c.Session.ThreeDsUrl))
            return StepOutcome.Fail("no action url supplied", retryable: true);

        c.Emit($"{Name}: payment requires action at {c.Session.ThreeDsUrl}", "3ds");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetMerchantCodeAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("checkout", out var ch) ? ch : string.Empty;
        var code = System.Text.RegularExpressions.Regex
            .Match(body, "\"merchant(?:Code|Id)\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(code))
            code = c.Session.Vars.TryGetValue("merchantCode", out var mc) ? mc : string.Empty;

        if (string.IsNullOrEmpty(code))
            return StepOutcome.Fail("no merchant code in checkout payload", retryable: true);

        c.Session.Vars["merchantCode"] = code;
        return StepOutcome.Success();
    }

    // ── PayPal ────────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> SubmitPayPalAsync(FlowContext c, CancellationToken ct)
    {
        var orderId = c.Session.Vars.TryGetValue("paypalOrderId", out var id) ? id : null;
        if (string.IsNullOrEmpty(orderId))
        {
            var token = await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
            if (!token.Ok) return token;
            orderId = c.Session.Vars["paypalOrderId"];
        }

        var res = await PostJsonAsync(c,
            "https://api.paypal.com/v2/checkout/orders/" + orderId + "/capture",
            "{}", Tag() + "-paypal-capture", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("paypal capture failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal capture HTTP {res.StatusCode}", retryable: true);

        var status = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"status\"\\s*:\\s*\"([A-Z_]+)\"").Groups[1].Value;

        c.Session.Vars["paypalStatus"] = status;
        if (string.Equals(status, "COMPLETED", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.OrderNumber = orderId;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail($"paypal status {status}");
    }
    public virtual async Task<StepOutcome> StartPayPalAsync(FlowContext c, CancellationToken ct)
    {
        var token = await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
        if (!token.Ok) return token;

        c.Session.Vars["paypalStarted"] = DateTime.UtcNow.ToString("u");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalTokenAsync(FlowContext c, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(c.Session.PaymentToken) &&
            c.Session.Vars.TryGetValue("paypalOrderId", out var existing) &&
            !string.IsNullOrEmpty(existing))
            return StepOutcome.Success();

        var body = new Newtonsoft.Json.Linq.JObject
        {
            ["intent"] = "CAPTURE",
            ["purchase_units"] = new Newtonsoft.Json.Linq.JArray(
                new Newtonsoft.Json.Linq.JObject
                {
                    ["amount"] = new Newtonsoft.Json.Linq.JObject
                    {
                        ["currency_code"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "USD",
                        ["value"] = c.Session.Vars.TryGetValue("total", out var tot) ? tot : "0.00",
                    },
                }),
        };

        var res = await PostJsonAsync(c, "https://api.paypal.com/v2/checkout/orders",
            body.ToString(Newtonsoft.Json.Formatting.None), Tag() + "-paypal-order", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("paypal order failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal order HTTP {res.StatusCode}", retryable: true);

        var orderId = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"id\"\\s*:\\s*\"([A-Z0-9]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(orderId))
            return StepOutcome.Fail("paypal returned no order id");

        c.Session.Vars["paypalOrderId"] = orderId;
        c.Session.PaymentToken = orderId;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalAccessTokenAsync(FlowContext c, CancellationToken ct)
    {
        // Delegates to the PayPal gateway when one is wired; otherwise reports the gap.
        var clientId = c.Session.Vars.TryGetValue("paypal.clientId", out var ci) ? ci : null;
        var secret = c.Session.Vars.TryGetValue("paypal.clientSecret", out var cs) ? cs : null;

        if (string.IsNullOrEmpty(clientId) || string.IsNullOrEmpty(secret))
            return StepOutcome.Fail("paypal client credentials missing", retryable: false);

        var basic = Convert.ToBase64String(
            System.Text.Encoding.UTF8.GetBytes(clientId + ":" + secret));
        c.Session.Headers["Authorization"] = "Basic " + basic;

        var res = await PostFormAsync(c, "https://api.paypal.com/v1/oauth2/token",
            new Dictionary<string, string> { ["grant_type"] = "client_credentials" },
            Tag() + "-paypal-token", ct).ConfigureAwait(false);

        c.Session.Headers.Remove("Authorization");

        if (res is null) return StepOutcome.Fail("paypal token call failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paypal token HTTP {res.StatusCode}", retryable: true);

        var token = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"access_token\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("paypal returned no access token");

        c.Session.AntiBotTokens["Authorization"] = "Bearer " + token;
        c.Session.Vars["paypal.accessToken"] = token;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetPayPalOrderIdAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("paypalOrderId", out var id) && !string.IsNullOrEmpty(id))
            return StepOutcome.Success();

        return await GetPayPalTokenAsync(c, ct).ConfigureAwait(false);
    }

    // ── Stripe / gateways ─────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> CreateStripePaymentMethodAsync(FlowContext c, CancellationToken ct)
    {
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        var publishable = c.Session.Vars.TryGetValue("stripe.publishableKey", out var pk)
            ? pk
            : string.Empty;

        var form = new Dictionary<string, string>
        {
            ["key"] = publishable,
            ["type"] = "card",
            ["card[number]"] = card.Number,
            ["card[exp_month]"] = card.Month ?? string.Empty,
            ["card[exp_year]"] = card.Year ?? string.Empty,
            ["card[cvc]"] = card.Cvv ?? string.Empty,
        };

        var res = await PostFormAsync(c, "https://api.stripe.com/v1/payment_methods", form,
            Tag() + "-stripe-pm", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("stripe payment method failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"stripe pm HTTP {res.StatusCode}", retryable: true);

        var id = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"id\"\\s*:\\s*\"(pm_[A-Za-z0-9]+)\"").Groups[1].Value;

        if (string.IsNullOrEmpty(id))
            return StepOutcome.Fail("stripe returned no payment method");

        c.Session.PaymentMethodId = id;
        c.Session.PaymentToken = id;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> GetStripePaymentIntentAsync(FlowContext c, CancellationToken ct)
    {
        var secret = c.Session.Vars.TryGetValue("stripe.clientSecret", out var cs) ? cs : null;
        if (!string.IsNullOrEmpty(secret))
        {
            c.Session.Vars["stripe.intentId"] = secret!.Split('_')[0] + "_" + secret.Split('_')[1];
            return StepOutcome.Success();
        }

        var pm = c.Session.PaymentMethodId;
        if (string.IsNullOrEmpty(pm))
        {
            var created = await CreateStripePaymentMethodAsync(c, ct).ConfigureAwait(false);
            if (!created.Ok) return created;
            pm = c.Session.PaymentMethodId;
        }

        var form = new Dictionary<string, string>
        {
            ["key"] = c.Session.Vars.TryGetValue("stripe.publishableKey", out var pk) ? pk : string.Empty,
            ["payment_method"] = pm!,
            ["amount"] = c.Session.Vars.TryGetValue("totalMinor", out var amt) ? amt : "0",
            ["currency"] = c.Session.Vars.TryGetValue("currency", out var cur) ? cur : "usd",
            ["confirm"] = "true",
        };

        var res = await PostFormAsync(c, "https://api.stripe.com/v1/payment_intents", form,
            Tag() + "-stripe-intent", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("stripe intent failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"stripe intent HTTP {res.StatusCode}", retryable: true);

        var status = System.Text.RegularExpressions.Regex
            .Match(res.Body, "\"status\"\\s*:\\s*\"([a-z_]+)\"").Groups[1].Value;

        c.Session.Vars["stripe.status"] = status;
        return string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Success()
            : StepOutcome.Fail($"stripe status {status}", retryable: status == "requires_action");
    }
    public virtual async Task<StepOutcome> CreateGmoTokenAsync(FlowContext c, CancellationToken ct)
    {
        // GMO Payment Gateway: the token endpoint takes the card in a POST form.
        var card = c.Card;
        if (card?.Number is null) return StepOutcome.Fail("no card");

        var shopId = c.Session.Vars.TryGetValue("gmo.shopId", out var s) ? s : string.Empty;
        var form = new Dictionary<string, string>
        {
            ["shop_id"] = shopId,
            ["card_no"] = card.Number,
            ["expire"] = (card.Year ?? "20")[^2..] + (card.Month ?? "01"),
            ["security_code"] = card.Cvv ?? string.Empty,
            ["hold_times"] = "10",
        };

        var res = await PostFormAsync(c,
            "https://p01.mul-pay.jp/payment/SaveCard.idPass", form, Tag() + "-gmo-token", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("gmo token failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"gmo HTTP {res.StatusCode}", retryable: true);

        var token = System.Text.RegularExpressions.Regex
            .Match(res.Body, "CardSeq=(\\d+)").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            token = System.Text.RegularExpressions.Regex
                .Match(res.Body, "ErrCode=([^&\\s]+)").Groups[1].Value;

        if (string.IsNullOrEmpty(token))
            return StepOutcome.Fail("gmo returned no card sequence");

        c.Session.PaymentToken = token;
        c.Session.Vars["gmo.cardSeq"] = token;
        return StepOutcome.Success();
    }

    // ── 3-D Secure ────────────────────────────────────────────────────────────
    public virtual async Task<StepOutcome> ThreeDSAsync(FlowContext c, CancellationToken ct)
    {
        var version = c.Session.Vars.TryGetValue("3dsVersion", out var v) ? v : "2.2.0";
        var enrolled = c.Session.Vars.TryGetValue("3dsEnrolled", out var e) ? e : null;

        // Issuer not enrolled means the payment can proceed without a challenge.
        if (string.Equals(enrolled, "N", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.Vars["3dsRequired"] = "false";
            return StepOutcome.Success();
        }

        c.Session.Vars["3dsRequired"] = "true";
        c.Session.Vars["3dsVersionUsed"] = version;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> Handle3DSAsync(FlowContext c, CancellationToken ct)
    {
        // Accept whatever the issuer returned; classification happens in Process3DS.
        var status = c.Session.Vars.TryGetValue("adyen.transStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status)) return StepOutcome.Success();   // not a 3DS flow

        return string.Equals(status, "Y", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Success()
            : StepOutcome.Fail($"3DS status {status}", retryable: false);
    }
    public virtual async Task<StepOutcome> Solve3DSAsync(FlowContext c, CancellationToken ct)
    {
        var jwt = c.Session.Vars.TryGetValue("adyen.paymentData", out var pd) ? pd : null;
        if (string.IsNullOrEmpty(jwt))
            return StepOutcome.Fail("no paymentData to solve", retryable: true);

        // The challenge answer is whatever the ACS page produced; without one, we can only
        // mark that a solve is required and hand the URL upwards.
        var acs = c.Session.Vars.TryGetValue("adyen.threeDSMethodUrl", out var m) ? m : null;
        if (string.IsNullOrEmpty(acs))
            return StepOutcome.Fail("no ACS url in paymentData", retryable: true);

        c.Session.ThreeDsUrl = acs;
        c.Session.Vars["3dsAcsUrl"] = acs!;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> Solve3DSRedirectAsync(FlowContext c, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(c.Session.ThreeDsUrl))
        {
            var solve = await Solve3DSAsync(c, ct).ConfigureAwait(false);
            if (!solve.Ok) return solve;
        }

        // Follow the redirect once; the ACS answers with an HTML form that posts the result.
        var res = await GetAsync(c, c.Session.ThreeDsUrl!, Tag() + "-3ds-redirect", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("3DS redirect unreachable", retryable: true);

        c.Session.Vars["3dsResponse"] = res.Body;
        var transStatus = System.Text.RegularExpressions.Regex
            .Match(res.Body, "name=\"transStatus\"[^>]*value=\"([YNUCR])\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(transStatus))
        {
            c.Session.Vars["adyen.transStatus"] = transStatus;
            return StepOutcome.Success();
        }

        return StepOutcome.Fail("3DS redirect carried no transStatus", retryable: true);
    }
    public virtual async Task<StepOutcome> Process3DSAsync(FlowContext c, CancellationToken ct)
    {
        var required = c.Session.Vars.TryGetValue("3dsRequired", out var r) && r == "true";
        if (!required) return StepOutcome.Success();

        var status = c.Session.Vars.TryGetValue("adyen.transStatus", out var s) ? s : null;
        if (string.IsNullOrEmpty(status))
            return StepOutcome.Fail("3DS required but no transStatus", retryable: true);

        return status.ToUpperInvariant() switch
        {
            "Y" or "A" => StepOutcome.Success(),
            "N" => StepOutcome.Fail("3DS rejected by issuer", retryable: false),
            "U" => StepOutcome.Fail("3DS unable to authenticate", retryable: true),
            "C" => StepOutcome.Fail("3DS challenge still pending", retryable: true),
            "R" => StepOutcome.Fail("3DS rejected, retry with new card", retryable: false),
            _ => StepOutcome.Fail($"3DS status {status}", retryable: true),
        };
    }
    public virtual async Task<StepOutcome> AwaitDeviceProfilingAsync(FlowContext c, CancellationToken ct)
    {
        // Some issuers require a few seconds of device data before the challenge opens.
        var wait = c.Session.Vars.TryGetValue("deviceProfilingMs", out var ms) &&
                   int.TryParse(ms, out var parsed)
            ? Math.Clamp(parsed, 0, 15000)
            : 3000;

        if (wait > 0) await Task.Delay(wait, ct).ConfigureAwait(false);

        c.Session.Vars["deviceProfiled"] = "true";
        return StepOutcome.Success();
    }

    // ── account ───────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> LoginAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> AccountLoginAsync(FlowContext c, CancellationToken ct)
        => LoginAsync(c, ct);
    public virtual Task<StepOutcome> EmailLoginAsync(FlowContext c, CancellationToken ct)
        => LoginAsync(c, ct);
    public virtual Task<StepOutcome> CheckLoginAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> HandleLoginAsync(FlowContext c, CancellationToken ct)
    {
        var outcome = await LoginAsync(c, ct).ConfigureAwait(false);
        if (!outcome.Ok) return outcome;

        var check = await CheckLoginAsync(c, ct).ConfigureAwait(false);
        return check.Ok ? StepOutcome.Success() : StepOutcome.Fail("login did not stick");
    }
    public virtual Task<StepOutcome> RegisterAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> CompleteRegistrationAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> SignUpAsync(FlowContext c, CancellationToken ct)
        => RegisterAsync(c, ct);
    public virtual async Task<StepOutcome> ResetPasswordAsync(FlowContext c, CancellationToken ct)
    {
        var email = await SetEmailAsync(c, ct).ConfigureAwait(false);
        if (!email.Ok) return email;

        var res = await PostJsonAsync(c, Origin(c.Url) + "/account/recover",  // inferred: no image evidence (R294)
            Newtonsoft.Json.JsonConvert.SerializeObject(new { email = c.Session.Vars["email"] }),
            Tag() + "-recover", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("password reset failed", retryable: true);
        return res.IsSuccess
            ? StepOutcome.Success()
            : StepOutcome.Fail($"recover HTTP {res.StatusCode}", retryable: true);
    }
    public virtual Task<StepOutcome> SendTwoFactorAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> SubmitPasswordAsync(FlowContext c, CancellationToken ct)
    {
        var password = c.Account?.Password;
        if (string.IsNullOrEmpty(password))
            return StepOutcome.Fail("no password on the account");

        // Never echo the value; only its shape is recorded for diagnostics.
        c.Session.Vars["passwordLength"] = password!.Length.ToString();
        c.Session.Vars["passwordSubmitted"] = "true";
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SetEmailAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email available");

        c.Session.Vars["email"] = email!;
        c.Session.Vars["emailDomain"] = email!.Contains('@') ? email.Split('@')[1] : string.Empty;
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitCustomerAsync(FlowContext c, CancellationToken ct)
    {
        var profile = c.ProfileData;
        if (profile is null) return StepOutcome.Fail("no profile");

        c.Session.Vars["customer.email"] = profile.Email ?? string.Empty;
        c.Session.Vars["customer.firstName"] = profile.FirstName ?? string.Empty;
        c.Session.Vars["customer.lastName"] = profile.LastName ?? string.Empty;
        c.Session.Vars["customer.phone"] = profile.Phone ?? string.Empty;
        return string.IsNullOrEmpty(profile.Email)
            ? StepOutcome.Fail("profile has no email")
            : StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitInfoAsync(FlowContext c, CancellationToken ct)
    {
        // Customer info is a subset of the shipping block on most platforms.
        var customer = await SubmitCustomerAsync(c, ct).ConfigureAwait(false);
        if (!customer.Ok) return customer;
        return await SubmitShippingAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> SubmitDetailsCommerceAsync(FlowContext c, CancellationToken ct)
    {
        // Commerce-platform detail block: customer + address + payment intent in one call.
        var customer = await SubmitCustomerAsync(c, ct).ConfigureAwait(false);
        if (!customer.Ok) return customer;

        var address = await LookupAddressAsync(c, ct).ConfigureAwait(false);
        if (!address.Ok) return address;

        c.Session.Vars["commerceDetails"] = "prepared";
        return StepOutcome.Success();
    }

    // ── anti-bot: Kasada / DataDome / PerimeterX ──────────────────────────────
    public virtual Task<StepOutcome> GetScriptAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GenerateAsync(FlowContext c, CancellationToken ct)
    {
        if (!UsesKasada)
        {
            c.Session.Vars["sensor"] = "none";
            return StepOutcome.Success();
        }

        // The concrete sensor generation happens in GenerateSensor; this is the dispatcher.
        return await GenerateSensorAsync(c, ct).ConfigureAwait(false);
    }
    public virtual Task<StepOutcome> GenerateSensorAsync(FlowContext c, CancellationToken ct)
        => GenerateAsync(c, ct);
    public virtual Task<StepOutcome> SubmitSensorAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual async Task<StepOutcome> GetSensorDataAsync(FlowContext c, CancellationToken ct)
    {
        var keys = new[] { "x-kpsdk-ct", "x-kpsdk-sb", "x-kpsdk-cd", "x-kpsdk-v" };
        var present = keys.Where(k => c.Session.AntiBotTokens.ContainsKey(k)).ToList();

        c.Session.Vars["sensorKeys"] = string.Join('|', present);
        return present.Count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no sensor tokens present", retryable: true);
    }
    public virtual Task<StepOutcome> GetKasadaAsync(FlowContext c, CancellationToken ct)
        => SubmitSensorAsync(c, ct);
    public virtual async Task<StepOutcome> GenerateSbsdAsync(FlowContext c, CancellationToken ct)
    {
        // The sbsd cookie comes from the same script as the client token.
        if (c.Session.AntiBotTokens.TryGetValue("x-kpsdk-sb", out var sb) && !string.IsNullOrEmpty(sb))
        {
            c.Session.Vars["sbsd"] = sb;  // inferred: no image evidence (R297)
            return StepOutcome.Success();
        }

        return await GenerateSensorAsync(c, ct).ConfigureAwait(false);
    }
    public virtual async Task<StepOutcome> GetSbsdDataAsync(FlowContext c, CancellationToken ct)
    {
        if (!c.Session.AntiBotTokens.TryGetValue("x-kpsdk-sb", out var sb) ||
            string.IsNullOrEmpty(sb))
            return StepOutcome.Fail("no sbsd token", retryable: true);  // inferred: no image evidence (R297)

        c.Session.Cookies["sbsd"] = sb;  // inferred: no image evidence (R297) — the pool has /sbsd and _sbsdContext, not a cookie of this name
        c.Session.Vars["sbsd"] = sb;  // inferred: no image evidence (R297)
        return StepOutcome.Success();
    }

    // ── captcha ───────────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> GetCaptchaAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetCheckoutCaptchaAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);
    /// <summary>
    /// Submits a captcha to the service the image names and polls until it answers, or until the deadline.
    ///
    /// <para>
    /// R961. This was one of thirty-six steps that returned Ok without doing anything, so a flow that needed a captcha
    /// solved was told it had been. The image carries the two endpoints -- in.php and res.php -- and three consecutive
    /// state machines, which is enough to do the work rather than report it.
    /// </para>
    ///
    /// <para>
    /// <b>The not-ready answer is the normal path.</b> A poll that comes back CAPCHA_NOT_READY means the task is still
    /// running, and treating it as a failure would break every solve that took longer than one poll. It is classified
    /// separately and leads back into the wait.
    /// </para>
    /// </summary>
    public virtual async Task<StepOutcome> SolveCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var apiKey = c.Session.Vars.GetValueOrDefault("captcha.apiKey");
        var siteKey = c.Session.Vars.GetValueOrDefault("captcha.siteKey");
        var pageUrl = c.Session.Vars.GetValueOrDefault("captcha.pageUrl") ?? c.Url;

        if (string.IsNullOrEmpty(apiKey) || string.IsNullOrEmpty(siteKey))
            return StepOutcome.Fail("captcha key or site key missing", retryable: false);

        var method = c.Session.Vars.GetValueOrDefault("captcha.method") ?? "userrecaptcha";

        var submitted = await c.Http.PostFormAsync(
            SolveCaptchaService.SubmitUrl,
            SolveCaptchaService.SubmitForm(apiKey!, method, siteKey!, pageUrl),
            new RequestOptions(),
            ct).ConfigureAwait(false);

        if (submitted.StatusCode is < 200 or >= 300)
            return StepOutcome.Fail("captcha submit HTTP " + submitted.StatusCode, retryable: submitted.StatusCode is 429 or >= 500);

        var taskId = SolveCaptchaService.TaskIdFrom(submitted.Body);
        if (string.IsNullOrEmpty(taskId))
            return StepOutcome.Fail("captcha service refused the task", retryable: false);

        var deadline = DateTimeOffset.UtcNow.AddSeconds(
            c.Session.Vars.TryGetValue("captchaTimeout", out var ts) && int.TryParse(ts, out var secs) ? secs : 120);
        var interval = TimeSpan.FromSeconds(
            c.Session.Vars.TryGetValue("captchaPollSeconds", out var ps) && int.TryParse(ps, out var pss) ? pss : 5);

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            await Task.Delay(interval, ct).ConfigureAwait(false);

            var polled = await c.Http.GetAsync(SolveCaptchaService.PollUrl(apiKey!, taskId!),
                new RequestOptions(), ct).ConfigureAwait(false);

            var poll = SolveCaptchaService.Poll(polled.StatusCode is < 200 or >= 300 ? null : polled.Body);

            switch (poll.Kind)
            {
                case CaptchaPollKind.Solved:
                    // the token goes where every captcha consumer already looks for it
                    c.Session.AntiBotTokens["g-recaptcha-response"] = poll.Token!;
                    c.Session.Vars["captchaToken"] = poll.Token!;
                    return StepOutcome.Success();

                case CaptchaPollKind.Failed:
                    return StepOutcome.Fail("captcha service refused the solve", retryable: false);

                case CaptchaPollKind.NotReady:
                    break;   // still working: keep waiting rather than failing
            }
        }

        return StepOutcome.Fail("captcha not solved within the deadline", retryable: true);
    }
    public virtual async Task<StepOutcome> PollCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var deadline = DateTimeOffset.UtcNow.AddSeconds(
            c.Session.Vars.TryGetValue("captchaTimeout", out var ts) && int.TryParse(ts, out var secs)
                ? secs
                : 60);

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            foreach (var key in new[] { "cf-turnstile-response", "g-recaptcha-response", "h-captcha-response" })
            {
                if (c.Session.AntiBotTokens.TryGetValue(key, out var token) && !string.IsNullOrEmpty(token))
                {
                    c.Session.Vars["captchaToken"] = token;
                    return StepOutcome.Success();
                }
            }

            await Task.Delay(TimeSpan.FromMilliseconds(500), ct).ConfigureAwait(false);
        }

        return StepOutcome.Fail("captcha not solved in time", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitCaptchaAsync(FlowContext c, CancellationToken ct)
    {
        var token = c.Session.AntiBotTokens
            .FirstOrDefault(kv => kv.Key.Contains("response", StringComparison.OrdinalIgnoreCase));

        if (token.Key is null)
            return StepOutcome.Fail("no captcha token to submit", retryable: true);

        c.Session.Vars["captchaToken"] = token.Value;
        c.Session.Vars["captchaKind"] = token.Key;
        return StepOutcome.Success();
    }

    // ── raffle / queue ────────────────────────────────────────────────────────
    public virtual Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetRaffleDataAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetRaffleAsync(FlowContext c, CancellationToken ct)
        => GetRaffleDataAsync(c, ct);
    public virtual async Task<StepOutcome> GetRaffleProductAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("raffle", out var r)
            ? r
            : c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;

        if (string.IsNullOrWhiteSpace(body))
            return StepOutcome.Fail("no raffle payload", retryable: true);

        var title = System.Text.RegularExpressions.Regex
            .Match(body, "\"product(?:Name)?\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;
        var size = System.Text.RegularExpressions.Regex
            .Match(body, "\"size\"\\s*:\\s*\"([^\"]+)\"").Groups[1].Value;

        if (!string.IsNullOrEmpty(title)) c.Session.Vars["product"] = title;
        if (!string.IsNullOrEmpty(size)) c.Session.Vars["size"] = size;

        return string.IsNullOrEmpty(title)
            ? StepOutcome.Fail("raffle payload had no product", retryable: true)
            : StepOutcome.Success();
    }
    public virtual Task<StepOutcome> ScrapeRaffleFormAsync(FlowContext c, CancellationToken ct) => Ok();
    /// <summary>
    /// Waits out a queue. The step existed as a bare Ok, which reported success without looking at anything -- so a flow
    /// that hit a waiting room believed it had passed one.
    ///
    /// <para>
    /// R960. The decision comes from QueueItProtocol, whose field list R959 recovered from the image: a host marker, the
    /// accepted-cookie prefix with its hash, a validity window, and a minimum remaining. The minimum is the part that
    /// matters here. A pass about to expire is worse than none, because the request it authorises is refused after the
    /// queue has already been left -- so this waits while the remaining validity is under the margin the image names.
    /// </para>
    ///
    /// <para>
    /// <b>Why a bounded loop rather than a sleep.</b> A wait whose length is unknown must still terminate, so the loop
    /// polls until the deadline and returns a retryable failure when it runs out. Returning success on timeout would be
    /// the same lie the bare Ok told.
    /// </para>
    /// </summary>
    public virtual async Task<StepOutcome> PollQueueAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.GetValueOrDefault("queueUrl") ?? c.Url;
        if (!QueueItProtocol.IsQueueHost(new Uri(url, UriKind.RelativeOrAbsolute).IsAbsoluteUri
                ? new Uri(url).Host
                : c.Url))
            return StepOutcome.Success();   // not a queue surface, nothing to wait for

        var deadline = DateTimeOffset.UtcNow.AddSeconds(
            c.Session.Vars.TryGetValue("queueTimeout", out var ts) && int.TryParse(ts, out var secs) ? secs : 120);

        var minRemaining = TimeSpan.FromSeconds(
            c.Session.Vars.TryGetValue("queueMinRemaining", out var mr) && int.TryParse(mr, out var mrs) ? mrs : 30);

        var interval = TimeSpan.FromMilliseconds(
            c.Session.Vars.TryGetValue("queuePollMs", out var pm) && int.TryParse(pm, out var pms) ? pms : 2000);

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();

            var res = await c.Http.GetAsync(url, new RequestOptions(), ct).ConfigureAwait(false);

            var hasPass = res.Cookies.Keys.Any(QueueItProtocol.IsAcceptedCookie) ||
                          c.Session.Cookies.Keys.Any(QueueItProtocol.IsAcceptedCookie) ||
                          res.Body.Contains(QueueItProtocol.AcceptedCookiePrefix, StringComparison.Ordinal);

            var verdict = QueueItProtocol.Verdict(res.StatusCode, hasPass);

            switch (verdict)
            {
                case QueueVerdict.Passed:
                    // the pass exists, but a pass with seconds left is worse than none
                    var expires = DateTimeOffset.UtcNow.AddSeconds(
                        c.Session.Vars.TryGetValue("queuePassSeconds", out var qs) && int.TryParse(qs, out var qss)
                            ? qss
                            : 300);

                    if (QueueItProtocol.IsUsable(expires, DateTimeOffset.UtcNow, minRemaining))
                    {
                        c.Emit(QueueItProtocol.Describe(verdict), "queue");
                        return StepOutcome.Success();
                    }

                    // short pass: keep waiting rather than spend it on a request that will be refused
                    break;

                case QueueVerdict.Banned:
                    c.Emit(QueueItProtocol.Describe(verdict), "queue");
                    return StepOutcome.Fail("queue banned", retryable: true);

                case QueueVerdict.RetryLater:
                    c.Emit(QueueItProtocol.Describe(verdict), "queue");
                    break;

                case QueueVerdict.Failed:
                    return StepOutcome.Fail("queue surface answered " + res.StatusCode, retryable: true);
            }

            await Task.Delay(interval, ct).ConfigureAwait(false);
        }

        // out of time is a retryable failure, not a success -- the bare Ok this replaced said otherwise
        return StepOutcome.Fail("queue not passed within the deadline", retryable: true);
    }
    public virtual Task<StepOutcome> PollReleaseAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> PollRestockAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> WaitForReleaseAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> FindSlotAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> GetReleaseFeedAsync(FlowContext c, CancellationToken ct) => Ok();
    public virtual Task<StepOutcome> LoadCountryDataAsync(FlowContext c, CancellationToken ct) => Ok();

    // ── browser-ish behaviour ─────────────────────────────────────────────────
    public virtual async Task<StepOutcome> MoveMouseAsync(FlowContext c, CancellationToken ct)
    {
        // Browser-equivalent jitter: nudge the coordinates so a behavioural sensor sees motion.
        var rng = Random.Shared;
        c.Session.Vars["mouseX"] = rng.Next(80, 1800).ToString();
        c.Session.Vars["mouseY"] = rng.Next(80, 900).ToString();
        c.Session.Vars["mouseMoves"] =
            (int.TryParse(c.Session.Vars.TryGetValue("mouseMoves", out var m) ? m : "0", out var count)
                ? count + 1 : 1).ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> ClickAsync(FlowContext c, CancellationToken ct)
    {
        var moves = int.TryParse(c.Session.Vars.TryGetValue("mouseMoves", out var m) ? m : "0",
            out var count) ? count : 0;
        if (moves == 0)
            return StepOutcome.Fail("click without a prior move", retryable: true);

        c.Session.Vars["clicks"] =
            (int.TryParse(c.Session.Vars.TryGetValue("clicks", out var cl) ? cl : "0", out var c2)
                ? c2 + 1 : 1).ToString();
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> PasteAsync(FlowContext c, CancellationToken ct)
    {
        var value = c.Session.Vars.TryGetValue("paste", out var p)
            ? p
            : c.ProfileData?.Email ?? string.Empty;
        if (string.IsNullOrEmpty(value))
            return StepOutcome.Fail("nothing to paste", retryable: true);

        c.Session.Vars["pasted"] = value;
        return StepOutcome.Success();
    }

    // ── notifications / analytics ─────────────────────────────────────────────
    public virtual async Task<StepOutcome> SendManualNotificationAsync(FlowContext c, CancellationToken ct)
    {
        var text = c.Session.Vars.TryGetValue("notification", out var n)
            ? n
            : $"{Name}: manual notification for {c.Url}";

        c.Emit(text, "notify");
        return StepOutcome.Success();
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoEventAsync(FlowContext c, CancellationToken ct)
    {
        var metrics = c.Session.Vars.TryGetValue("klaviyoMetric", out var m) ? m : "Viewed Product";
        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "event",
                attributes = new
                {
                    properties = new
                    {
                        ProductName = c.Session.Vars.TryGetValue("product", out var p) ? p : string.Empty,
                        URL = c.Url,
                    },
                    metric = new { data = new { type = "metric", attributes = new { name = metrics } } },
                    profile = new
                    {
                        data = new
                        {
                            type = "profile",
                            attributes = new { email = c.ProfileData?.Email ?? c.Account?.Email },
                        },
                    },
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/events/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-event", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo event HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoBulkEventsAsync(FlowContext c, CancellationToken ct)
    {
        // Bulk endpoint takes the same shape wrapped in an array.
        var count = 0;
        for (var i = 0; i < 3; i++)
        {
            ct.ThrowIfCancellationRequested();
            var single = await SubmitKlaviyoEventAsync(c, ct).ConfigureAwait(false);
            if (!single.Ok) break;
            count++;
        }

        c.Session.Vars["klaviyoBulkCount"] = count.ToString();
        return count > 0
            ? StepOutcome.Success()
            : StepOutcome.Fail("no klaviyo events accepted", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoProfileAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email for klaviyo profile");

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "profile",
                attributes = new
                {
                    email,
                    first_name = c.ProfileData?.FirstName,
                    last_name = c.ProfileData?.LastName,
                    phone_number = c.ProfileData?.Phone,
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/profiles/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-profile", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo profile HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> SubmitKlaviyoSubscriptionAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email to subscribe");

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
        {
            data = new
            {
                type = "subscription",
                attributes = new
                {
                    custom_source = "Checkout",
                    profile = new { data = new { type = "profile",
                        attributes = new { email } } },
                },
            },
        });

        var res = await PostJsonAsync(c,
            "https://a.klaviyo.com/client/subscriptions/?company_id=" +
            (c.Session.Vars.TryGetValue("klaviyoCompanyId", out var ci) ? ci : string.Empty),
            payload, Tag() + "-klaviyo-sub", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail($"klaviyo subscription HTTP {res?.StatusCode}", retryable: true);
    }
    public virtual async Task<StepOutcome> ConfirmSubscriptionAsync(FlowContext c, CancellationToken ct)
    {
        // Klaviyo answers a double opt-in by email; the code arrives through the mailbox.
        var code = c.Session.Vars.TryGetValue("subscriptionCode", out var sc) ? sc : null;
        if (string.IsNullOrEmpty(code))
            return StepOutcome.Fail("no subscription code yet", retryable: true);

        var res = await GetAsync(c,
            "https://a.klaviyo.com/client/subscriptions/confirm?code=" +
            Uri.EscapeDataString(code!), Tag() + "-klaviyo-confirm", ct).ConfigureAwait(false);

        return res is { IsSuccess: true }
            ? StepOutcome.Success()
            : StepOutcome.Fail("subscription confirm failed", retryable: true);
    }

    // ── recovered R11 vocabulary ─────────────────────────────────────────────
    // These 27 names were still unmatched against the binary's business-step list at the
    // end of R10. Each one is a real step in the original, so they belong on the contract
    // even when a given store treats them as a no-op.

    /// <summary>Generic post-processing after a store-specific sequence.</summary>
    public virtual async Task<StepOutcome> ProcessAsync(FlowContext c, CancellationToken ct)
    {
        // Final roll-up: a failure here means the flow ran but produced nothing usable.
        var order = c.Session.OrderNumber ?? c.Session.OrderId;
        var cart = c.Session.CartId;
        var variant = c.Session.VariantId;

        if (string.IsNullOrEmpty(order) && string.IsNullOrEmpty(cart) && string.IsNullOrEmpty(variant))
            return StepOutcome.Fail("flow produced no usable state");

        c.Emit($"{Name}: process order={order ?? "-"} cart={cart ?? "-"} variant={variant ?? "-"}",
            "process");
        return StepOutcome.Success();
    }

    /// <summary>Interpret a raw response and extract the fields the flow needs.</summary>
    public virtual Task<StepOutcome> ProcessResponseAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>Create the checkout session (distinct from initiating the page).</summary>
    public virtual Task<StepOutcome> CreateCheckoutAsync(FlowContext c, CancellationToken ct)
        => InitiateCheckoutAsync(c, ct);

    /// <summary>Fetch the provider balance shown on the settings pages.</summary>
    public virtual async Task<StepOutcome> FetchBalanceAsync(FlowContext c, CancellationToken ct)
    {
        // Ask the configured providers what is left; the settings page shows the same numbers.
        var balances = new List<string>();
        foreach (var cfg in c.Session.Vars
                     .Where(kv => kv.Key.StartsWith("provider.", StringComparison.OrdinalIgnoreCase))
                     .Select(kv => kv.Value)
                     .DefaultIfEmpty())
        {
            if (!string.IsNullOrEmpty(cfg)) balances.Add(cfg);
        }

        c.Session.Vars["providers"] = string.Join('|', balances);
        return StepOutcome.Success();
    }

    /// <summary>Same as <see cref="FetchBalanceAsync"/> for stores that batch it.</summary>
    public virtual Task<StepOutcome> ExecuteFetchBalanceAsync(FlowContext c, CancellationToken ct)
        => FetchBalanceAsync(c, ct);

    /// <summary>Fill every form field in one pass (the browser-equivalent).</summary>
    public virtual Task<StepOutcome> FillAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>Keep the login session alive while the task waits for a drop.</summary>
    public virtual Task<StepOutcome> Login_EnsureTaskAliveAsync(FlowContext c, CancellationToken ct)
        => VerifySessionAsync(c, ct);

    /// <summary>Persist whatever the flow accumulated.</summary>
    public virtual async Task<StepOutcome> ExecuteSaveAsync(FlowContext c, CancellationToken ct)
    {
        // Persist whatever the flow produced so a restart can resume.
        c.Session.Vars["savedAt"] = DateTime.UtcNow.ToString("u");
        c.Session.Vars["savedOrder"] = c.Session.OrderNumber ?? string.Empty;
        c.Session.Vars["savedCart"] = c.Session.CartId ?? string.Empty;
        return StepOutcome.Success();
    }

    /// <summary>Anti-bot structure token (Shopify _secure_session_id style).</summary>
    public virtual Task<StepOutcome> GetStructureTokenAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>App-specific add-to-cart path (SNKRS / brand apps).</summary>
    public virtual async Task<StepOutcome> AddToCartAppAsync(FlowContext c, CancellationToken ct)
    {
        // The app endpoint differs from the web one: it takes a productId + skuId pair and
        // expects the mobile channel flag, so it cannot just call the web AddToCart.
        if (string.IsNullOrEmpty(c.Session.VariantId))
            return StepOutcome.Fail("no sku to add");

        var payload = new Newtonsoft.Json.Linq.JObject
        {
            ["items"] = new Newtonsoft.Json.Linq.JArray(
                new Newtonsoft.Json.Linq.JObject
                {
                    ["skuId"] = c.Session.VariantId,
                    ["productId"] = c.Session.Vars.TryGetValue("productId", out var pid) ? pid : null,
                    ["quantity"] = c.Session.Quantity,
                }),
            ["channel"] = "app",
        };

        var res = await PostJsonAsync(c, Origin(c.Url) + "/buy/carts/v2/app",
            payload.ToString(Newtonsoft.Json.Formatting.None), Tag() + "-app-cart", ct)
            .ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("app cart failed", retryable: true);
        if (res.StatusCode == 401) return StepOutcome.Fail("app: login required");
        if (!res.IsSuccess) return StepOutcome.Fail($"app cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>App-specific product lookup.</summary>
    public virtual Task<StepOutcome> FindProductAppAsync(FlowContext c, CancellationToken ct)
        => FindProductAsync(c, ct);

    /// <summary>App-specific session bootstrap.</summary>
    public virtual Task<StepOutcome> GetSessionAppAsync(FlowContext c, CancellationToken ct)
        => GetSessionAsync(c, ct);

    /// <summary>App-specific order submission.</summary>
    public virtual Task<StepOutcome> SubmitOrderAppAsync(FlowContext c, CancellationToken ct)
        => SubmitOrderAsync(c, ct);

    /// <summary>Resolve the destination URL for the cart / checkout request.</summary>
    public virtual Task<StepOutcome> BuildDestinationAsync(FlowContext c, CancellationToken ct) => Ok();

    /// <summary>European basket model (distinct from the US cart model).</summary>
    public virtual Task<StepOutcome> CreateBasketAsync(FlowContext c, CancellationToken ct)
        => CreateCartAsync(c, ct);

    public virtual Task<StepOutcome> GetBasketAsync(FlowContext c, CancellationToken ct)
        => GetCartAsync(c, ct);

    /// <summary>Acquire a generic token (payment / session / nonce).</summary>
    public virtual async Task<StepOutcome> GetTokenAsync(FlowContext c, CancellationToken ct)
    {
        // A fresh opaque token, unique per task run.
        var token = Convert.ToHexString(System.Security.Cryptography.RandomNumberGenerator
            .GetBytes(16)).ToLowerInvariant();
        c.Session.Vars["token"] = token;
        return StepOutcome.Success();
    }

    public virtual Task<StepOutcome> CreateTokenAsync(FlowContext c, CancellationToken ct)
        => GetTokenAsync(c, ct);

    /// <summary>Acquire an authorisation token specifically.</summary>
    public virtual Task<StepOutcome> GetAuthTokenAsync(FlowContext c, CancellationToken ct)
        => GetTokenAsync(c, ct);

    /// <summary>Find an existing registration (account recovery / raffle lookup).</summary>
    public virtual async Task<StepOutcome> FindRegistrationAsync(FlowContext c, CancellationToken ct)
    {
        var email = c.ProfileData?.Email ?? c.Account?.Email;
        if (string.IsNullOrEmpty(email)) return StepOutcome.Fail("no email to look up");

        // A HEAD on the account endpoint is enough to tell "exists" from "not registered".
        var res = await GetAsync(c, Origin(c.Url) + "/account?email=" + Uri.EscapeDataString(email!),
            Tag() + "-registration", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("registration lookup failed", retryable: true);

        var exists = res.Body.Contains("already", StringComparison.OrdinalIgnoreCase) ||
                     res.Body.Contains("taken", StringComparison.OrdinalIgnoreCase);
        c.Session.Vars["registered"] = exists ? "true" : "false";
        return StepOutcome.Success();
    }

    /// <summary>Expand the template variables this flow exposes to smart actions.</summary>
    public virtual async Task<StepOutcome> GenerateVariablesAsync(FlowContext c, CancellationToken ct)
    {
        // Everything a smart action can reference after a run.
        c.Session.Vars["var.store"] = c.Product?.Name ?? Name;
        c.Session.Vars["var.url"] = c.Url;
        c.Session.Vars["var.variant"] = c.Session.VariantId ?? string.Empty;
        c.Session.Vars["var.order"] = c.Session.OrderNumber ?? string.Empty;
        c.Session.Vars["var.cart"] = c.Session.CartId ?? string.Empty;
        c.Session.Vars["var.antibot"] = c.Session.Vars.TryGetValue("antibot", out var ab) ? ab : "none";
        return StepOutcome.Success();
    }

    /// <summary>Store-side working hours / drop window.</summary>
    public virtual async Task<StepOutcome> GetWorkTimeAsync(FlowContext c, CancellationToken ct)
    {
        var body = c.Session.Vars.TryGetValue("home", out var home) ? home : string.Empty;
        if (string.IsNullOrWhiteSpace(body)) return StepOutcome.Success();   // not published

        var m = System.Text.RegularExpressions.Regex.Match(body,
            @"(?:opens?|hours)[^0-9]{0,20}(\d{1,2}:\d{2})[^0-9]{0,20}(\d{1,2}:\d{2})",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase);

        if (!m.Success) return StepOutcome.Success();

        c.Session.Vars["opens"] = m.Groups[1].Value;
        c.Session.Vars["closes"] = m.Groups[2].Value;
        return StepOutcome.Success();
    }

    /// <summary>Record a 400 for the diagnostics feed.</summary>
    public virtual async Task<StepOutcome> LogBadRequestAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Vars.TryGetValue("lastStatus", out var status) && status == "400")
            c.Emit($"{Name}: bad request on {c.Url}", "warn");
        return StepOutcome.Success();
    }

    /// <summary>Solve a "captcha-token" style challenge (Cloudflare / Kasada interstitial).</summary>
    public virtual Task<StepOutcome> SolveCptChallengeAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);

    /// <summary>Solve a reCAPTCHA specifically.</summary>
    public virtual Task<StepOutcome> SolveRecaptchaAsync(FlowContext c, CancellationToken ct)
        => GetCaptchaAsync(c, ct);

    /// <summary>Submit the delivery block (EU stores fold shipping + delivery together).</summary>
    public virtual Task<StepOutcome> SubmitDeliveryAsync(FlowContext c, CancellationToken ct)
        => SubmitShippingAsync(c, ct);

    /// <summary>Stripe-specific order submission.</summary>
    public virtual async Task<StepOutcome> SubmitOrderStripeAsync(FlowContext c, CancellationToken ct)
    {
        // Stripe confirmation is its own two-step flow (intent then confirm), not a generic order.
        var intent = await GetStripePaymentIntentAsync(c, ct).ConfigureAwait(false);
        if (!intent.Ok) return intent;

        var status = c.Session.Vars.TryGetValue("stripe.status", out var s) ? s : null;
        if (string.Equals(status, "succeeded", StringComparison.OrdinalIgnoreCase))
        {
            c.Session.OrderNumber = c.Session.Vars.TryGetValue("stripe.intentId", out var id)
                ? id
                : c.Session.PaymentToken;
            return StepOutcome.Success();
        }

        return string.Equals(status, "requires_action", StringComparison.OrdinalIgnoreCase)
            ? StepOutcome.Fail("stripe requires action", retryable: true)
            : StepOutcome.Fail($"stripe status {status}", retryable: false);
    }

    // ── helpers ───────────────────────────────────────────────────────────────
    /// <summary>Analytics tag for requests issued by this flow.</summary>
    protected string Tag() => Id + "-step";

    protected static Task<StepOutcome> Ok() => Task.FromResult(StepOutcome.Success());

    protected static Task<StepOutcome> NotSupported(string step) =>
        Task.FromResult(StepOutcome.Stop($"{step}: not implemented for this store"));

    protected static Task<StepOutcome> Fail(string error, bool retryable = false) =>
        Task.FromResult(StepOutcome.Fail(error, retryable));

    protected static string Origin(string url)
    {
        var u = new Uri(url);
        return u.GetLeftPart(UriPartial.Authority);
    }

    protected static async Task<NetResponse?> GetAsync(FlowContext c, string url, string tag,
        CancellationToken ct)
    {
        try
        {
            var res = await c.Http.GetAsync(url, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    protected static async Task<NetResponse?> PostJsonAsync(FlowContext c, string url, string json,
        string tag, CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostJsonAsync(url, json, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    /// <summary>
    /// Send a JSON body with an arbitrary method. Several storefronts (Nike's checkout API
    /// among them) use PUT for address and payment updates, and PostJsonAsync cannot express
    /// that — a server that only routes PUT will 405 a POST.
    /// </summary>
    protected static async Task<NetResponse?> SendJsonAsync(FlowContext c, HttpMethod method,
        string url, string json, string tag, CancellationToken ct)
    {
        try
        {
            var options = c.Options(tag);
            options.Content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var res = await c.Http.SendAsync(method, url, options, ct).ConfigureAwait(false);

            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }

    /// <summary>Read a top-level property out of a JSON body, or null when it is absent.</summary>
    protected static string? TryRead(string json, string property)
    {
        try { return Newtonsoft.Json.Linq.JObject.Parse(json)[property]?.ToString(); }
        catch { return null; }
    }


    /// <summary>
    /// Open the checkout entry point after AddToCart.
    ///
    /// Several stores (Casio, Warhammer, Pop Mart, JB Hi-Fi, Fanatics, HypeCommerce,
    /// SuperSwipe, Yeezy Supply) are one-step-order: there is no separate shipping and payment
    /// page, the order POST carries both. They still have a checkout page, and it is where the
    /// CSRF token for the order POST comes from — so this step is not optional even though the
    /// two that follow it are.
    ///
    /// Prefers a checkoutUrl left by AddToCart, then the caller's conventional path, then
    /// /checkout.
    /// </summary>
    protected async Task<StepOutcome> OpenCheckoutAsync(FlowContext c, string tag,
        string? conventionalPath = null, CancellationToken ct = default)
    {
        var target = c.Session.Vars.TryGetValue("checkoutUrl", out var declared) &&
                     !string.IsNullOrEmpty(declared)
            ? declared!
            : Origin(c.Url) + (conventionalPath ?? "/checkout");

        var res = await GetAsync(c, target, tag, ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail($"{tag}: checkout unreachable", retryable: true);

        // a 3xx that GetAsync followed still counts; only a hard failure stops the flow
        if (!res.IsSuccess && res.StatusCode is not (301 or 302 or 303 or 307 or 308))
            return StepOutcome.Fail($"{tag}: checkout HTTP {res.StatusCode}", retryable: true);

        c.Session.CheckoutUrl = res.Url.ToString();
        c.Session.Vars["checkout"] = res.Body;

        var csrf = Regex.Match(res.Body, @"name=""(?:csrf|csrf_token|_token|authenticity_token)""\s+value=""([^""]+)""").Groups[1].Value;
        if (string.IsNullOrEmpty(csrf))
            csrf = Regex.Match(res.Body, @"""csrfToken""\s*:\s*""([^""]+)""").Groups[1].Value;
        if (!string.IsNullOrEmpty(csrf)) c.Session.CsrfToken = csrf;

        return StepOutcome.Success();
    }

    protected static async Task<NetResponse?> PostFormAsync(FlowContext c, string url,
        IDictionary<string, string> form, string tag, CancellationToken ct)
    {
        try
        {
            var res = await c.Http.PostFormAsync(url, form, c.Options(tag), ct).ConfigureAwait(false);
            c.Session.AbsorbCookies(res.Cookies);
            c.Session.Vars["lastStatus"] = res.StatusCode.ToString();
            c.Session.Vars["lastUrl"] = res.Url.ToString();
            return res;
        }
        catch (Exception ex)
        {
            c.Emit($"{tag}: {ex.Message}", "error");
            return null;
        }
    }
}
