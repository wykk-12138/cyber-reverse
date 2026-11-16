"""Drop HypeCommerceFlow's honest-failure overrides so the matrix stops counting them. (R800)

R799 replaced five invented storefront paths with honest failures, and the coverage matrix kept reporting 71%: it asks
whether a step is overridden, not whether the override can do anything. So seven declared failures were
indistinguishable from seven working steps -- the same trap R772 recorded when it noted that declaring an override
counts as an implementation.

The fix is to stop declaring them. The base class already refuses the seven required steps, so leaving them alone makes
the matrix report '-' and the module lands at one of seven, which is what the evidence supports: hypecommerce's image
surface is an admin entries API and one step (validate then create) can be built from it.

The explanation moves to the class documentation and the exemption entry, which is where a reader looks for reasons
anyway. A number that says "one step" plus a paragraph saying why is more useful than a number that says "five steps"
and is false.
"""

import io

PATH = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\RetailFlows.cs"
START = "class HypeCommerceFlow : StoreFlow"
END = "/// <summary>"

NEW = '''class HypeCommerceFlow : StoreFlow
{
    public override string Id => "hypecommerce";
    public override string Name => "HypeCommerce";
    public override IReadOnlyList<string> Domains => new[] { "hypecommerce.io", "hypecommerce.com" };

    /// <summary>
    /// The host the image actually names. R799/R800.
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
    /// They were invented, and they scored seventy-one percent because the coverage matrix asks whether a step is
    /// overridden, not whether its path came from evidence.
    /// </para>
    ///
    /// <para>
    /// R799 replaced them with honest failure stubs, and the number stayed at seventy-one percent -- which is the
    /// same defect one layer down: a declared failure counts exactly like a working step. So the stubs are gone and
    /// the base class refuses these steps instead. The matrix now reports what is true, one of seven, and the reason
    /// lives here and in the exemption table rather than in a number that overstates.
    /// </para>
    ///
    /// <para>
    /// <b>Unknown:</b> the request bodies for validate and create. The builder serialises an object supplied by its
    /// caller, so the field names live in the caller's type rather than in the function -- the asymmetry that has now
    /// cost five rounds across casio, goat, popmart and this one.
    /// </para>
    /// </summary>
    private const string HypeApi = "https://admin.hypecommerce.io";

    /// <summary>
    /// Create an entry the way the image does: validate, then create. The only step this module can evidence.
    ///
    /// <para>
    /// The body carries only what the replica knows, and a rejection is the honest outcome until the payload is
    /// recovered. Sending an invented body would look like progress and would not be one.
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
    if start < 0:
        print("  START anchor missing")
        return 1
    end = text.find(END, start)
    if end < 0:
        print("  END anchor missing")
        return 1

    out = text[:start] + NEW + text[end:]
    io.open(PATH, "w", encoding="utf-8", newline="").write(out)

    overrides = out[start:out.find(END, start)].count("override")
    print("  replaced %d chars; overrides in the new class: %d" % (end - start, overrides))
    print("  NoStorefront stubs left anywhere: %s" % ("NoStorefront" in out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
