using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Stores.Flows;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Cybersource Flex — the microform's tokenisation surface, which is how the Casio flow turns a card into
/// a token before it hands anything to Adyen.
///
/// <para>
/// <b>Observed</b>, all frozen literals from the image:
/// <c>https://flex.cybersource.com/flex/v2/tokens</c> (0x147066CCC);
/// <c>https://flex.cybersource.com/cybersource/assets/microform/0.11.8/iframe.html?keyId=</c>
/// (0x147066C0C) and <c>https://flex.cybersource.com/microform/bundle/v2.0.2/iframe.html?keyId=</c>
/// (0x147066D3C) — two generations of the hosted iframe, both present, so a store can be on either;
/// <c>https://api.cybersource.com</c> (0x1470535DC) and <c>api.cybersource.com</c> (0x146F748D4);
/// <c>https://secureacceptance.cybersource.com/silent/embedded/pay</c> (0x14708014C) and its two
/// payer-authentication siblings (0x1470801DC, 0x1470802D4). The Casio class's own metadata carries
/// <c>_flexTokensUrl</c> (0x1433830FE), <c>_captureContext</c> (0x1433831FB) and <c>_cybersource</c>
/// (0x14338320B) beside a <c>GetCaptureContext</c> / <c>Tokenize</c> / <c>GetCardBrand</c> helper trio,
/// and the JSON key <c>cardInfo</c> (0x146FC03B4).
/// </para>
///
/// <para>
/// <b>Inference</b>: the request shape. The image attests the endpoint, the <c>cardInfo</c> key and the
/// capture-context field, but not the members inside <c>cardInfo</c> nor the response's token member, so
/// those follow Cybersource's published Flex v2 contract and are marked as such in
/// <see cref="TokenizeBody"/>. A reader who wants to falsify this should capture one request; nothing here
/// is presented as decompiled.
/// </para>
///
/// <para>
/// <b>Not modelled</b>: acquiring the capture context. <c>_captureContext</c> exists as a field but no
/// literal spells the store endpoint that issues it, so <see cref="TokenizeAsync"/> takes one as an
/// argument instead of inventing where it comes from.
/// </para>
/// </summary>
public static class CybersourceFlex
{
    /// <summary>The Flex v2 token endpoint.</summary>
    public const string TokensUrl = "https://flex.cybersource.com/flex/v2/tokens";

    /// <summary>The 0.11.8 microform iframe, with the key id appended by the caller.</summary>
    public const string MicroformIframeV0118 =
        "https://flex.cybersource.com/cybersource/assets/microform/0.11.8/iframe.html?keyId=";

    /// <summary>The 2.0.2 microform bundle iframe, with the key id appended by the caller.</summary>
    public const string MicroformIframeV202 =
        "https://flex.cybersource.com/microform/bundle/v2.0.2/iframe.html?keyId=";

    /// <summary>The REST host, distinct from the Flex one.</summary>
    public const string ApiHost = "https://api.cybersource.com";

    /// <summary>Secure Acceptance, which is a third surface again — hosted payment pages.</summary>
    public const string SecureAcceptanceHost = "https://secureacceptance.cybersource.com";

    public const string SecureAcceptancePayPath = "/silent/embedded/pay";

    /// <summary>The two payer-authentication entry points, kept apart because they differ by query shape.</summary>
    public const string PayerAuthLoadPath =
        "/silent/embedded/payer_authentication/hybrid?ccaAction=load&sessionid=";

    public const string PayerAuthSessionPath = "/silent/embedded/payer_authentication/hybrid?sessionid=";

    /// <summary>An iframe URL for a key id, on either generation of the microform.</summary>
    public static string MicroformIframeUrl(string keyId, bool bundleV2 = true) =>
        (bundleV2 ? MicroformIframeV202 : MicroformIframeV0118) + Uri.EscapeDataString(keyId ?? string.Empty);

    /// <summary>
    /// The Flex v2 tokenise body.
    ///
    /// <para>
    /// <b>Inference</b>, from Cybersource's published contract rather than from the image: the image
    /// attests only <c>cardInfo</c>. The member names below are the documented ones, and
    /// <c>tokenInformation</c> is sent empty because the response options are defaults.
    /// </para>
    /// </summary>
    public static JObject TokenizeBody(Card? card)
    {
        var info = new JObject
        {
            ["cardNumber"] = Digits(card?.Number),
        };

        if (!string.IsNullOrEmpty(card?.Month)) info["expirationMonth"] = card!.Month;
        if (!string.IsNullOrEmpty(card?.Year)) info["expirationYear"] = card!.Year;
        if (!string.IsNullOrEmpty(card?.Cvv)) info["securityCode"] = card!.Cvv;

        return new JObject
        {
            ["cardInfo"] = info,
            ["tokenInformation"] = new JObject(),
        };
    }

    /// <summary>
    /// Tokenise a card with a capture context, returning the transient token and, when the reply carries
    /// one, the card type — which is what the image's <c>GetCardBrand</c> helper is for.
    ///
    /// <para>
    /// The capture context is the authorisation: Flex v2 expects it as a bearer token, which is
    /// <b>Inference</b> from the published contract. The response members <c>token</c> and
    /// <c>cardType</c> are likewise.
    /// </para>
    /// </summary>
    public static async Task<FlexTokenResult> TokenizeAsync(
        FlowContext c,
        string captureContext,
        CancellationToken ct,
        string? tokensUrl = null)
    {
        if (string.IsNullOrWhiteSpace(captureContext))
            return FlexTokenResult.Fail("cybersource flex: no capture context");

        var card = c.Card;
        if (card?.Number is null) return FlexTokenResult.Fail("cybersource flex: no card");

        // The capture context is the authorisation. RequestOptions carries headers straight into the
        // request, so the bearer goes on the options rather than through a helper that has no header slot.
        var options = c.Options("cybersource-flex-token");
        options.Headers["Authorization"] = "Bearer " + captureContext;
        options.Headers["Accept"] = "application/json";

        var reply = await c.Http
            .PostJsonAsync(tokensUrl ?? TokensUrl, TokenizeBody(card).ToString(Formatting.None), options, ct)
            .ConfigureAwait(false);

        if (reply is null || !reply.IsSuccess) return FlexTokenResult.Fail("cybersource flex: token call failed");

        JObject body;
        try { body = JObject.Parse(reply.Body); }
        catch (JsonException) { return FlexTokenResult.Fail("cybersource flex: reply is not JSON"); }

        var token = body["token"]?.ToString();
        if (string.IsNullOrEmpty(token)) return FlexTokenResult.Fail("cybersource flex: no token in reply");

        return new FlexTokenResult
        {
            Ok = true,
            Token = token!,
            CardType = body["cardType"]?.ToString() ?? string.Empty,
        };
    }

    private static string Digits(string? number) =>
        number is null ? string.Empty : new string(Array.FindAll(number.ToCharArray(), char.IsDigit));
}

/// <summary>What a Flex tokenisation produced.</summary>
public sealed class FlexTokenResult
{
    public bool Ok { get; init; }
    public string Token { get; init; } = string.Empty;
    public string CardType { get; init; } = string.Empty;
    public string Error { get; init; } = string.Empty;

    public static FlexTokenResult Fail(string error) => new() { Ok = false, Error = error };
}
