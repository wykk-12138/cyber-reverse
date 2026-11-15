import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlow.cs"
t = io.open(p, encoding="utf-8").read()

# 1) after detection, actually run the wall's ladder — the last layer of R140/R141's defect:
#    the call existed but nothing called it.
old = '''        c.Session.Vars["antibot"] = vendor;
        c.Emit($"{Name}: anti-bot = {vendor}", "detect");
        return StepOutcome.Success();
    }'''

new = '''        c.Session.Vars["antibot"] = vendor;
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
    }'''

if old not in t:
    raise SystemExit("detect anchor missing")
t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("DetectAsync now dispatches to the wall's strategy")
