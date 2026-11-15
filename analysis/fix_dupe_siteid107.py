import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\DemandwareFlow.cs"
t = io.open(p, encoding="utf-8").read()

# There is already a SiteId(FlowContext) on this flow — reuse it instead of adding a second.
old_marker = '''    /// <summary>
    /// The <c>siteId</c> an SCAPI call needs. It is the site id the store already carries
    /// (<c>Sites-{site}-Site</c>), not a separate value.
    /// </summary>
    private static string SiteId(FlowContext c) =>
        c.Session.Vars.TryGetValue("site", out var site) && !string.IsNullOrWhiteSpace(site)
            ? site
            : "default";'''

replacement = '''    /// <summary>
    /// The <c>siteId</c> an SCAPI call needs — the same site id the flow already carries
    /// (<c>Sites-{site}-Site</c>), not a separate value, so it reuses <c>SiteId</c>.
    /// </summary>'''

if old_marker not in t:
    raise SystemExit("new SiteId helper not found")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old_marker, replacement, 1))
print("duplicate SiteId removed")
