import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\PopMartFlow.cs"
t = io.open(p, encoding="utf-8").read()

anchor = '''    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "popmart-checkout", "/checkout", ct);'''

add = '''    /// <summary>
    /// The cart read — R122 found a six-method cart class whose first method is
    /// <c>GetCartDataList</c>, and this endpoint is named for it.
    ///
    /// <para>
    /// The draw half of Pop Mart (twenty-four steps: draws, points, reservations) and the buying half
    /// (this class) are two different things, which R116 inferred from the twenty-five unused endpoints
    /// and R122 confirmed from the class itself. Reading the cart is the first buying step.
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> GetCartAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetJsonAsync(c,
            Origin(c.Url) + PopMartEndpoints.ShoppingCartDataList + "cart",
            "popmart-cart-read", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("popmart cart read failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"popmart cart HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["cart"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>FetchCoupons</c> — the second method of the cart class, served by the coupons list.
    /// </summary>
    public override async Task<StepOutcome> FetchCouponsAsync(FlowContext c, CancellationToken ct)
    {
        var res = await GetJsonAsync(c, Origin(c.Url) + PopMartEndpoints.CouponsList,
            "popmart-coupons", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("popmart coupons failed", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"popmart coupons HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["coupons"] = res.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// <c>SubmitDiscount</c> — the third method. A checkout cannot apply a discount without verifying
    /// the coupon, so this posts the code to the verify endpoint and records the verdict.
    ///
    /// <para>
    /// A rejection here is not a failure to retry: a coupon that does not apply still leaves an
    /// orderable cart, exactly as a non-raffle store still checks out (R99).
    /// </para>
    /// </summary>
    public override async Task<StepOutcome> SubmitDiscountAsync(FlowContext c, CancellationToken ct)
    {
        var code = c.ProfileData?.DiscountCode;
        if (string.IsNullOrWhiteSpace(code))
        {
            c.Session.Vars["discount"] = "absent";
            return StepOutcome.Success();
        }

        var payload = new JObject { ["couponCode"] = code };

        var res = await PostJsonAsync(c, Origin(c.Url) + PopMartEndpoints.CouponsVerify,
            payload.ToString(Newtonsoft.Json.Formatting.None), "popmart-discount", ct).ConfigureAwait(false);

        if (res is null)
        {
            c.Session.Vars["discount"] = "unknown";
            return StepOutcome.Success();
        }

        c.Session.Vars["discount"] = res.IsSuccess ? "applied" : "rejected";
        return StepOutcome.Success();
    }

    public override Task<StepOutcome> GetCheckoutAsync(FlowContext c, CancellationToken ct) =>
        OpenCheckoutAsync(c, "popmart-checkout", "/checkout", ct);'''

if anchor not in t:
    raise SystemExit("checkout anchor missing")
if "GetCartAsync" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add, 1))
    print("three cart-half steps added")
