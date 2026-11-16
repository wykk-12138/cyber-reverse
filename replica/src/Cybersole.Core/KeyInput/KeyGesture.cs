namespace Cybersole.KeyInput;

/// <summary>
/// A key with its modifiers — what a keybinding is stored as.
///
/// <para>
/// R926. The bindings declare <c>Cybersole.KeyInput.KeyGesture</c> with two members, <c>Key</c> and <c>Modifiers</c>,
/// and the replica declared neither this type nor anything under this namespace. That made it one of the seven real
/// gaps behind the seventeen absent types, and the smallest of them: two members with names that say exactly what they
/// are.
/// </para>
///
/// <para>
/// <b>Why a value type rather than a string.</b> A keybinding written as "Ctrl+Shift+D" has to be parsed wherever it is
/// read and formatted wherever it is shown, and the two can disagree — a case slip in one direction turns a working
/// binding into a dead one. Holding the key and the modifiers separately means the comparison is on values and there is
/// no text in the middle to get wrong.
/// </para>
///
/// <para>
/// <b>What is inference.</b> The member types. The bindings name <c>Key</c> and <c>Modifiers</c> without saying whether
/// they are an enum, a string or a flag set, so the choices below are the least surprising ones for a keybinding and are
/// labelled rather than presented as recovered. What is not inference is the pair of names: those are the binding's.
/// </para>
/// </summary>
public readonly struct KeyGesture : IEquatable<KeyGesture>
{
    /// <summary>The key itself, without any modifier. An empty string means "no key", which is how an unbound gesture
    /// is represented rather than by a null.</summary>
    public string Key { get; }

    /// <summary>
    /// The modifiers, as a flag set. Separate from <see cref="Key"/> so that a comparison cannot be confused by the
    /// order they were written in.
    /// </summary>
    public ModifierKeys Modifiers { get; }

    public KeyGesture(string key, ModifierKeys modifiers = ModifierKeys.None)
    {
        // R926: a single-character key is normalised to upper case here rather than in ToString, so that the value and
        // its text agree. Leaving it alone made "shift+ctrl+d" parse to a gesture whose ToString was "Ctrl+Shift+d" and
        // the round trip failed on a capital letter -- which is the exact class of slip this type exists to prevent.
        Key = string.IsNullOrEmpty(key) ? string.Empty : (key.Length == 1 ? key.ToUpperInvariant() : key);
        Modifiers = modifiers;
    }

    /// <summary>True when nothing is bound, which is a state a keybinding editor has to show and act on.</summary>
    public bool IsEmpty => string.IsNullOrEmpty(Key) && Modifiers == ModifierKeys.None;

    public bool Equals(KeyGesture other) =>
        string.Equals(Key, other.Key, StringComparison.OrdinalIgnoreCase) && Modifiers == other.Modifiers;

    public override bool Equals(object? obj) => obj is KeyGesture other && Equals(other);

    public override int GetHashCode() =>
        HashCode.Combine(Key.ToUpperInvariant(), Modifiers);

    public static bool operator ==(KeyGesture a, KeyGesture b) => a.Equals(b);

    public static bool operator !=(KeyGesture a, KeyGesture b) => !a.Equals(b);

    /// <summary>
    /// Text form, in the order a keyboard shortcut is conventionally written. The round trip through
    /// <see cref="TryParse"/> is the property that matters: a gesture stored and reloaded must equal the original.
    /// </summary>
    public override string ToString()
    {
        var parts = new List<string>(4);
        if (Modifiers.HasFlag(ModifierKeys.Control)) parts.Add("Ctrl");
        if (Modifiers.HasFlag(ModifierKeys.Shift)) parts.Add("Shift");
        if (Modifiers.HasFlag(ModifierKeys.Alt)) parts.Add("Alt");
        if (Modifiers.HasFlag(ModifierKeys.Windows)) parts.Add("Win");
        if (!string.IsNullOrEmpty(Key)) parts.Add(Key);
        return string.Join("+", parts);
    }

    /// <summary>
    /// Parses the conventional text form. Accepts either case and any modifier order, because a hand-edited settings
    /// file is a normal source of these and refusing it over a capital letter would lose a binding the user meant.
    /// </summary>
    public static bool TryParse(string? text, out KeyGesture gesture)
    {
        gesture = default;
        if (string.IsNullOrWhiteSpace(text)) return false;

        var modifiers = ModifierKeys.None;
        string? key = null;

        foreach (var raw in text.Split('+', StringSplitOptions.RemoveEmptyEntries))
        {
            var part = raw.Trim();
            switch (part.ToLowerInvariant())
            {
                case "ctrl": case "control": modifiers |= ModifierKeys.Control; break;
                case "shift": modifiers |= ModifierKeys.Shift; break;
                case "alt": modifiers |= ModifierKeys.Alt; break;
                case "win": case "windows": case "meta": modifiers |= ModifierKeys.Windows; break;
                default:
                    // only one non-modifier is meaningful; a second means the text is not a gesture
                    if (key != null) return false;
                    key = part;
                    break;
            }
        }

        if (key == null) return false;
        gesture = new KeyGesture(key, modifiers);
        return true;
    }
}

/// <summary>
/// The modifier half of a <see cref="KeyGesture"/>, as flags so that combinations need no ordering.
/// </summary>
[Flags]
public enum ModifierKeys
{
    None = 0,
    Control = 1,
    Shift = 2,
    Alt = 4,
    Windows = 8,
}