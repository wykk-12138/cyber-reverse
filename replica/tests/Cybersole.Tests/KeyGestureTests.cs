using Cybersole.KeyInput;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// KeyGesture, one of the seven real gaps behind the seventeen absent types.
///
/// <para>
/// R926. The bindings name two members, Key and Modifiers, and the replica had nothing under Cybersole.KeyInput. The
/// property these tests care about is the round trip: a gesture stored as text and reloaded must equal the original,
/// because a keybinding written to a settings file and read back is the ordinary path and a case slip there turns a
/// working binding into a dead one.
/// </para>
/// </summary>
public class KeyGestureTests
{
    /// <summary>The two member names the bindings declare are the two the type has.</summary>
    [Fact]
    public void TheTwoBoundMembersExist()
    {
        var t = typeof(KeyGesture);
        Assert.NotNull(t.GetProperty("Key"));
        Assert.NotNull(t.GetProperty("Modifiers"));
    }

    /// <summary>A gesture formats in the conventional order regardless of the order its modifiers were set in.</summary>
    [Fact]
    public void ModifierOrderDoesNotChangeTheText()
    {
        var a = new KeyGesture("D", ModifierKeys.Control | ModifierKeys.Shift);
        var b = new KeyGesture("D", ModifierKeys.Shift | ModifierKeys.Control);

        Assert.Equal("Ctrl+Shift+D", a.ToString());
        Assert.Equal(a.ToString(), b.ToString());
        Assert.Equal(a, b);
    }

    /// <summary>The round trip, which is the reason the type holds parts rather than a string.</summary>
    [Theory]
    [InlineData("Ctrl+Shift+D")]
    [InlineData("Alt+F4")]
    [InlineData("F5")]
    [InlineData("Ctrl+Alt+Delete")]
    public void TextSurvivesARoundTrip(string text)
    {
        Assert.True(KeyGesture.TryParse(text, out var parsed));
        Assert.Equal(text, parsed.ToString());
    }

    /// <summary>
    /// Any modifier order and any case parses, because a hand-edited settings file is a normal source and refusing it
    /// over a capital letter would lose a binding the user meant.
    /// </summary>
    [Theory]
    [InlineData("shift+ctrl+d", "Ctrl+Shift+D")]
    [InlineData("CTRL+SHIFT+D", "Ctrl+Shift+D")]
    [InlineData("control + alt + x", "Ctrl+Alt+X")]
    public void AnyOrderAndCaseParsesToTheCanonicalForm(string input, string canonical)
    {
        Assert.True(KeyGesture.TryParse(input, out var parsed));
        Assert.Equal(canonical, parsed.ToString());
    }

    /// <summary>Text with two non-modifiers is not a gesture, and saying so is better than silently keeping one.</summary>
    [Theory]
    [InlineData("Ctrl+A+B")]
    [InlineData("Ctrl+Shift")]
    [InlineData("")]
    [InlineData("   ")]
    public void MalformedTextIsRejected(string input)
    {
        Assert.False(KeyGesture.TryParse(input, out _));
    }

    /// <summary>Unbound is a state with its own answer, since a keybinding editor has to show and act on it.</summary>
    [Fact]
    public void EmptyIsItsOwnState()
    {
        Assert.True(default(KeyGesture).IsEmpty);
        Assert.True(new KeyGesture("").IsEmpty);
        Assert.False(new KeyGesture("D").IsEmpty);
        // a modifier alone is not empty, and not usable either -- the distinction is kept rather than collapsed
        Assert.False(new KeyGesture("", ModifierKeys.Control).IsEmpty);
    }

    /// <summary>Equality ignores case in the key, so "d" and "D" are one binding rather than two.</summary>
    [Fact]
    public void KeyComparisonIgnoresCase()
    {
        Assert.Equal(new KeyGesture("d"), new KeyGesture("D"));
        Assert.Equal(new KeyGesture("d").GetHashCode(), new KeyGesture("D").GetHashCode());
        Assert.NotEqual(new KeyGesture("d", ModifierKeys.Control), new KeyGesture("D"));
    }
}