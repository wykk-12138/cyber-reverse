using System.Collections.Generic;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The eight-field browser fingerprint the image carries, read out in R130 — the model the profile
/// generator materialises for each new Chrome profile.
///
/// <para>
/// The evidence is one metadata run in the string pool, which lists the class's backing fields in
/// order, plus the setters that precede it:
/// </para>
///
/// <code>
/// &lt;ColorDepth&gt;k__BackingField            &lt;DeviceMemory&gt;k__BackingField
/// &lt;HardwareConcurrency&gt;k__BackingField   &lt;PixelRatio&gt;k__BackingField
/// &lt;ScreenWidth&gt;k__BackingField           &lt;ScreenHeight&gt;k__BackingField
/// &lt;AvailableScreenWidth&gt;k__BackingField   &lt;AvailableScreenHeight&gt;k__BackingField
/// </code>
///
/// <para>
/// Beside it sit <c>Fingerprint.template.json</c>, <c>Fingerprint</c>, the Chromium switches
/// <c>--profile-directory=</c> / <c>user-data-dir</c>, and numbered profile folders
/// (<c>Profile 0</c>, <c>Profile 1</c>, <c>Profile 6</c>, <c>Profile 8</c>). Together that is the
/// mechanism: <b>a template is filled per profile, and every profile is its own Chrome identity</b>.
/// The values below are the shape; the template supplies the population.
/// </para>
///
/// <para>
/// The replica used to hardcode two of these (<c>hardwareConcurrency = 8</c>,
/// <c>deviceMemory = 8</c>) for every run, and never set the six screen fields at all — which is the
/// one thing a fingerprint check notices first, because two sessions from the same install then
/// report identical hardware.
/// </para>
/// </summary>
public sealed record BrowserFingerprint
{
    /// <summary>The template file the image ships.</summary>
    public const string TemplateFile = "Fingerprint.template.json";

    /// <summary>A window size the image passes to Chromium, kept as an observed sample.</summary>
    public const string ObservedWindowSize = "--window-size=363,684";

    public int ColorDepth { get; init; } = 24;
    public int DeviceMemory { get; init; } = 8;
    public int HardwareConcurrency { get; init; } = 8;
    public double PixelRatio { get; init; } = 1;
    public int ScreenWidth { get; init; } = 1920;
    public int ScreenHeight { get; init; } = 1080;
    public int AvailableScreenWidth { get; init; } = 1920;
    public int AvailableScreenHeight { get; init; } = 1040;

    /// <summary>The field names, in the order the image lists them.</summary>
    public static readonly IReadOnlyList<string> Fields = new[]
    {
        "ColorDepth", "DeviceMemory", "HardwareConcurrency", "PixelRatio",
        "ScreenWidth", "ScreenHeight", "AvailableScreenWidth", "AvailableScreenHeight",
    };

    /// <summary>
    /// The screen sizes a template can draw from. Four real configurations rather than a random
    /// integer, because a 1373-wide screen with 1920 available is itself a tell.
    /// </summary>
    public static readonly IReadOnlyList<(int Width, int Height, int AvailWidth, int AvailHeight)> Screens =
        new[]
        {
            (1920, 1080, 1920, 1040),
            (1536, 864, 1536, 824),
            (1440, 900, 1440, 860),
            (1366, 768, 1366, 728),
        };

    /// <summary>The hardware hints a template can draw from.</summary>
    public static readonly IReadOnlyList<(int Cores, int Memory)> Hardware = new[]
    {
        (4, 4), (8, 8), (12, 8), (16, 16),
    };

    /// <summary>
    /// A fingerprint that is <b>stable per profile and different across profiles</b>.
    ///
    /// <para>
    /// Deterministic on the profile key, because a fingerprint that changes between two requests from
    /// the same profile is worse than no fingerprint at all — it is the pattern a bot wall looks for.
    /// Two different profiles get different screens and hardware.
    /// </para>
    /// </summary>
    public static BrowserFingerprint ForProfile(string profileKey)
    {
        var hash = StableHash(profileKey);
        var screen = Screens[(int)(hash % (uint)Screens.Count)];
        var hardware = Hardware[(int)((hash / 7) % (uint)Hardware.Count)];
        var ratio = (hash & 0x1) == 0 ? 1.0 : 1.25;

        return new BrowserFingerprint
        {
            ColorDepth = 24,
            DeviceMemory = hardware.Memory,
            HardwareConcurrency = hardware.Cores,
            PixelRatio = ratio,
            ScreenWidth = screen.Width,
            ScreenHeight = screen.Height,
            AvailableScreenWidth = screen.AvailWidth,
            AvailableScreenHeight = screen.AvailHeight,
        };
    }

    /// <summary>FNV-1a — stable across runs, unlike <see cref="string.GetHashCode()"/>.</summary>
    private static uint StableHash(string value)
    {
        unchecked
        {
            var hash = 2166136261u;
            foreach (var ch in value)
            {
                hash ^= ch;
                hash *= 16777619u;
            }
            return hash;
        }
    }

    /// <summary>
    /// The JavaScript that applies all eight fields, for injection before any page script runs.
    ///
    /// <para>
    /// Every field is set with a getter that reports the profile's value, and the screen object is
    /// patched rather than replaced so that <c>screen.orientation</c> and the rest keep working.
    /// </para>
    /// </summary>
    public string ToJavaScript()
    {
        var ratio = PixelRatio.ToString(System.Globalization.CultureInfo.InvariantCulture);

        // A raw interpolated string with doubled braces is unreadable here; plain concatenation keeps
        // the JavaScript visible and avoids the CS9006 brace-count rule entirely.
        var js = string.Empty;
        js += "(function () {\n";
        js += "  try {\n";
        js += "    const N = Navigator.prototype;\n";
        js += "    Object.defineProperty(N, 'hardwareConcurrency', { get: () => " + HardwareConcurrency + ", configurable: true });\n";
        js += "    Object.defineProperty(N, 'deviceMemory', { get: () => " + DeviceMemory + ", configurable: true });\n";
        js += "    Object.defineProperty(N, 'maxTouchPoints', { get: () => 0, configurable: true });\n";
        js += "    Object.defineProperty(window, 'devicePixelRatio', { get: () => " + ratio + ", configurable: true });\n";
        js += "    const S = Screen.prototype;\n";
        js += "    Object.defineProperty(S, 'width', { get: () => " + ScreenWidth + ", configurable: true });\n";
        js += "    Object.defineProperty(S, 'height', { get: () => " + ScreenHeight + ", configurable: true });\n";
        js += "    Object.defineProperty(S, 'availWidth', { get: () => " + AvailableScreenWidth + ", configurable: true });\n";
        js += "    Object.defineProperty(S, 'availHeight', { get: () => " + AvailableScreenHeight + ", configurable: true });\n";
        js += "    Object.defineProperty(S, 'colorDepth', { get: () => " + ColorDepth + ", configurable: true });\n";
        js += "    Object.defineProperty(S, 'pixelDepth', { get: () => " + ColorDepth + ", configurable: true });\n";
        js += "  } catch (e) {}\n";
        js += "})();\n";
        return js;
    }

    /// <summary>
    /// The Chrome profile-directory name, from the numbered folders the image ships
    /// (<c>Profile 0</c>, <c>Profile 1</c>, <c>Profile 6</c>, <c>Profile 8</c>).
    ///
    /// <para>
    /// A persistent user-data-dir holds several <c>Profile N</c> folders, and Chromium is told which
    /// one to use with <c>--profile-directory=</c>. Deriving the number from the profile key keeps one
    /// profile key on one directory across restarts — the folder and the fingerprint then describe the
    /// same identity.
    /// </para>
    /// </summary>
    public string ProfileDirectoryName(string profileKey) =>
        "Profile " + (StableHash(profileKey) % 9);

    /// <summary>The switch Chromium takes for that directory.</summary>
    public string ProfileDirectoryArgument(string profileKey) =>
        "--profile-directory=" + ProfileDirectoryName(profileKey);

    /// <summary>The window size argument for this fingerprint's screen.</summary>
    public string WindowSizeArgument() => $"--window-size={ScreenWidth - 120},{ScreenHeight - 200}";

    /// <summary>
    /// The launch size that matches the profile's claim.
    ///
    /// <para>
    /// R150: an Apple profile says its screen is 402×874 and its outer window is 402×874. Launching the
    /// browser at the desktop size instead makes <c>outerHeight</c> report the host's height, which the
    /// image's own comment calls out as the worse of two impossibilities — "the host window must actually
    /// be this size or clicks land outside the viewport we claim". So the launch size follows the user
    /// agent the profile will send.
    /// </para>
    /// </summary>
    public string WindowSizeArgument(string? userAgent) =>
        MobileSurface.IsAppleUserAgent(userAgent)
            ? $"--window-size={MobileSurface.ScreenWidth},{MobileSurface.ScreenHeight}"
            : WindowSizeArgument();
}
