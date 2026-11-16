using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Dicks Sporting Goods — a store read by part number, gated at the paygate, with an out-of-stock callback the image
/// names.
///
/// <para>
/// R919. Nine literals name it, and they fall into three groups.
/// </para>
///
/// <code>
/// identity   "DICKS" · "DicksSportingGoods" · "Dicks Sporting Goods" · "dsg-ecomm"
/// endpoints  https://www.dickssportinggoods.com/
///            https://api-search.dickssportinggoods.com/catalog-productdetails/v4/byPartNumber/
///            https://payments.dickssportinggoods.com/prod/api/paygate/v2/authorization
///            https://payments.dickssportinggoods.com/prod/api/paygate/v2/threeDSAuthentication
/// behaviour  "_outOfStock(Dicks Sporting Goods"
/// </code>
///
/// <para>
/// Four identity forms is more than a display name and an id: <c>dsg-ecomm</c> looks like the application or channel
/// name a request carries, and <c>DICKS</c> the short tag. This class exposes all four as constants rather than
/// choosing one, because which appears in a request is unknown and guessing would put a wrong value in a header.
/// </para>
///
/// <para>
/// The behaviour literal is the most informative thing recovered: <c>_outOfStock</c> is a closure name, so the original
/// has an out-of-stock callback attached to this store specifically. That is a monitoring concern rather than a
/// checkout one, and it is modelled as one.
/// </para>
///
/// <para>
/// <b>What is missing.</b> There is no cart or checkout path for this store in the recovered inventory — the only
/// endpoints are a product search and a paygate. That is why <see cref="StepSequence"/> lists only what can be run: a
/// store with a paygate but no recovered basket call cannot be taken through a purchase from this evidence, and
/// pretending otherwise would be a sequence of steps that fail at the second one.
/// </para>
/// </summary>
public sealed class DicksSportingGoodsFlow : StoreFlow
{
    public override string Id => "dickssportinggoods";
    public override string Name => "Dicks Sporting Goods";

    public override IReadOnlyList<string> Domains => new[] { "www.dickssportinggoods.com", "api-search.dickssportinggoods.com", "payments.dickssportinggoods.com" };

    // ── identity, in all four recovered forms ─────────────────────────────────
    internal const string ShortTag = "DICKS";
    internal const string IdForm = "DicksSportingGoods";
    internal const string DisplayName = "Dicks Sporting Goods";
    internal const string Channel = "dsg-ecomm";

    // ── endpoints ─────────────────────────────────────────────────────────────
    internal const string StorefrontHost = "https://www.dickssportinggoods.com";
    internal const string SearchHost = "https://api-search.dickssportinggoods.com";
    internal const string PayHost = "https://payments.dickssportinggoods.com";

    internal const string ByPartNumber = "/catalog-productdetails/v4/byPartNumber/";
    internal const string PayAuthorize = "/prod/api/paygate/v2/authorization";
    internal const string PayThreeDs = "/prod/api/paygate/v2/threeDSAuthentication";

    internal const int RecoveredAddressCount = 4;

    /// <summary>
    /// Two steps. The busiest store still needs a cart call before an order, and this one has none recovered, so the
    /// sequence stops where the evidence does.
    /// </summary>
    public override IReadOnlyList<string> StepSequence => new[] { "FindProduct", "SubmitPayment" };

    /// <summary>
    /// The product lookup is by part number rather than by URL: <c>byPartNumber/</c> is the whole path segment after
    /// the version. A flow that fetched the product page would be reading a different endpoint from the one the image
    /// names.
    /// </summary>
    public override async Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct)
    {
        var part = c.Session.Vars.TryGetValue("partNumber", out var p) && !string.IsNullOrWhiteSpace(p)
            ? p
            : PartNumberFrom(c.Url);

        if (string.IsNullOrEmpty(part))
            return StepOutcome.Fail("dickssportinggoods FindProduct has no part number in the url or session");

        var res = await GetAsync(c, SearchHost + ByPartNumber + Uri.EscapeDataString(part),
            "dsg-product", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("dsg search host unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"dsg product HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["raw"] = res.Body;

        // _outOfStock is the behaviour the image names for this store, so availability is read here rather than left
        // to a later step guessing from a status code
        var outOfStock = Regex.IsMatch(res.Body, @"""inStock""\s*:\s*false|""availability""\s*:\s*""OutOfStock""",
            RegexOptions.IgnoreCase);
        c.Session.Vars["available"] = outOfStock ? "false" : "true";
        if (outOfStock) c.Session.Vars["_outOfStock"] = DisplayName;

        c.Session.Vars["product"] = Regex.Match(res.Body, @"""name""\s*:\s*""([^""]+)""").Groups[1].Value;
        return StepOutcome.Success();
    }

    /// <summary>
    /// Authorization, then 3-D Secure when the answer asks for it. The two paygate calls are separate in the image and
    /// kept separate here: a flow that always ran the second would authenticate orders that needed no authentication.
    /// </summary>
    public override async Task<StepOutcome> SubmitPaymentAsync(FlowContext c, CancellationToken ct)
    {
        var authorize = new JObject { ["channel"] = Channel };
        var res = await PostJsonAsync(c, PayHost + PayAuthorize,
            authorize.ToString(Newtonsoft.Json.Formatting.None), "dsg-authorize", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("dsg paygate unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"dsg authorize HTTP {res.StatusCode}", retryable: true);

        c.Session.Vars["dsg.authorize"] = res.Body;

        // only when the authorisation itself says authentication is required
        if (!Regex.IsMatch(res.Body, @"""(?:requires?3DS|threeDSRequired|challengeRequired)""\s*:\s*true",
                RegexOptions.IgnoreCase))
            return StepOutcome.Success();

        var ds = await PostJsonAsync(c, PayHost + PayThreeDs,
            new JObject { ["authorization"] = res.Body }.ToString(Newtonsoft.Json.Formatting.None),
            "dsg-3ds", ct).ConfigureAwait(false);

        if (ds is null) return StepOutcome.Fail("dsg 3DS unreachable", retryable: true);
        if (!ds.IsSuccess) return StepOutcome.Fail($"dsg 3DS HTTP {ds.StatusCode}", retryable: true);

        c.Session.Vars["dsg.threeDs"] = ds.Body;
        return StepOutcome.Success();
    }

    /// <summary>
    /// A part number out of a product URL. The image reads this store by part number, so a URL carrying one is the
    /// natural source when the session has none.
    /// </summary>
    internal static string PartNumberFrom(string url)
    {
        var m = Regex.Match(url, @"(?:/p/|partNumber[=/])([A-Za-z0-9\-]{3,})", RegexOptions.IgnoreCase);
        return m.Success ? m.Groups[1].Value : string.Empty;
    }
}