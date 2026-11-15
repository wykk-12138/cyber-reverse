import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs"
t = io.open(p, encoding="utf-8").read()

anchor = """    /// <summary>All five flows.</summary>"""

add = '''    /// <summary>
    /// A UK retailer's app flow: 17 steps that keep an <c>App</c> path (<c>FindProductApp</c>,
    /// <c>GetSessionApp</c>, <c>AddToCartApp</c>, <c>CreateCheckoutApp</c>) beside the web steps, and
    /// end in <c>StartPayment</c> / <c>GetPaymentUrl</c> rather than a card form.
    ///
    /// <para>
    /// The distinctive pair is <c>GetCollectPlusLocations</c> / <c>SubmitCollectPlus</c>: CollectPlus
    /// is a UK parcel network, so this flow is a UK store with click-and-collect. <b>The brand is not
    /// proven</b> — CollectPlus is used by more than one UK retailer — so the flow is named for its
    /// evidence, not for a guess at the logo.
    /// </para>
    /// </summary>
    public static readonly Flow CollectPlusApp = new("collectplus-app", new[]
    {
        new Step("GetHome", 33), new Step("GetProduct", 34), new Step("FindProductApp", 35),
        new Step("GetSessionApp", 36), new Step("AddToCartApp", 37),
        new Step("CreateCheckoutApp", 38), new Step("GetBasket", 39), new Step("AddToCart", 40),
        new Step("SubmitDiscount", 41), new Step("LookupAddress", 42), new Step("GetDelivery", 43),
        new Step("GetCollectPlusLocations", 44), new Step("SubmitCollectPlus", 45),
        new Step("SubmitDelivery", 47), new Step("SubmitBilling", 48),
        new Step("StartPayment", 49), new Step("GetPaymentUrl", 50),
    });

    /// <summary>
    /// Fifteen steps on an engine that issues a <b>structure token</b> before it will take a payment:
    /// <c>GetMerchantCode</c> → <c>GetStructureToken</c> → <c>CreateTransaction</c> →
    /// <c>SubmitPayment</c> → <c>ProcessPayment</c>.
    ///
    /// <para>
    /// The payment vocabulary is the evidence: the image also carries
    /// <c>PaymentData.UrlStructureTokenEncoded</c>, <c>_structureToken</c> and
    /// <c>#UrlStructureTokenEncoded</c>, so "structure token" is a real field of a real payment
    /// integration rather than a name invented here. <b>Which provider it is, is not proven</b> — the
    /// flow is named for the mechanic.
    /// </para>
    ///
    /// <para>
    /// This is the multi-variant variant: it opens with <c>FindProductMulti</c> /
    /// <c>AddToCartMulti</c> and includes <c>CalculateTaxes</c>.
    /// </para>
    /// </summary>
    public static readonly Flow StructureTokenMulti = new("structure-token-multi", new[]
    {
        new Step("FindProductMulti", 29), new Step("FindProductFlow", 30),
        new Step("FindVariant", 32), new Step("AddToCartMulti", 33),
        new Step("GetCheckout", 37), new Step("GetMerchantCode", 38),
        new Step("GetShippingRate", 39), new Step("SubmitShipping", 40),
        new Step("CalculateTaxes", 41), new Step("GetStructureToken", 42),
        new Step("CreateTransaction", 43), new Step("SubmitPayment", 44),
        new Step("GetPayPalToken", 45), new Step("SubmitPayPal", 46),
        new Step("ProcessPayment", 47),
    });

    /// <summary>
    /// The same engine in its single-variant shape: twelve steps, opening with <c>EditLine</c> and
    /// carrying <c>GetStructureToken</c> at ordinal 40 instead of 42.
    ///
    /// <para>
    /// Two flows sharing five step names (<c>GetCheckout</c>, <c>GetShippingRate</c>,
    /// <c>SubmitShipping</c>, <c>GetStructureToken</c>, <c>CreateTransaction</c>, <c>SubmitPayment</c>,
    /// <c>GetPayPalToken</c>, <c>SubmitPayPal</c>, <c>ProcessPayment</c>) is not a coincidence: it is
    /// one engine behind two storefronts, and keeping both is how the replica stays honest about them.
    /// </para>
    /// </summary>
    public static readonly Flow StructureTokenSingle = new("structure-token-single", new[]
    {
        new Step("EditLine", 34), new Step("AddToCart", 35), new Step("GetCheckout", 36),
        new Step("GetMerchantCode", 37), new Step("GetShippingRate", 38),
        new Step("SubmitShipping", 39), new Step("GetStructureToken", 40),
        new Step("CreateTransaction", 41), new Step("SubmitPayment", 42),
        new Step("GetPayPalToken", 43), new Step("SubmitPayPal", 44),
        new Step("ProcessPayment", 45),
    });

    /// <summary>
    /// What identifies each unnamed flow, recorded next to it so a later round can name it with
    /// evidence instead of guessing. <b>No brand is claimed.</b>
    /// </summary>
    public static readonly IReadOnlyDictionary<string, string> IdentityEvidence =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["collectplus-app"] =
                "GetCollectPlusLocations + *App steps + GetPaymentUrl — UK click-and-collect store",
            ["structure-token-multi"] =
                "GetMerchantCode + GetStructureToken + CalculateTaxes, multi-variant (FindProductMulti)",
            ["structure-token-single"] =
                "same engine, single-variant (EditLine first), GetStructureToken at ordinal 40",
        };

    /// <summary>All eight flows.</summary>'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "CollectPlusApp" in t:
    print("already present")
else:
    t = t.replace(anchor, add, 1)
    # extend All
    t = t.replace(
        "        Nike, PopMart, JohnLewis, DemandwareClassic, DemandwareDual,",
        "        Nike, PopMart, JohnLewis, DemandwareClassic, DemandwareDual,\n"
        "        CollectPlusApp, StructureTokenMulti, StructureTokenSingle,", 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("three flows added")
