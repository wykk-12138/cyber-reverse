using System.IO;
using Cybersole.Services;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R212: the notification player must be silent by default under test. This is the guard for the ding the machine
/// used to make on every notification test — see <see cref="SilentTestRun"/> for the module initializer that sets it.
/// </summary>
public sealed class SoundPlayerTests
{
    private readonly ITestOutputHelper _out;
    public SoundPlayerTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheWholeTestProcessIsSilent()
    {
        _out.WriteLine($"env {PlatformSoundPlayer.SilentVariable}=" +
                       $"{Environment.GetEnvironmentVariable(PlatformSoundPlayer.SilentVariable)}");

        // the module initializer ran, and the player picked it up
        Assert.Equal("1", Environment.GetEnvironmentVariable(PlatformSoundPlayer.SilentVariable));
        Assert.True(PlatformSoundPlayer.Suppressed);
    }

    [Fact]
    public void PlayingWhileSuppressedIsANoOpAndDoesNotThrow()
    {
        var was = PlatformSoundPlayer.Suppressed;
        try
        {
            PlatformSoundPlayer.Suppressed = true;
            var player = new PlatformSoundPlayer();

            // the default alias path and a file path both return without reaching winmm
            player.Play(null);
            player.Play(string.Empty);
            player.Play(Path.Combine(Path.GetTempPath(), "definitely-missing.wav"));
        }
        finally
        {
            PlatformSoundPlayer.Suppressed = was;
        }
    }

    [Fact]
    public void TheSwitchIsReadableFromTheEnvironmentNameInTheSource()
    {
        // the variable name is part of the contract: a CI or a shell can set it without touching code
        Assert.Equal("CYBERSOLE_SILENT", PlatformSoundPlayer.SilentVariable);

        var source = File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Services", "SoundPlayer.cs"));
        Assert.Contains("SndAlias", source);
        Assert.Contains("SystemNotification", source);
        Assert.Contains("if (_suppressed) return;", source);
    }
}
