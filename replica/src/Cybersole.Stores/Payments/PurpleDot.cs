using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Purple Dot — a preorder service, and the only vendor in the inventory whose API key is in the binary.
///
/// <para>
/// R920. One literal names it, and it carries three facts at once:
/// </para>
///
/// <code>
/// https://www.purpledotprice.com/api/v1/products/preorder-state?api_key=c114b1fe-63fa-4216-9d7c-07a87697fccd&handle=
/// </code>
///
/// <para>
/// The host, a preorder-state endpoint, and a key. Purple Dot sells preorder and back-in-stock handling to shops, so
/// this is not a storefront: a flow asks it whether a given product handle is on preorder, and a monitor that treats a
/// preorder as in-stock will try to buy something that ships months later. That is why it belongs beside the payment
/// gateways rather than among the stores.
/// </para>
///
/// <para>
/// <b>The key.</b> It is a literal in the binary, so it is recorded as recovered rather than invented, and it is a
/// third-party service key that the original ships. Whether it is per-install or a shared public key is not knowable
/// from one string; what is knowable is that the original sends it in a query string rather than a header, and this
/// class does the same so a request matches the shape the image implies.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The response shape. Nothing describes what <c>preorder-state</c> returns, so the reader
/// below looks for the field names a state endpoint would plausibly use and treats their absence as unknown rather
/// than as "not a preorder" — a monitor that guessed "no" on an unreadable answer would buy a preorder.
/// </para>
/// </summary>
public static class PurpleDot
{
    internal const string Host = "https://www.purpledotprice.com";
    internal const string PreorderState = "/api/v1/products/preorder-state";

    /// <summary>
    /// The key as it appears in the binary. Recovered, not invented; see the class note on what its scope is not.
    /// </summary>
    internal const string ApiKey = "c114b1fe-63fa-4216-9d7c-07a87697fccd";

    /// <summary>True when a session recorded a preorder state at all, as distinct from what it recorded.</summary>
    public const string StateVar = "purpledot.state";

    /// <summary>Builds the request URL for a product handle. Exposed so a test can pin the shape without a network.</summary>
    public static string UrlFor(string handle) =>
        Host + PreorderState + "?api_key=" + Uri.EscapeDataString(ApiKey) + "&handle=" + Uri.EscapeDataString(handle ?? string.Empty);

    /// <summary>
    /// Asks whether a handle is on preorder.
    ///
    /// <para>
    /// Three outcomes, and the third is the one that matters: an unreadable answer leaves the state unset, so a caller
    /// must decide what to do rather than being told "not a preorder" by a default.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> QueryAsync(FlowSession session, string handle, CancellationToken ct,
        Func<string, CancellationToken, Task<NetResponse?>> get)
    {
        if (string.IsNullOrWhiteSpace(handle))
            return StepOutcome.Fail("PurpleDot needs a product handle and none was given");

        var res = await get(UrlFor(handle), ct).ConfigureAwait(false);
        if (res is null) return StepOutcome.Fail("purpledotprice unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"purpledotprice HTTP {res.StatusCode}", retryable: true);

        session.Vars["purpledot.body"] = res.Body;

        // R920: false has to be part of the alternation. The first version accepted only true or a string, so an answer
        // saying {"isPreorder":false} fell through to the unrecognised branch and left the state unset -- which is the
        // safe direction to fail but also means the common case could never succeed.
        var on = Regex.Match(res.Body, @"""(?:isPreorder|preorder|onPreorder|preorderState)""\s*:\s*(true|false|""[^""]*"")",
            RegexOptions.IgnoreCase);
        if (!on.Success)
            return StepOutcome.Fail("purpledotprice answered in a shape this does not recognise; state left unset");

        var raw = on.Groups[1].Value.Trim('"');
        session.Vars[StateVar] = raw.Equals("true", StringComparison.OrdinalIgnoreCase) ? "preorder" : "in-stock";
        return StepOutcome.Success();
    }

    /// <summary>
    /// The decision a monitor needs, phrased so the unknown case cannot be mistaken for a purchase signal.
    /// </summary>
    public static bool IsBuyable(FlowSession session) =>
        session.Vars.TryGetValue(StateVar, out var s) && s == "in-stock";
}