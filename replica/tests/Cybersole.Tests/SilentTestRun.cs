using System.Runtime.CompilerServices;
using Cybersole.Services;

namespace Cybersole.Tests;

/// <summary>
/// R212: the test process never makes a sound.
///
/// <para>
/// <see cref="PlatformSoundPlayer"/> calls <c>winmm!PlaySound("SystemNotification")</c> whenever a notification fires,
/// and the suite fires plenty. Every one of those was audible on the machine — a Windows ding with no window attached
/// to it, several times per run. The switch below is set before the first test runs, so the whole process is quiet;
/// a test that wants to exercise the player turns <see cref="PlatformSoundPlayer.Suppressed"/> off and on itself.
/// </para>
/// </summary>
internal static class SilentTestRun
{
    [ModuleInitializer]
    internal static void Initialize() => Environment.SetEnvironmentVariable(
        PlatformSoundPlayer.SilentVariable, "1");
}
