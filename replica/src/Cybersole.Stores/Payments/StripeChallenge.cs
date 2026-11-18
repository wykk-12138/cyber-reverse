using System.Net.Http;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>
/// Stripe's checkout challenge — the confirmation a Stripe payment asks for when its risk engine
/// gates the card behind a captcha, solved end to end from <c>sub_140BE31F0</c> (reached from the
/// frozen <c>Solving Stripe challenge</c> literal at 0x146e94270 = chars 0x146e9427c - 12).
///
/// <para>
/// The state machine reports <c>Submit billing</c> around the step, hangs an <b>orange</b>
/// <c>StatusInfo</c> wall with the <c>Solving Stripe challenge</c> text, awaits the captcha under
/// <c>Waiting for captcha</c>, and on a token PUTs a five-field form to
/// <b>https://api.stripe.com</b> + the per-checkout path the context carries (ctx field 800):
/// </para>
///
/// <code>
///   challenge_response_token  = the captcha token (the awaited payload, ctx 784/792 family)
///   challenge_response_ekey   = ""          (the empty-string sentinel 0x146A622F8)
///   client_secret             = ctx field 728
///   captcha_vendor_name       = "hcaptcha"  (the frozen literal 0x147045DF0)
///   key                       = ctx field 704 (the publishable key)
/// </code>
///
/// <para>
/// A captcha that never arrives reports <c>Stripe challenge captcha failed</c> with the UI colour
/// <c>#FB4961</c> — the image's own colour code, kept verbatim. The send is the +24 verb slot
/// (<c>sub_1408B6310</c>, the same PUT the Nike and PayPal surfaces use), the request DTO is the
/// shared <c>unk_144BDF900</c> and the form body is built by the <c>unk_144CB7DE8</c> encoder.
/// </para>
/// </summary>
public sealed class StripeChallenge
{
    /// <summary>The form target host, a frozen literal (0x147054DD8); the path rides the context.</summary>
    public const string ApiHost = "https://api.stripe.com";

    /// <summary>The wall text (0x146E94270) — an orange wall, unlike PayPal's white one.</summary>
    public const string SolvingStatus = "Solving Stripe challenge";

    /// <summary>The wall kind the registration carries (0x1471099B0).</summary>
    public const string WallKind = "orange";

    /// <summary>The await's own label while the captcha is being solved (0x146F25E60).</summary>
    public const string WaitingForCaptcha = "Waiting for captcha";

    /// <summary>The failure text when no captcha token ever arrives (0x146E9F310).</summary>
    public const string CaptchaFailedStatus = "Stripe challenge captcha failed";

    /// <summary>The failure text's UI colour (0x146A76FD0) — the image's own code, kept verbatim.</summary>
    public const string CaptchaFailedColour = "#FB4961";

    /// <summary>The vendor the form swears by (0x147045DF0) — Stripe's challenge is an hCaptcha gate.</summary>
    public const string CaptchaVendor = "hcaptcha";

    /// <summary>What the confirm step needs — the fields the original reads off its checkout context.</summary>
    public sealed class ChallengeInput
    {
        /// <summary>The solved captcha token; without it the original reports the failed status.</summary>
        public string? CaptchaToken { get; init; }

        /// <summary>client_secret — the payment intent's secret (ctx field 728).</summary>
        public string? ClientSecret { get; init; }

        /// <summary>The publishable key (ctx field 704).</summary>
        public string? PublishableKey { get; init; }

        /// <summary>The per-checkout path after the host (ctx field 800).</summary>
        public string? Path { get; init; }
    }

    /// <summary>What the confirm step reports back.</summary>
    public sealed class ChallengeOutcome
    {
        public bool Ok { get; init; }
        public int Status { get; init; }
        public string? Body { get; init; }
        public string? Error { get; init; }

        public static ChallengeOutcome Success(int status, string? body) =>
            new() { Ok = true, Status = status, Body = body };

        public static ChallengeOutcome Failed(int status) =>
            new() { Status = status, Error = "stripe challenge: HTTP " + status };
    }

    /// <summary>
    /// The five-field form, in the encoder's own order (sub_14130CC50 calls): token, the empty ekey,
    /// the secret, the vendor's name, the key.
    /// </summary>
    public static IReadOnlyDictionary<string, string> Form(ChallengeInput i) => new Dictionary<string, string>
    {
        ["challenge_response_token"] = i.CaptchaToken ?? string.Empty,
        ["challenge_response_ekey"] = string.Empty,
        ["client_secret"] = i.ClientSecret ?? string.Empty,
        ["captcha_vendor_name"] = CaptchaVendor,
        ["key"] = i.PublishableKey ?? string.Empty,
    };

    /// <summary>
    /// The confirm step: orange wall, the captcha-token gate, the form PUT to the stripe host, and
    /// the two reportable ends — the failed status with its colour, or the PUT's answer.
    /// </summary>
    public static async Task<ChallengeOutcome> ConfirmAsync(FlowContext c, ChallengeInput input,
        CancellationToken ct, string? url = null)
    {
        // The wall registration the state machine makes: (text, "orange", "StatusInfo", null).
        c.Emit(SolvingStatus, "StatusInfo");

        // The captcha gate. The original awaits its token under 'Waiting for captcha' and reports
        // the failed status with #FB4961 when nothing arrives; the replica receives the token as an
        // input, so the gate is the same check on what arrived.
        c.Emit(WaitingForCaptcha, "StatusInfo");
        if (string.IsNullOrEmpty(input.CaptchaToken))
        {
            // R1086: Emit's second parameter is the event TYPE (the original reports the failure
            // with its colour, 0x146a76fd0, as part of the message's presentation — kept as the
            // CaptchaFailedColour constant — not as the event's channel).
            c.Emit(CaptchaFailedStatus, "error");
            return ChallengeOutcome.Failed(0);
        }

        var form = Form(input);
        var body = string.Join("&", form.Select(kv =>
            $"{Uri.EscapeDataString(kv.Key)}={Uri.EscapeDataString(kv.Value)}"));

        var options = c.Options("stripe-challenge");
        options.Content = new StringContent(body, System.Text.Encoding.UTF8,
            "application/x-www-form-urlencoded");
        var res = await c.Http.SendAsync(HttpMethod.Put, url ?? ApiHost + (input.Path ?? string.Empty),
            options, ct).ConfigureAwait(false);
        c.Session.AbsorbCookies(res.Cookies);

        return res.StatusCode is >= 200 and < 300
            ? ChallengeOutcome.Success(res.StatusCode, res.Body)
            : ChallengeOutcome.Failed(res.StatusCode);
    }
}
