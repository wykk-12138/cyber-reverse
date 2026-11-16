"""Replace HypeCommerceFlow with the entries-only version, with guards before writing. (R800, retry)

The previous attempt replaced 244 characters and left the file unparseable. The cause was an END anchor of
"/// <summary>", which appears inside the replacement's own doc comment, so a re-run could close the span almost
immediately. This version anchors on the next class's doc line, which is outside the region and cannot move, and it
verifies the span length before writing. If any check fails it writes nothing at all.
"""

import io

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\RetailFlows.cs"
START = "class HypeCommerceFlow : StoreFlow"
END = "/// <summary>\n/// Fanatics"

NEW = '''class HypeCommerceFlow : StoreFlow
{
    public override string Id => "hypecommerce";
    public override string Name => "HypeCommerce";
    public override IReadOnlyList<string> Domains => new[] { "hypecommerce.io", "hypecommerce.com" };

    /// <summary>
    /// The host the image names. R799/R800.
    ///
    /// <para>
    /// <b>Observation:</b> the image carries six strings for this platform, all on
    /// <c>admin.hypecommerce.io/api/</c> -- <c>entries/create</c>, <c>entries/validate</c>,
    /// <c>payment/methods/store</c> and <c>settings</c>, each with exactly one builder function.
    /// </para>
    ///
    /// <para>
    /// This class used to carry a storefront chain: <c>/api/auth/login</c>, <c>GET /api/entries/{slug}</c>,
    /// <c>/api/cart</c>, <c>/api/cart/checkout</c> and <c>/checkout</c>. <b>None of those five is in the image.</b>
    /// They were invented, and they scored 71% because the coverage matrix asks whether a step is overridden, not
    /// whether its path came from evidence.
    /// </para>
    ///
    /// <para>
    /// R799 replaced them with honest failure stubs and the number did not move -- the same defect one layer down,
    /// since a declared failure counts exactly like a working step. So the stubs are gone and the base class refuses
    /// these steps instead. The matrix now reports one of seven, which is what the evidence supports, and the reason
    /// lives here and in the exemption table rather than in a number that overstates.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown:</b> the request bodies for validate and create. The builder serialises an object supplied by its
    /// caller, so the field names live in the caller's type rather than in the function -- the asymmetry that has cost
    /// five rounds across casio, goat, popmart and this one.
    /// </para>
    /// </summary>
    private const string HypeApi = "https://admin.hypecommerce.io";

    /// <summary>
    /// Create an entry the way the image does: validate, then create. The only step this module can evidence.
    ///
    /// <para>
    /// The body carries only what the replica knows, and a rejection is the honest outcome until the payload is
    /// recovered. An invented body would look like progress and would not be one.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitOrderAsync(FlowContext c, CancellationToken ct)
    {
        var entryId = c.Session.VariantId;
        if (string.IsNullOrEmpty(entryId))
            return StepOutcome.Fail("hypecommerce: no entry id to submit");

        var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new { entryId });

        var validate = await PostJsonAsync(c, HypeApi + "/api/entries/validate", payload,
            "hype-validate", ct).ConfigureAwait(false);
        if (validate is null) return StepOutcome.Fail("hypecommerce: validate unreachable", retryable: true);
        if (!validate.IsSuccess)
            return StepOutcome.Fail($"hypecommerce: validate HTTP {validate.StatusCode}", retryable: true);

        var create = await PostJsonAsync(c, HypeApi + "/api/entries/create", payload,
            "hype-create", ct).ConfigureAwait(false);
        if (create is null) return StepOutcome.Fail("hypecommerce: create unreachable", retryable: true);
        if (!create.IsSuccess)
            return StepOutcome.Fail($"hypecommerce: create HTTP {create.StatusCode}", retryable: true);

        c.Session.Vars["entry"] = create.Body;
        return StepOutcome.Success();
    }
}

'''


def main():
    text = io.open(PATH, encoding="utf-8").read()
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0 or end <= start:
        print("  anchors not found or out of order: start=%d end=%d" % (start, end))
        return 1

    span = text[start:end]
    print("  span: %d chars" % len(span))
    if len(span) < 4000:
        print("  refusing: span is too short to be the class body")
        return 1
    for must in ("HypeApi", "SubmitOrderAsync", "OpenCheckoutAsync"):
        if must not in span:
            print("  refusing: span does not contain %s" % must)
            return 1

    out = text[:start] + NEW + text[end:]

    # post-conditions: one class declaration, no invented paths, no failure stubs
    if out.count("class HypeCommerceFlow") != 1:
        print("  refusing: class declaration count is wrong")
        return 1
    for gone in ('"/api/cart/checkout"', '"/api/auth/login"', '"hype-checkout"', "NoStorefront"):
        if gone in out:
            print("  refusing: %s survived" % gone)
            return 1
    if out.count("public override async Task<StepOutcome> SubmitOrderAsync") < 1:
        print("  refusing: SubmitOrderAsync missing after replacement")
        return 1

    io.open(PATH, "w", encoding="utf-8", newline="").write(out)
    print("  written: %d -> %d chars" % (len(text), len(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
