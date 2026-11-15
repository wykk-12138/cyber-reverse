import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\NikeFlow.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    public override async Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Cookies.TryGetValue("NIKE_COMMERCE_COUNTRY", out var country))
            c.Session.Vars["country"] = country;
        return StepOutcome.Success();
    }'''

new = '''    public override async Task<StepOutcome> GetSessionAsync(FlowContext c, CancellationToken ct)
    {
        if (c.Session.Cookies.TryGetValue("NIKE_COMMERCE_COUNTRY", out var country))
            c.Session.Vars["country"] = country;

        // R88: the image carries four Nike request headers (nike-api-caller-id, x-nike-ux-id,
        // x-nike-visitid, x-nike-visitorid) plus the Kasada version, and the replica sent none of
        // them. The values come from what the site hands back — the flow records them as session
        // vars — so a header is only sent when it is actually known. See NikeHeaders.
        foreach (var (varKey, header) in NikeHeaders.FromSessionVar)
            if (c.Session.Vars.TryGetValue(varKey, out var value) && !string.IsNullOrWhiteSpace(value))
                c.Session.Headers[header] = value;

        return StepOutcome.Success();
    }'''

if old not in t:
    raise SystemExit("GetSessionAsync anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("Nike headers wired into GetSessionAsync")
