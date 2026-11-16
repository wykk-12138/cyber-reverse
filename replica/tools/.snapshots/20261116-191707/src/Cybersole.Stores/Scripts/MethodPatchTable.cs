using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Every <c>method(target, name, build)</c> site in the capture, recorded as a table (R178).
///
/// <para>
/// Thirty-four distinct sites, found by scanning the pool for the call shape. Reading them as a list is what makes the
/// scope of the injection visible: it is not a navigator patch with extras — it reaches <c>Function.prototype.bind</c>,
/// <c>JSON.stringify</c>, <c>Reflect.ownKeys</c>, four <c>Date.prototype</c> methods, six canvas methods, three WebGL
/// methods, five audio entry points, <c>StorageManager.estimate</c> and <c>getComputedStyle</c>.
/// </para>
///
/// <para>
/// The table is deliberately a <b>record</b>, not an implementation plan: it says which sites exist and which of them
/// this workspace has built, so the gap is a number rather than an impression. <see cref="Implemented"/> lists what
/// exists today.
/// </para>
/// </summary>
public static class MethodPatchTable
{
    /// <summary>One patch site: the object it lands on, the name, and a one-line statement of what the patch does.</summary>
    public sealed record Site(string Target, string Name, string Behaviour);

    /// <summary>The thirty-four sites, in the order the pool lists them.</summary>
    public static readonly IReadOnlyList<Site> Sites = new[]
    {
        new Site("Function.prototype", "bind", "patches the bound function's name and arity to match the original"),
        new Site("JSON", "stringify", "so a serialised navigator member answers what the device answers"),
        new Site("Reflect", "ownKeys", "keeps the enumerated key order the device reports"),
        new Site("Document.prototype", "createEvent", "the event object a feature probe asks for"),
        new Site("window", "matchMedia", "matches the query against the claimed device's media features"),
        new Site("WebGLRenderingContext.prototype", "getParameter", "the twelve parameters a fingerprint reads"),
        new Site("WebGLRenderingContext.prototype", "getSupportedExtensions", "the extension list of the claimed device"),
        new Site("WebGLRenderingContext.prototype", "getContextAttributes", "alpha/antialias/depth/stencil values"),
        new Site("WebGLRenderingContext.prototype", "getShaderPrecisionFormat", "precision triplets"),
        new Site("HTMLCanvasElement.prototype", "getContext", "the context handed to the page"),
        new Site("CanvasRenderingContext2D.prototype", "measureText", "a width consistent with the claimed font stack"),
        new Site("CanvasRenderingContext2D.prototype", "fillRect", "the pixels a canvas hash reads"),
        new Site("CanvasRenderingContext2D.prototype", "arc", "the same, for path drawing"),
        new Site("HTMLCanvasElement.prototype", "toDataURL", "a stable data URL for a given drawing"),
        new Site("CanvasRenderingContext2D.prototype", "getImageData", "the pixel buffer a hash reads"),
        new Site("AudioBuffer.prototype", "getChannelData", "the samples an audio fingerprint reads"),
        new Site("Performance.prototype", "now", "a monotonic clock consistent with the claimed engine"),
        new Site("Date.prototype", "toJSON", "the serialised date"),
        new Site("HTMLAudioElement.prototype", "canPlayType", "the codec list of the claimed device"),
        new Site("HTMLVideoElement.prototype", "canPlayType", "the same for video"),
        new Site("MediaRecorder", "isTypeSupported", "the recorder mime list"),
        new Site("StorageManager.prototype", "estimate", "quota and usage figures"),
        new Site("Window.prototype", "getComputedStyle", "the resolved style a layout probe reads"),
        new Site("Intl.DateTimeFormat.prototype", "resolvedOptions", "the locale quartet"),
        new Site("Date.prototype", "getTimezoneOffset", "the timezone offset of the claimed device"),
        new Site("Date.prototype", "toDateString", "the fixed-locale date string"),
        new Site("Date.prototype", "toTimeString", "the fixed-locale time string"),
        new Site("Date.prototype", "toString", "the full date string"),
        new Site("DateProxy", "getYear", "the legacy accessor"),
        new Site("DateProxy", "getTimezoneOffset", "the same offset through the proxy"),
        new Site("DateProxy", "setYear", "the legacy setter"),
        new Site("Date", "parse", "parsing under the fixed locale"),
        new Site("SpeechSynthesis", "getVoices", "the voice list of the claimed device"),
        new Site("SpeechSynthesisVoice", "voiceURI", "the voice's identity string"),
    };

    /// <summary>The sites this workspace implements today, by <c>Target.Name</c>.</summary>
    public static readonly IReadOnlyList<string> Implemented = new[]
    {
        "Document.prototype.createEvent",
        "SpeechSynthesis.getVoices",
        "CanvasRenderingContext2D.prototype.measureText",
        "CanvasRenderingContext2D.prototype.fillRect",
        "CanvasRenderingContext2D.prototype.arc",
        "HTMLCanvasElement.prototype.toDataURL",
        "CanvasRenderingContext2D.prototype.getImageData",
        "WebGLRenderingContext.prototype.getParameter",
        "Date.prototype.getTimezoneOffset",
        "Date.prototype.toString",
        "Date.prototype.toDateString",
        "Date.prototype.toTimeString",
        "Intl.DateTimeFormat.prototype.resolvedOptions",
    };

    /// <summary>The gap, by name, so "how much is left" is a list and not a feeling.</summary>
    public static IReadOnlyList<string> Missing => Sites
        .Select(s => s.Target + "." + s.Name)
        .Where(n => !Implemented.Contains(n))
        .ToList();

    /// <summary>Counts by area, which is how the work gets ordered.</summary>
    public static IReadOnlyDictionary<string, int> ByArea()
    {
        bool Canvas(Site s) => s.Target.Contains("Canvas", System.StringComparison.Ordinal);
        bool Webgl(Site s) => s.Target.Contains("WebGL", System.StringComparison.Ordinal);
        bool Audio(Site s) => s.Target.Contains("Audio", System.StringComparison.Ordinal);
        bool DateIntl(Site s) => s.Target.Contains("Date", System.StringComparison.Ordinal)
                                 || s.Target.Contains("Intl", System.StringComparison.Ordinal);
        bool Core(Site s) => s.Target is "Function.prototype" or "JSON" or "Reflect";

        var known = Sites.Where(s => Canvas(s) || Webgl(s) || Audio(s) || DateIntl(s) || Core(s)).Count();

        return new Dictionary<string, int>
        {
            ["canvas"] = Sites.Count(Canvas),
            ["webgl"] = Sites.Count(Webgl),
            ["audio"] = Sites.Count(Audio),
            ["date-intl"] = Sites.Count(DateIntl),
            ["core"] = Sites.Count(Core),
            // whatever the five names above do not claim, so the areas always add up to the table (R178: the first
            // version summed to 25 of 34 and the assertion said so, which is the point of asserting a sum)
            ["other"] = Sites.Count - known,
        };
    }

    /// <summary>What the list itself says.</summary>
    public const string Rule =
        "the injection is not a navigator patch with extras: it reaches bind, JSON.stringify, Reflect.ownKeys, four "
        + "Date methods, six canvas methods, three WebGL methods and five audio entry points";
}
