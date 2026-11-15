using Cybersole.Core.Input;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Key codes in settings.keyBinds are <b>Avalonia Key enum values</b>, not Win32 virtual-key
/// codes. Round 116 found the two schemes had been mixed: the matcher produced Win32 codes
/// (A = 65, F1 = 112) while settings.json from the live build carried Avalonia values
/// (A = 44, F1 = 90). Every chord failed except Delete (32 in both) and one coincidence —
/// pressing Z (90) started all tasks because F1 is 90 in Avalonia.
/// </summary>
public class KeyBindMatcherTests
{
    [Theory]
    [InlineData("A", 44)]
    [InlineData("z", 69)]
    [InlineData("0", 34)]
    [InlineData("9", 43)]
    [InlineData("D2", 36)]
    [InlineData("F1", 90)]
    [InlineData("F12", 101)]
    [InlineData("F24", 113)]
    [InlineData("Space", 18)]
    [InlineData("Escape", 13)]
    [InlineData("Delete", 32)]
    [InlineData("Left", 23)]
    [InlineData("Right", 25)]
    [InlineData("OemOpenBrackets", 147)]
    [InlineData("OemCloseBrackets", 149)]
    [InlineData("OemPeriod", 144)]
    [InlineData("NumPad5", 79)]
    public void Maps_Names_To_Avalonia_Key_Codes(string name, int expected)
        => Assert.Equal(expected, KeyBindMatcher.VirtualKey(name));

    [Theory]
    [InlineData("[", 147)]
    [InlineData("]", 149)]
    [InlineData(".", 144)]
    [InlineData("-", 143)]
    [InlineData("=", 141)]
    [InlineData("/", 145)]
    [InlineData(";", 140)]
    [InlineData("'", 150)]
    public void Maps_Literal_Punctuation(string name, int expected)
        => Assert.Equal(expected, KeyBindMatcher.VirtualKey(name));

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("Nope")]
    [InlineData("F99")]
    public void Unknown_Names_Map_To_Zero(string? name)
        => Assert.Equal(0, KeyBindMatcher.VirtualKey(name));

    [Fact]
    public void Modifier_Mask_Matches_Settings_Encoding()
    {
        Assert.Equal(0, KeyBindMatcher.Modifiers());
        Assert.Equal(1, KeyBindMatcher.Modifiers(alt: true));
        Assert.Equal(2, KeyBindMatcher.Modifiers(control: true));
        Assert.Equal(4, KeyBindMatcher.Modifiers(shift: true));
        Assert.Equal(7, KeyBindMatcher.Modifiers(true, true, true));
        Assert.Equal(6, KeyBindMatcher.Modifiers(control: true, shift: true));
    }

    [Fact]
    public void Matches_Exact_Key_And_Modifiers()
    {
        var bind = new KeyBind { Key = 69, Modifiers = 0 };     // Avalonia Z
        Assert.True(KeyBindMatcher.Matches(bind, 69, 0));
        Assert.False(KeyBindMatcher.Matches(bind, 69, 2));      // same key, Ctrl held
        Assert.False(KeyBindMatcher.Matches(bind, 68, 0));      // Y
    }

    [Fact]
    public void Null_Bind_Never_Matches()
        => Assert.False(KeyBindMatcher.Matches(null, 69, 0));

    [Fact]
    public void Describe_Renders_Chord()
    {
        Assert.Equal("Ctrl+Shift+F5", KeyBindMatcher.Describe(new KeyBind { Key = 94, Modifiers = 6 }));
        Assert.Equal("Z", KeyBindMatcher.Describe(new KeyBind { Key = 69, Modifiers = 0 }));
        Assert.Equal("Alt+Space", KeyBindMatcher.Describe(new KeyBind { Key = 18, Modifiers = 1 }));
        Assert.Equal("—", KeyBindMatcher.Describe(new KeyBind { Key = 0 }));
    }

    /// <summary>
    /// Every default must round-trip: feeding the chord's own key name back into VirtualKey has
    /// to yield the stored code. That is the invariant the old table broke.
    /// </summary>
    [Fact]
    public void Default_Bindings_RoundTrip_Through_Their_Own_Names()
    {
        var binds = new TaskKeyBinds();

        Assert.Equal(binds.StartAll.Key, KeyBindMatcher.VirtualKey("F1"));
        Assert.Equal(binds.StopAll.Key, KeyBindMatcher.VirtualKey("F2"));
        Assert.Equal(binds.New.Key, KeyBindMatcher.VirtualKey("G"));
        Assert.Equal(binds.Creator.Key, KeyBindMatcher.VirtualKey("N"));
        Assert.Equal(binds.Editor.Key, KeyBindMatcher.VirtualKey("E"));
        Assert.Equal(binds.Delete.Key, KeyBindMatcher.VirtualKey("Delete"));
        Assert.Equal(binds.Clone.Key, KeyBindMatcher.VirtualKey("C"));
        Assert.Equal(binds.Search.Key, KeyBindMatcher.VirtualKey("F"));
        Assert.Equal(binds.Quicktask.Key, KeyBindMatcher.VirtualKey("Q"));
        Assert.Equal(binds.LinkChange.Key, KeyBindMatcher.VirtualKey("M"));
        Assert.Equal(binds.NextGroup.Key, KeyBindMatcher.VirtualKey("Right"));
        Assert.Equal(binds.PreviousGroup.Key, KeyBindMatcher.VirtualKey("Left"));
    }

    [Fact]
    public void Proxy_And_Billing_Defaults_RoundTrip()
    {
        var proxies = new ProxyKeyBinds();
        Assert.Equal(proxies.New.Key, KeyBindMatcher.VirtualKey("G"));
        Assert.Equal(proxies.Add.Key, KeyBindMatcher.VirtualKey("N"));
        Assert.Equal(proxies.TestAll.Key, KeyBindMatcher.VirtualKey("T"));
        Assert.Equal(proxies.Copy.Key, KeyBindMatcher.VirtualKey("C"));
        Assert.Equal(proxies.Clone.Key, KeyBindMatcher.VirtualKey("D"));
        Assert.Equal(proxies.Delete.Key, KeyBindMatcher.VirtualKey("Delete"));

        var billing = new BillingKeyBinds();
        Assert.Equal(billing.New.Key, KeyBindMatcher.VirtualKey("G"));
        Assert.Equal(billing.Add.Key, KeyBindMatcher.VirtualKey("N"));
        Assert.Equal(billing.Clone.Key, KeyBindMatcher.VirtualKey("D"));
        Assert.Equal(billing.Delete.Key, KeyBindMatcher.VirtualKey("Delete"));
    }

    /// <summary>
    /// The exact bug: F1 and Z must not be interchangeable. 90 is F1 in Avalonia and Z in Win32,
    /// and the old matcher conflated them.
    /// </summary>
    [Fact]
    public void F1_And_Z_Are_Different_Keys()
    {
        var startAll = new TaskKeyBinds().StartAll;

        Assert.True(KeyBindMatcher.Matches(startAll, KeyBindMatcher.VirtualKey("F1"), 0));
        Assert.False(KeyBindMatcher.Matches(startAll, KeyBindMatcher.VirtualKey("Z"), 0));
    }

    /// <summary>Every chord stored in the live settings.json must resolve to a known code.</summary>
    [Theory]
    [InlineData("startAll", 90)]
    [InlineData("stopAll", 91)]
    [InlineData("new", 50)]
    [InlineData("creator", 57)]
    [InlineData("editor", 48)]
    [InlineData("delete", 32)]
    [InlineData("clone", 46)]
    [InlineData("search", 49)]
    [InlineData("quicktask", 60)]
    [InlineData("linkChange", 56)]
    [InlineData("nextGroup", 25)]
    [InlineData("previousGroup", 23)]
    public void Live_Settings_Values_Are_In_Avalonia_Space(string label, int stored)
    {
        _ = label;
        // A-Z, 0-9, F1-F24, and the named keys are the only legal ranges
        var legal = stored is (>= 34 and <= 43) or (>= 44 and <= 69) or (>= 90 and <= 113)
                    or (>= 18 and <= 33) or (>= 140 and <= 151);
        Assert.True(legal, $"{label}={stored} is outside the Avalonia Key ranges");
    }
}
