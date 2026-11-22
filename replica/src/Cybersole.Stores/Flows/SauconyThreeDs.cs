using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Saucony's 3DS answer, as <c>sub_140A76F60</c> reads it.
///
/// <para>
/// <b>Observed</b> (R1375): that function's nine literals are <c>MD</c>, <c>SAUCONY-3DS</c>, <c>StatusInfo</c>,
/// "Unexpected 3DS response", <c>error</c>, <c>jwt</c>, <c>red</c>, <c>redirectUrl</c> and <c>stepUpUrl</c>. So a
/// reply carries one of two urls — a redirect or a step-up — with a jwt beside them and the MD field 3DS uses, and
/// anything else is answered with the handler's own sentence.
/// </para>
///
/// <para>
/// <b>Not observed:</b> the API paths the payer form posts to. This class therefore reads replies and never invents a
/// request.
/// </para>
/// </summary>
public static class SauconyThreeDs
{
    /// <summary>The step name the image carries.</summary>
    public const string StepName = "SAUCONY-3DS";

    /// <summary>The 3DS message field.</summary>
    public const string MdField = "MD";

    /// <summary>The token field.</summary>
    public const string JwtField = "jwt";

    /// <summary>The redirect field.</summary>
    public const string RedirectUrlField = "redirectUrl";

    /// <summary>The step-up field.</summary>
    public const string StepUpUrlField = "stepUpUrl";

    /// <summary>The handler's words when the reply is neither shape.</summary>
    public const string UnexpectedResponseMessage = "Unexpected 3DS response";

    /// <summary>What a reply turned out to be.</summary>
    public enum Shape
    {
        /// <summary>A redirect to follow.</summary>
        Redirect,

        /// <summary>A step-up challenge to answer.</summary>
        StepUp,

        /// <summary>Neither shape — the handler's own refusal.</summary>
        Unexpected,
    }

    /// <summary>
    /// Classify a reply. The redirect is checked first: when a reply carries both, following it is what the browser
    /// would do, and the step-up url is then redundant rather than competing.
    /// </summary>
    public static (Shape Shape, string? Url, string? Jwt) Classify(JObject? reply)
    {
        if (reply is null) return (Shape.Unexpected, null, null);

        var source = reply["data"] as JObject ?? reply;
        var jwt = source[JwtField]?.ToString();

        var redirect = source[RedirectUrlField]?.ToString();
        if (!string.IsNullOrEmpty(redirect)) return (Shape.Redirect, redirect, jwt);

        var stepUp = source[StepUpUrlField]?.ToString();
        if (!string.IsNullOrEmpty(stepUp)) return (Shape.StepUp, stepUp, jwt);

        return (Shape.Unexpected, null, jwt);
    }
}
