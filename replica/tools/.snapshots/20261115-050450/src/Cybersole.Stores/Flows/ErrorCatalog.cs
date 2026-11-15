namespace Cybersole.Stores.Flows;

/// <summary>
/// The error catalogue the live 5.18.32 build shows under Settings → Need Help?.
///
/// Every entry below was read off the running window (docs/GUI_BASELINE.md). The wording is
/// part of the product surface — a user comparing the two builds should see the same
/// explanation for the same failure — so the strings are reproduced verbatim, typos included
/// ("a unrecoverable error" is the original).
///
/// The keys are stable ids for the replica's own classification; the tags in brackets
/// (<c>[General]</c>, <c>[Shopify]</c>, <c>[Footsites]</c>) are how the UI groups them.
/// </summary>
public static class ErrorCatalog
{
    public sealed record Entry(string Id, string Tag, string Title, string Detail);

    public static IReadOnlyList<Entry> All { get; } = new[]
    {
        // ---- General ----------------------------------------------------------------
        new Entry("general.connection", "General", "[General] Connection Error",
            "Target website unreachable or your proxies are currently not working."),

        new Entry("general.notfound", "General", "[General] Not found",
            "Response code indicates that the server can't find the requested resource."),

        new Entry("general.unavailable", "General", "[General] Service Unavailable",
            "Response code indicates that the server is not ready to handle the request."),

        new Entry("general.ratelimit", "General", "[General] Rate Limit",
            "Response status code indicates the user has sent too many requests in a given " +
            "amount of time (\"rate limiting\")."),

        new Entry("general.forbidden", "General", "[General] Forbidden",
            "Response status code indicates that the server understood the request but " +
            "refuses to authorize it."),

        new Entry("general.taskfailed", "General", "[General] Task failed",
            "The task hit a unrecoverable error. Please make sure that it's configured " +
            "properly and that all profile data is filled in and correct."),

        // ---- Shopify ----------------------------------------------------------------
        new Entry("shopify.shipping.handle", "Shopify",
            "[Shopify] Error Submitting Shipping (Handle Error)",
            "This is caused by starting your Safe Preload tasks too early, which causes you " +
            "to get requeued."),

        new Entry("shopify.order.ratelimit", "Shopify",
            "[Shopify] Error Submitting Order (Rate Limit)",
            "This means you were detected by antibot. This normally happens mainly if you are " +
            "running Fast Mode on a site with antibot, however sometimes Shopify makes changes " +
            "that will cause everyone to run into this until we push a fix."),

        new Entry("shopify.payment", "Shopify", "[Shopify] Payment Error",
            "This usually means that the item went out of stock on processing."),

        new Entry("shopify.connection", "Shopify", "[Shopify] Connection Errors",
            "Your proxies are randomly disconnecting/having issues connecting to the site. " +
            "This can also happen if you have not authenticated your IP for your IP auth proxies."),

        new Entry("shopify.shipping.hang", "Shopify",
            "[Shopify] Tasks hanging on \"Getting Shipping Rates\"",
            "This usually means that the site you are trying for does not ship to you and has " +
            "region locked it to the state that their store is."),

        new Entry("shopify.card.invalid", "Shopify",
            "[Shopify] Invalid Credit Card Number/Billing",
            "Your credit card number/billing is invalid or Shopify is returning that from " +
            "their end. It is not bot related."),

        // ---- Footsites --------------------------------------------------------------
        new Entry("footsites.ratelimit", "Footsites", "[Footsites] Rate Limit / 429",
            "Status code used for a multitude of errors. Ranging from product blocks to " +
            "IP / ASN blacklist."),
    };

    /// <summary>Entries for one bracket tag, in catalogue order.</summary>
    public static IEnumerable<Entry> Tagged(string tag) =>
        All.Where(e => string.Equals(e.Tag, tag, StringComparison.OrdinalIgnoreCase));

    /// <summary>Lookup by id; null when the id is not in the catalogue.</summary>
    public static Entry? ById(string id) =>
        All.FirstOrDefault(e => string.Equals(e.Id, id, StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// Map an HTTP status plus the request stage onto a catalogue entry. This is the
    /// classification the replica uses when a step fails, so the surfaced reason matches what
    /// the original would say for the same shape of failure.
    /// </summary>
    public static Entry Classify(int statusCode, StepStage stage, bool blocked = false)
    {
        if (blocked && stage is StepStage.SubmitOrder)
            return ById("shopify.order.ratelimit")!;

        if (statusCode == 403) return ById("general.forbidden")!;
        if (statusCode == 404) return ById("general.notfound")!;
        if (statusCode == 429)
            return stage is StepStage.SubmitShipping or StepStage.SubmitOrder
                ? ById("footsites.ratelimit")!
                : ById("general.ratelimit")!;
        if (statusCode is 502 or 503 or 504) return ById("general.unavailable")!;
        if (statusCode == 0) return ById("general.connection")!;

        return stage switch
        {
            StepStage.SubmitShipping => ById("shopify.shipping.handle")!,
            StepStage.SubmitPayment => ById("shopify.payment")!,
            StepStage.SubmitOrder => ById("general.taskfailed")!,
            _ => ById("general.taskfailed")!,
        };
    }
}

/// <summary>Which step a failure came from, for <see cref="ErrorCatalog.Classify"/>.</summary>
public enum StepStage
{
    Monitor,
    FindProduct,
    FindVariant,
    AddToCart,
    GetCart,
    GetCheckout,
    SubmitShipping,
    SubmitPayment,
    SubmitOrder,
}
