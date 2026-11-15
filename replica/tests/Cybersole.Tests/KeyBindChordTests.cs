using System.Linq;
using Cybersole.Core.Input;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R338: every chord printed by Settings → Keyboard Shortcuts, pinned against the running build.
///
/// <para>
/// The page renders each binding through <see cref="KeyBindMatcher.Describe"/>, so the thing on screen is that method's
/// output. R76 copied the table off the live page; this test makes the copy falsifiable: 12 task chords, 6 proxy chords
/// and 4 billing chords, in the order the page lists them, spelled exactly as the chips read.
/// </para>
/// </summary>
public sealed class KeyBindChordTests
{
    private readonly ITestOutputHelper _out;
    public KeyBindChordTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheTwelveTaskChordsReadAsThePagePrintsThem()
    {
        var binds = new TaskKeyBinds();
        var actual = new[]
        {
            KeyBindMatcher.Describe(binds.New), KeyBindMatcher.Describe(binds.Creator),
            KeyBindMatcher.Describe(binds.Editor), KeyBindMatcher.Describe(binds.StartAll),
            KeyBindMatcher.Describe(binds.StopAll), KeyBindMatcher.Describe(binds.Delete),
            KeyBindMatcher.Describe(binds.Clone), KeyBindMatcher.Describe(binds.Search),
            KeyBindMatcher.Describe(binds.Quicktask), KeyBindMatcher.Describe(binds.LinkChange),
            KeyBindMatcher.Describe(binds.NextGroup), KeyBindMatcher.Describe(binds.PreviousGroup),
        };

        _out.WriteLine(string.Join(" | ", actual));

        Assert.Equal(
            new[]
            {
                "Ctrl+G", "Ctrl+N", "Ctrl+E", "F1", "F2", "Delete",
                "Ctrl+C", "Ctrl+F", "Ctrl+Q", "Ctrl+M", "Ctrl+Right", "Ctrl+Left",
            },
            actual);
    }

    [Fact]
    public void TheSixProxyChordsReadAsThePagePrintsThem()
    {
        var binds = new ProxyKeyBinds();
        var actual = new[]
        {
            KeyBindMatcher.Describe(binds.New), KeyBindMatcher.Describe(binds.Add),
            KeyBindMatcher.Describe(binds.TestAll), KeyBindMatcher.Describe(binds.Copy),
            KeyBindMatcher.Describe(binds.Clone), KeyBindMatcher.Describe(binds.Delete),
        };

        _out.WriteLine(string.Join(" | ", actual));

        Assert.Equal(
            new[] { "Ctrl+G", "Ctrl+N", "Ctrl+T", "Ctrl+C", "Ctrl+D", "Delete" },
            actual);
    }
    /// <summary>
    /// The four Billing chords. R338 re-read "New Group Ctrl+G" and "Add Profile Ctrl+N" off the live page; the last two
    /// rows were below the fold and come from R76's table, so they are pinned here rather than claimed as re-measured.
    /// </summary>
    [Fact]
    public void TheFourBillingChordsReadAsThePagePrintsThem()
    {
        var binds = new BillingKeyBinds();
        var actual = new[]
        {
            KeyBindMatcher.Describe(binds.New), KeyBindMatcher.Describe(binds.Add),
            KeyBindMatcher.Describe(binds.Clone), KeyBindMatcher.Describe(binds.Delete),
        };

        _out.WriteLine(string.Join(" | ", actual));

        Assert.Equal(new[] { "Ctrl+G", "Ctrl+N", "Ctrl+D", "Delete" }, actual);
    }
}
