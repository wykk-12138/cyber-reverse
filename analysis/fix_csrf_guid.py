"""Remove the three GUID fallbacks that invent a CSRF token. (R823)

ShopifyFlow, FootsitesFlow and MagentoFlow all do `Guid.NewGuid().ToString("N")` when their extraction finds nothing, and
Magento sends that value as ["CSRFToken"]. A fabricated token is worse than an absent one: the server answers "invalid"
and the blame looks like a protocol problem, while an absent token answers "missing" and points at the extraction that
failed. The standard in use all session is that a clear failure beats a silent wrong value, and this is a silent wrong
value generated on purpose.

Each site already extracts the real token when it can -- Shopify from name="authenticity_token", Footsites from a
csrf_token JSON key then the XSRF-TOKEN cookie, Magento from form_key -- so the fallback only fires when extraction
failed, which is exactly when inventing a value hides the failure.

No test asserts the fabricated value, checked before editing. Consumers already guard on IsNullOrEmpty, so an absent
token is handled.
"""

import io

EDITS = [
    (
        r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ShopifyFlow.cs",
        """    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        if (!string.IsNullOrEmpty(c.Session.CsrfToken)) return StepOutcome.Success();
        c.Session.CsrfToken = Guid.NewGuid().ToString("N");
        return StepOutcome.Success();
    }
""",
        """    public override async Task<StepOutcome> GetCsrfAsync(FlowContext c, CancellationToken ct)
    {
        // R823: no fabricated fallback. GetHomeAsync already extracts name="authenticity_token" from the page when the
        // page carries one; if it did not, inventing a GUID here would put a token in the session that this server never
        // issued, and every request carrying it would be rejected as invalid rather than recognised as tokenless.
        // Shopify's cart endpoints do not require one at all, so an absent token is the truthful state.
        return StepOutcome.Success();
    }
""",
    ),
    (
        r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\FootsitesFlow.cs",
        """        c.Session.CsrfToken = string.IsNullOrEmpty(token) ? Guid.NewGuid().ToString("N") : token;
""",
        """        // R823: when neither the page nor the XSRF-TOKEN cookie yields one, the session stays tokenless. The previous
        // fallback was a fresh GUID, which no server has ever issued -- a silent wrong value in place of the information
        // that extraction failed.
        if (!string.IsNullOrEmpty(token)) c.Session.CsrfToken = token;
""",
    ),
    (
        r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\MagentoFlow.cs",
        """        if (!string.IsNullOrEmpty(c.Session.CsrfToken)) return StepOutcome.Success();

        c.Session.CsrfToken = Guid.NewGuid().ToString("N");
        c.Session.Headers["X-Requested-With"] = "XMLHttpRequest";
        return StepOutcome.Success();
""",
        """        if (!string.IsNullOrEmpty(c.Session.CsrfToken)) return StepOutcome.Success();

        // R823: Magento sends this value as ["CSRFToken"], so a fabricated one guaranteed an "invalid form key" answer
        // that looked like a protocol mismatch. GetHomeAsync extracts form_key when the page carries it; when it does
        // not, the session stays tokenless and the submission reports a missing key, which is the true condition.
        c.Session.Headers["X-Requested-With"] = "XMLHttpRequest";
        return StepOutcome.Success();
""",
    ),
]


def main():
    for path, old, new in EDITS:
        t = io.open(path, encoding="utf-8").read()
        if t.count(old) != 1:
            print("  %-22s anchor count %d — skipping" % (path.split("\\")[-1], t.count(old)))
            continue
        out = t.replace(old, new, 1)
        io.open(path, "w", encoding="utf-8", newline="").write(out)
        print("  %-22s replaced; Guid.NewGuid left: %d" % (path.split("\\")[-1], out.count('Guid.NewGuid().ToString("N")')))

    print()
    import os
    total = 0
    for d, _, fs in os.walk(r"D:\projects\cyber-reverse\replica\src"):
        for f in fs:
            if f.endswith(".cs"):
                p = os.path.join(d, f)
                c = io.open(p, encoding="utf-8", errors="replace").read().count('Guid.NewGuid().ToString("N")')
                if c:
                    print("  still present: %-24s %d" % (f, c))
                    total += c
    print("  total fabricated-token sites left in src: %d" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
