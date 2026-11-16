namespace Cybersole.Core.Store;

/// <summary>
/// The single place the app's version string lives.
///
/// <para>
/// R118 centralised it because the number was spelled in five files and a bump meant finding all
/// five. R74 found that the one value it centralised was <b>wrong</b>: it said 5.18.32's
/// predecessor — <c>5.18.28</c> — in the constant, in the window title, in the settings rail and in
/// 54 places across 34 files.
/// </para>
///
/// <para>
/// The binary says otherwise. <c>Cybersole.exe</c> reports <c>FileVersion 5.18.32.0</c> and
/// <c>ProductVersion 5.18.32+dfee55e…</c>, and its own Settings page prints "Version 5.18.32".
/// Centralising a number does not check it; <c>VersionMatchesTheOriginalBinary</c> now does.
/// </para>
/// </summary>
public static class AppVersion
{
    public const string Current = "5.18.32";

    /// <summary>"5.18.32" into (5, 18, 30); missing parts are 0.</summary>
    public static Version Parsed =>
        Version.TryParse(Current, out var v) ? v : new Version(5, 18, 30);
}
