using System;
using System.Runtime.InteropServices;

namespace Cybersole.Services;

/// <summary>
/// Plays a notification sound.
///
/// <para>
/// The interface exists so the notification path can be tested without making noise, and so a
/// platform without a player stays visibly silent instead of pretending.
/// </para>
/// </summary>
public interface ISoundPlayer
{
    /// <summary>
    /// Plays <paramref name="path"/>, or the platform's default notification sound when it is null
    /// or empty — which is what the live page's "Default" button means.
    /// </summary>
    void Play(string? path);
}

/// <summary>
/// The Windows player: <c>winmm.dll</c>'s <c>PlaySound</c>, which is what every managed wrapper
/// calls underneath.
///
/// <para>
/// R78: the Notifications page has had a Sounds switch, a sound file and a Play button since the
/// page was built, and <see cref="NotificationService"/> never played anything — <c>Sound</c> and
/// <c>Path</c> were two fields with no reader. This is the reader.
/// </para>
///
/// <para>
/// No NuGet dependency: <c>System.Media.SoundPlayer</c> lives in the Windows Desktop runtime, which
/// this app does not reference, while the call it makes is one P/Invoke.
/// </para>
/// </summary>
public sealed class PlatformSoundPlayer : ISoundPlayer
{
    private const uint SndAsync = 0x0001;
    private const uint SndNoDefault = 0x0002;
    private const uint SndAlias = 0x00010000;

    /// <summary>The Windows alias for "the notification sound", as the Sounds switch expects.</summary>
    internal const string DefaultAlias = "SystemNotification";

    /// <summary>Set to <c>1</c> to make the player a no-op (tests, CI, headless runs).</summary>
    public const string SilentVariable = "CYBERSOLE_SILENT";

    private static bool _suppressed = Environment.GetEnvironmentVariable(SilentVariable) == "1";

    /// <summary>
    /// When true, <see cref="Play"/> returns without making a sound. Defaults to the value of
    /// <see cref="SilentVariable"/> at first use, so the test run is quiet without any test having to remember.
    ///
    /// <para>
    /// R212: without this the suite played <c>SystemNotification</c> through the machine's speakers on every
    /// notification test. The interface's own contract says it "exists so the notification path can be tested without
    /// making noise" — that contract was written but never enforced, and the noise landed on whoever was sitting at
    /// the machine.
    /// </para>
    /// </summary>
    public static bool Suppressed
    {
        get => _suppressed;
        set => _suppressed = value;
    }

    [DllImport("winmm.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool PlaySound(string? sound, IntPtr module, uint flags);

    public void Play(string? path)
    {
        if (_suppressed) return;
        if (!OperatingSystem.IsWindows()) return;

        try
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                PlaySound(DefaultAlias, IntPtr.Zero, SndAsync | SndAlias | SndNoDefault);
                return;
            }

            if (File.Exists(path))
                PlaySound(path, IntPtr.Zero, SndAsync | SndNoDefault);
        }
        catch (Exception)
        {
            // A missing winmm or an unreadable file must not take the notification down with it.
        }
    }
}

/// <summary>A player that records what it was asked to play, for tests and headless runs.</summary>
public sealed class RecordingSoundPlayer : ISoundPlayer
{
    public List<string?> Plays { get; } = new();

    public void Play(string? path) => Plays.Add(path);
}
