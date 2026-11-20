namespace Cybersole.Stores.Flows;

/// <summary>
/// The four challenge surfaces the image carries as complete solver pages, and how a page is recognised as one.
///
/// <para>
/// These are not guesses: the artifact embeds the HTML the solver loads, and each block names its own loader script.
/// The literals below are copied out of those blocks verbatim —
/// </para>
///
/// <code>
/// 143ca6a9f  reCAPTCHA v2 checkpoint   document.Solver.Captcha.Type === 0 -> document.Solver.Recaptcha()
///                                     : 1 -> grecaptcha.execute()          <- the Type field's meaning
/// 143ca8507  reCAPTCHA Enterprise     https://www.google.com/recaptcha/enterprise.js?render=%sitekey%
///                                     grecaptcha.enterprise.execute(Captcha.Sitekey, { action: Captcha.Action })
/// 143cb2699  Cloudflare Turnstile     https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback
///                                     turnstile.render("#captcha", { sitekey, callback, 'before-interactive-callback' })
/// 147153cf4  hCaptcha (invisible)     script[src*='js.hcaptcha.com/1/api.js']
/// 146ab71b4  reCAPTCHA v2 anchor      /recaptcha/api2/anchor
/// </code>
///
/// <para>
/// Every one of the four reports its token through the same bridge — <c>document.Solver.Captcha.Solve(token)</c> — which
/// is why one classifier can serve all of them: what differs is the loader, not the return path.
/// </para>
/// </summary>
public static class CaptchaSurface
{
    /// <summary>The hCaptcha loader, as the image's own selector spells it (147153cf4).</summary>
    public const string HCaptchaSelector = "script[src*='js.hcaptcha.com/1/api.js']";

    /// <summary>The hCaptcha script host (1470ad964).</summary>
    public const string HCaptchaHost = "js.hcaptcha.com";

    /// <summary>The Turnstile loader, verbatim from the solver page (143cb2699).</summary>
    public const string TurnstileLoader =
        "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback";

    /// <summary>The Enterprise loader, with the image's own <c>%sitekey%</c> placeholder intact (143ca8507).</summary>
    public const string EnterpriseLoader =
        "https://www.google.com/recaptcha/enterprise.js?render=%sitekey%";

    /// <summary>The reCAPTCHA v2 anchor path (146ab71b4).</summary>
    public const string RecaptchaAnchorPath = "/recaptcha/api2/anchor";

    /// <summary>
    /// What a page is asking for, read from the loader it names.
    ///
    /// <para>
    /// Order matters: an Enterprise page also mentions <c>grecaptcha</c>, so the specific loaders are tested before the
    /// generic ones. The result is one of <c>hcaptcha</c>, <c>turnstile</c>, <c>recaptcha-enterprise</c>,
    /// <c>recaptcha-v2</c>, <c>recaptcha-v3</c> or <c>none</c>.
    /// </para>
    /// </summary>
    public static string Classify(string? body)
    {
        if (string.IsNullOrEmpty(body)) return "none";

        if (body.Contains("js.hcaptcha.com", System.StringComparison.OrdinalIgnoreCase))
            return "hcaptcha";
        if (body.Contains("challenges.cloudflare.com/turnstile", System.StringComparison.OrdinalIgnoreCase))
            return "turnstile";
        if (body.Contains("recaptcha/enterprise.js", System.StringComparison.OrdinalIgnoreCase))
            return "recaptcha-enterprise";
        if (body.Contains(RecaptchaAnchorPath, System.StringComparison.Ordinal))
            return "recaptcha-v2";
        // v3 is the branch the image reaches without a checkbox: grecaptcha.execute() rather than a rendered anchor
        if (body.Contains("grecaptcha.execute", System.StringComparison.OrdinalIgnoreCase))
            return "recaptcha-v3";

        return "none";
    }

    /// <summary>
    /// The <c>Captcha.Type</c> values the checkpoint page switches on (143ca6a9f): 0 is the interactive checkbox it
    /// clicks, 1 is the invisible execute. Stated here because the page is the only place the field's meaning appears.
    /// </summary>
    public const int TypeInteractive = 0;

    /// <inheritdoc cref="TypeInteractive"/>
    public const int TypeInvisibleExecute = 1;

    /// <summary>True when the type needs a click before the token can be produced.</summary>
    public static bool NeedsClick(int captchaType) => captchaType == TypeInteractive;
}
