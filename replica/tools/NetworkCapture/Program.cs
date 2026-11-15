using Cybersole.Stores.Scripts;

// Standalone capture harness.
//
// Why a console app instead of a test: a headed Chrome launched from the test host is not
// reaped, and the run hangs instead of failing. Running here owns the process lifetime.
//
//   dotnet run --project tools/NetworkCapture -- <url> [seconds] [--headless] [--scroll]
//                                                    [--click=<css>] [--find-add]
//
// --scroll  drive the page down a few screens first. Storefront grids are lazy-loaded.
// --click=  click one element by CSS selector, then wait, so the request it triggers is caught.
// --find-add  list the candidate add-to-cart controls on the page and exit. Use it to get a
//             selector for --click without opening devtools.
//
// Without --click an add-to-cart capture is impossible: the cart endpoint only appears in
// response to a click, and guessing it has already produced three wrong platform guesses.

var url = args.FirstOrDefault(a => !a.StartsWith('-'));
var seconds = 8;
var headed = !args.Contains("--headless");
var scroll = args.Contains("--scroll");
var findAdd = args.Contains("--find-add");

var clickSelector = args
    .FirstOrDefault(a => a.StartsWith("--click=", StringComparison.Ordinal))?["--click=".Length..];

foreach (var a in args.Where(x => int.TryParse(x, out _))) int.TryParse(a, out seconds);

if (url is null)
{
    Console.Error.WriteLine(
        "usage: NetworkCapture <url> [seconds] [--headless] [--scroll] " +
        "[--click=<css>] [--steps=\"click:<css>; wait:<ms>; eval:<js>\"] " +
        "[--find-add] [--follow=<n>] [--mouse=<css>] [--mouse-xy=x,y] [--await-url=<s>]");
    return 2;
}

Console.WriteLine($"capturing {url}");
Console.WriteLine($"  mode:   {(headed ? "headed (gets past bot detection)" : "headless (many stores 403 this)")}");
Console.WriteLine($"  window: {seconds}s" + (scroll ? ", scrolling" : "") +
                  (clickSelector is null ? "" : $", clicking {clickSelector}"));
Console.WriteLine();

if (ChromiumBridge.FindBrowser() is null)
{
    Console.Error.WriteLine("no Chrome/Edge found on this machine");
    return 3;
}

NetworkRecorder? rec = null;

try
{
    rec = await NetworkRecorder.BeginAsync(headed: headed);

    await rec.VisitAsync(url);

    if (scroll)
    {
        // step down a screen at a time and give the grid time to fetch each batch
        for (var step = 1; step <= 5; step++)
        {
            await rec.RunAsync($"window.scrollTo(0, document.body.scrollHeight * {step} / 5)");
            await rec.WaitAsync(TimeSpan.FromSeconds(2));
        }

        await rec.RunAsync("window.scrollTo(0, 0)");
    }

    // --mouse drives a real pointer through CDP. The difference from an eval-step click is
    // isTrusted: true on the resulting event, which is what bot walls actually look at.
    var mouseSel = args.FirstOrDefault(a => a.StartsWith("--mouse=", StringComparison.Ordinal))
        ?["--mouse=".Length..];
    var mouseXy = args.FirstOrDefault(a => a.StartsWith("--mouse-xy=", StringComparison.Ordinal))
        ?["--mouse-xy=".Length..];

    if (mouseSel is not null)
    {
        var box = await rec.MouseClickAsync(mouseSel);
        Console.WriteLine($"--- mouse click {mouseSel} -> {box ?? "not found"} ---");
        await rec.WaitAsync(TimeSpan.FromSeconds(4));
        Console.WriteLine();
    }
    else if (mouseXy is not null)
    {
        var parts = mouseXy.Split(',');
        if (parts.Length == 2
            && double.TryParse(parts[0], out var mx) && double.TryParse(parts[1], out var my))
        {
            await rec.MouseMoveAsync(mx, my);
            await rec.MouseClickAsync(mx, my);
            Console.WriteLine($"--- mouse click at {mx},{my} ---");
            await rec.WaitAsync(TimeSpan.FromSeconds(4));
            Console.WriteLine();
        }
        else
        {
            Console.Error.WriteLine($"bad --mouse-xy value: {mouseXy} (want x,y)");
        }
    }

    // --follow walks down one level of listing pages on its own. Bstn's product pages sit two
    // grids below the entry URL; probing that by hand costs a run per level.
    var followArg = args.FirstOrDefault(a => a.StartsWith("--follow=", StringComparison.Ordinal));
    if (followArg is not null && int.TryParse(followArg["--follow=".Length..], out var followCount)
        && followCount > 0)
    {
        var host = Uri.TryCreate(url, UriKind.Absolute, out var entryUri)
            ? entryUri.Host
            : string.Empty;

        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var frontier = new List<string> { url };
        var deepest = new List<(string Url, int Depth)>();

        for (var level = 1; level <= followCount && frontier.Count > 0; level++)
        {
            var next = new List<string>();

            foreach (var page in frontier.Take(4))
            {
                await rec.VisitAsync(page);

                // scroll each page it walks to, not just the entry page: a lazy grid renders
                // nothing until it is scrolled, and --follow re-navigates, discarding whatever
                // the entry-page scroll produced. Offspring's listing returned 0 links until
                // this was added.
                if (scroll)
                {
                    for (var step = 1; step <= 3; step++)
                    {
                        await rec.RunAsync($"window.scrollTo(0, document.body.scrollHeight * {step} / 3)");
                        await rec.WaitAsync(TimeSpan.FromSeconds(1));
                    }
                }

                await rec.WaitAsync(TimeSpan.FromSeconds(2));

                var walked = await rec.CollectLinksAsync();

                foreach (var link in walked)
                {
                    if (!seen.Add(link)) continue;
                    if (!Uri.TryCreate(link, UriKind.Absolute, out var u)) continue;
                    if (!u.Host.Equals(host, StringComparison.OrdinalIgnoreCase)) continue;

                    var depth = u.AbsolutePath.Count(c => c == '/');
                    deepest.Add((link, depth));

                    // candidates for the next level: deeper than the entry page, not a leaf
                    if (depth >= 3 && depth <= 6) next.Add(link);
                }
            }

            frontier = next
                .OrderByDescending(x => Uri.TryCreate(x, UriKind.Absolute, out var u)
                    ? u.AbsolutePath.Count(c => c == '/')
                    : 0)
                .Take(followCount)
                .ToList();

            Console.WriteLine($"--- level {level}: {next.Count} candidate(s), " +
                              $"following {frontier.Count} ---");
        }

        Console.WriteLine();
        Console.WriteLine($"--- {deepest.Count} same-host link(s), deepest first ---");
        foreach (var (link, depth) in deepest.OrderByDescending(d => d.Depth).Take(25))
            Console.WriteLine($"  d{depth}  {link}");

        Console.WriteLine();
        Console.WriteLine("a product page is usually the deepest thing that is not itself a grid");
        return 0;
    }

    // --eval-file runs JavaScript from a file. Passing a non-trivial script through --steps is
    // unreliable: the shell eats the quotes, and a single ';' inside the script splits it into
    // fragments (hence ';;'). A file sidesteps both.
    var evalFileArg = args.FirstOrDefault(a => a.StartsWith("--eval-file=", StringComparison.Ordinal));
    if (evalFileArg is not null)
    {
        var path = evalFileArg["--eval-file=".Length..];

        if (!File.Exists(path))
        {
            Console.Error.WriteLine($"eval file not found: {path}");
            return 5;
        }

        var script = await File.ReadAllTextAsync(path);
        Console.WriteLine($"--- eval-file {path} ({script.Length} chars) ---");
        Console.WriteLine(await rec.RunAsync(script));
        await rec.WaitAsync(TimeSpan.FromSeconds(2));
        Console.WriteLine();
    }

    if (findAdd)
    {
        // report the controls that look like add-to-cart, with the attributes needed to
        // re-select them, so the caller can pass one to --click
        const string probe = """
            JSON.stringify((() => {
              const pick = el => ({
                tag: el.tagName.toLowerCase(),
                text: (el.textContent || el.value || '').trim().slice(0, 40),
                id: el.id || null,
                cls: (el.className || '').toString().slice(0, 70) || null,
                testid: el.getAttribute('data-testid') || el.getAttribute('data-test-id') || null,
                action: el.getAttribute('data-action') || el.getAttribute('data-click') || null,
                disabled: el.disabled === true
              });

              // a storefront's buy control is not always a <button>: HBX's product page has
              // zero buttons, so the selector has to reach divs, spans and anchors that merely
              // behave like one. Cast wider, then let the text/attribute filter decide.
              const wide = Array.from(document.querySelectorAll(
                'button, a, input[type=submit], [role=button], [data-action], [data-click], ' +
                '[class*=add], [class*=cart], [class*=buy], [data-testid*=add], [data-test-id*=add]'
              ));

              const addish = wide.filter(el =>
                /add\s*to\s*(cart|bag|basket)|buy\s*now|in\s*den\s*warenkorb|ajouter|add\b|cart|bag/i
                  .test((el.textContent || el.value || el.getAttribute('aria-label') ||
                         el.className || '').toString()));

              return {
                totalButtons: document.querySelectorAll('button').length,
                totalWide: wide.length,
                addish: addish.slice(0, 20).map(pick),
                all: addish.length === 0 ? wide.slice(0, 30).map(pick) : []
              };
            })())
            """;

        var found = await rec.RunAsync(probe);

        Console.WriteLine("--- add-to-cart candidates ---");
        Console.WriteLine(found ?? "(none)");
        Console.WriteLine();
        Console.WriteLine("pass one as --click (e.g. --click=\"button[data-testid='add-to-cart']\")");
        Console.WriteLine("if the addish list is empty, the button is gated behind a size/colour");
        Console.WriteLine("choice — the `all` list shows what the page actually offers.");
        return 0;
    }

    // --steps runs a small script of interactions. An add-to-cart capture needs at least two:
    // choose a size, then press the button that only becomes live once a size is chosen.
    var stepsArg = args.FirstOrDefault(a => a.StartsWith("--steps=", StringComparison.Ordinal));
    var steps = stepsArg?["--steps=".Length..];

    if (steps is not null)
    {
        Console.WriteLine("--- steps ---");

        // ';;' rather than ';': an eval step is JavaScript, and JavaScript is full of
        // semicolons. Splitting on a single one truncated every non-trivial script.
        var sep = steps.Contains(";;") ? ";;" : ";";

        foreach (var raw in steps.Split(sep, StringSplitOptions.RemoveEmptyEntries))
        {
            var step = raw.Trim();
            var colon = step.IndexOf(':');
            var kind = (colon < 0 ? step : step[..colon]).Trim().ToLowerInvariant();
            var arg = colon < 0 ? string.Empty : step[(colon + 1)..].Trim();

            switch (kind)
            {
                case "click":
                {
                    var script = $$"""
                        (() => {
                          const el = document.querySelector({{System.Text.Json.JsonSerializer.Serialize(arg)}});
                          if (!el) return 'not found';
                          el.scrollIntoView({block: 'center'});
                          el.click();
                          return 'clicked';
                        })()
                        """;
                    Console.WriteLine($"  click {arg} -> {await rec.RunAsync(script)}");
                    await rec.WaitAsync(TimeSpan.FromSeconds(2));
                    break;
                }

                case "eval":
                    Console.WriteLine($"  eval -> {await rec.RunAsync(arg)}");
                    await rec.WaitAsync(TimeSpan.FromSeconds(1));
                    break;

                case "wait":
                {
                    var ms = int.TryParse(arg, out var parsed) ? parsed : 500;
                    Console.WriteLine($"  wait {ms}ms");
                    await rec.WaitAsync(TimeSpan.FromMilliseconds(ms));
                    break;
                }

                default:
                    Console.WriteLine($"  unknown step '{kind}' — ignored");
                    break;
            }
        }

        Console.WriteLine();
    }

    // --await-url polls location.href until it changes. A client-side router pushes the new URL
    // asynchronously after a click, so reading it immediately returns the old page. Bstn is the
    // case that needs this: its product tiles are plain divs and the URL only appears once the
    // SPA routes.
    var awaitArg = args.FirstOrDefault(a => a.StartsWith("--await-url", StringComparison.Ordinal));
    if (awaitArg is not null)
    {
        var limit = 8;
        var eq = awaitArg.IndexOf('=');
        if (eq > 0 && int.TryParse(awaitArg[(eq + 1)..], out var parsed)) limit = parsed;

        var before = await rec.RunAsync("location.href");
        Console.WriteLine($"--- await-url (max {limit}s), from {before} ---");

        var deadline = DateTime.UtcNow.AddSeconds(limit);
        string? after = before;

        while (DateTime.UtcNow < deadline)
        {
            await rec.WaitAsync(TimeSpan.FromMilliseconds(400));
            after = await rec.RunAsync("location.href");

            if (!string.IsNullOrEmpty(after) && after != before)
            {
                Console.WriteLine($"--- url changed -> {after} ---");
                break;
            }
        }

        if (after == before)
            Console.WriteLine($"--- url did not change within {limit}s ---");

        Console.WriteLine();
    }

    else if (clickSelector is not null)
    {
        // single-click form, kept for the common case
        var clickScript = $$"""
            (() => {
              const el = document.querySelector({{System.Text.Json.JsonSerializer.Serialize(clickSelector)}});
              if (!el) return 'not found';
              el.scrollIntoView({block: 'center'});
              el.click();
              return 'clicked';
            })()
            """;

        var outcome = await rec.RunAsync(clickScript);
        Console.WriteLine($"--- click: {outcome} ---");
        await rec.WaitAsync(TimeSpan.FromSeconds(5));
    }

    await rec.WaitAsync(TimeSpan.FromSeconds(seconds));

    var api = rec.ApiCalls.ToList();

    Console.WriteLine($"--- {api.Count} call(s) ---");
    Console.WriteLine(rec.Describe());

    Console.WriteLine();
    Console.WriteLine("--- hosts seen ---");
    foreach (var group in api
                 .Where(c => c.Url is not null)
                 .GroupBy(c => Uri.TryCreate(c.Url!, UriKind.Absolute, out var u) ? u.Host : "?")
                 .OrderByDescending(g => g.Count()))
        Console.WriteLine($"  {group.Count(),3}  {group.Key}");

    // product URLs the page itself linked to — the thing that cannot be found in static HTML
    var links = await rec.CollectLinksAsync();
    Console.WriteLine();
    Console.WriteLine($"--- {links.Count} link(s) in the rendered DOM ---");

    var productish = NetworkRecorder.Productish(links).Take(12).ToList();
    if (productish.Count > 0)
    {
        Console.WriteLine("--- product-shaped links ---");
        foreach (var p in productish) Console.WriteLine($"  {p}");
    }
    else
    {
        // nothing matched the obvious shapes; show the DEEPEST paths instead, because a
        // product page sits below categories and the heuristic may simply not fit this site
        Console.WriteLine("--- no product-shaped links; deepest paths instead ---");
        var deepest = links
            .Select(l => (Link: l,
                          Depth: Uri.TryCreate(l, UriKind.Absolute, out var u)
                              ? u.AbsolutePath.Count(c => c == '/')
                              : 0))
            .Where(x => x.Depth >= 2)
            .OrderByDescending(x => x.Depth)
            .Take(15)
            .ToList();

        foreach (var (link, depth) in deepest) Console.WriteLine($"  d{depth}  {link}");
    }

    var blocked = api.Count > 0 && api.All(c => c.Status == 403);
    Console.WriteLine();
    Console.WriteLine(blocked
        ? "RESULT: blocked (403) — retry with a persistent profile"
        : $"RESULT: captured {api.Count} call(s)");

    return blocked ? 1 : 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine("capture failed: " + ex.Message);
    return 4;
}
finally
{
    if (rec is not null) await rec.DisposeAsync();
}

