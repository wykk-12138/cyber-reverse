import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)"
if anchor not in t:
    raise SystemExit("anchor missing")

raffle_step = '''    /// <summary>
    /// Enters a Demandware draw. The image carries the three pieces this needs: the
    /// <c>SaleRegistration-Config</c> / <c>SaleRegistration-SignupSubmit</c> controllers a sale
    /// registration also uses, the <c>panagora-raffle-data</c> script the page carries its payload
    /// in, and <c>Already Entered Draw</c> as the duplicate-entry answer.
    ///
    /// <para>
    /// A page with no raffle payload is <b>not</b> a failure: most Demandware stores are not running
    /// a draw, and turning that into an error would fail every normal checkout that never asked for
    /// one. It records <c>raffle=absent</c> and succeeds.
    /// </para>
    /// </summary>
    public async Task<StepOutcome> EnterRaffleAsync(FlowContext c, CancellationToken ct)
    {
        var page = await GetAsync(c, Origin(c.Url) + DemandwareRaffle.EntryPage,
            Tag() + "-raffle-page", ct).ConfigureAwait(false);

        if (page is null) return StepOutcome.Fail("raffle page unreachable", retryable: true);

        var payload = DemandwareRaffle.ExtractData(page.Body);
        if (payload is null)
        {
            c.Session.Vars["raffle"] = "absent";
            return StepOutcome.Success();
        }

        c.Session.Vars["raffle"] = "present";
        c.Session.Vars["raffle.data"] = payload;

        var id = DemandwareRaffle.ExtractId(page.Body);
        if (id is not null) c.Session.Vars["raffle.id"] = id;

        var config = await GetAsync(c, Controller(c, DemandwareControllers.SaleConfig),
            Tag() + "-raffle-config", ct).ConfigureAwait(false);

        if (config is not null && !config.IsSuccess)
            return StepOutcome.Fail($"raffle config HTTP {config.StatusCode}", retryable: true);

        var form = new Dictionary<string, string>
        {
            ["raffleId"] = id ?? string.Empty,
            ["email"] = c.Session.Vars.TryGetValue("email", out var email) ? email : string.Empty,
        };

        var submit = await PostFormAsync(c, Controller(c, DemandwareControllers.SaleSignupSubmit),
            form, Tag() + "-raffle-submit", ct).ConfigureAwait(false);

        if (submit is null) return StepOutcome.Fail("raffle submit failed", retryable: true);

        if (DemandwareRaffle.IsAlreadyEntered(submit.Body))
        {
            c.Session.Vars["raffle.status"] = "already-entered";
            return StepOutcome.Success();
        }

        if (!submit.IsSuccess)
            return StepOutcome.Fail($"raffle submit HTTP {submit.StatusCode}", retryable: true);

        c.Session.Vars["raffle.status"] = "entered";
        return StepOutcome.Success();
    }

'''

io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, raffle_step + anchor, 1))
print("EnterRaffleAsync inserted before GetCartAsync")
