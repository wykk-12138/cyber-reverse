using Cybersole.Core.Models;

namespace Cybersole.Core.Input;

/// <summary>
/// Matches a live key press against the chords stored in settings.keyBinds.
///
/// The stored codes are <b>Avalonia/WPF Key enum values</b>, not Win32 virtual-key codes.
/// A = 44 … Z = 69, D0 = 34 … D9 = 43, F1 = 90 … F24 = 113, Left = 23, Right = 25,
/// Delete = 32, Space = 18, OemPeriod = 144.
///
/// Round 116 found this the hard way: the old implementation mapped names to Win32 VK codes
/// (A = 65, F1 = 112) and compared those against the stored Avalonia values, so every binding in
/// the file failed except two coincidences — <c>Delete</c> (32 in both schemes) and the fact that
/// <c>'Z'</c> is 90 in Win32 and <c>F1</c> is 90 in Avalonia. Pressing Z started every task while
/// F1 did nothing.
///
/// Keeping the values as Avalonia codes also means the UI can round-trip a captured key press
/// without a translation table.
/// </summary>
public static class KeyBindMatcher
{
    // Avalonia.Input.Key values that matter for shortcuts. Named so the numbers are auditable.
    private static readonly Dictionary<string, int> Named = new(StringComparer.OrdinalIgnoreCase)
    {
        ["NONE"] = 0,
        ["CANCEL"] = 1,
        ["BACK"] = 2, ["BACKSPACE"] = 2,
        ["TAB"] = 3,
        ["RETURN"] = 6, ["ENTER"] = 6,
        ["PAUSE"] = 7,
        ["CAPITAL"] = 8, ["CAPSLOCK"] = 8,
        ["ESCAPE"] = 13, ["ESC"] = 13,
        ["SPACE"] = 18,
        ["PRIOR"] = 19, ["PAGEUP"] = 19, ["PGUP"] = 19,
        ["NEXT"] = 20, ["PAGEDOWN"] = 20, ["PGDN"] = 20,
        ["END"] = 21,
        ["HOME"] = 22,
        ["LEFT"] = 23,
        ["UP"] = 24,
        ["RIGHT"] = 25,
        ["DOWN"] = 26,
        ["SNAPSHOT"] = 30, ["PRINTSCREEN"] = 30, ["PRTSC"] = 30,
        ["INSERT"] = 31, ["INS"] = 31,
        ["DELETE"] = 32, ["DEL"] = 32,
        ["HELP"] = 33,
        ["LWIN"] = 70, ["LWINDOWS"] = 70,
        ["RWIN"] = 71, ["RWINDOWS"] = 71,
        ["APPS"] = 72,
        ["SLEEP"] = 73,
        ["MULTIPLY"] = 84,
        ["ADD"] = 85,
        ["SEPARATOR"] = 86,
        ["SUBTRACT"] = 87,
        ["DECIMAL"] = 88,
        ["DIVIDE"] = 89,
        ["NUMLOCK"] = 114,
        ["SCROLL"] = 115,
        ["LEFTSHIFT"] = 116, ["SHIFT"] = 116,
        ["RIGHTSHIFT"] = 117,
        ["LEFTCTRL"] = 118, ["CONTROL"] = 118, ["CTRL"] = 118,
        ["RIGHTCTRL"] = 119,
        ["LEFTALT"] = 120, ["ALT"] = 120,
        ["RIGHTALT"] = 121,
        ["OEMMINUS"] = 143,
        ["OEMPLUS"] = 141,
        ["OEMCOMMA"] = 142,
        ["OEMPERIOD"] = 144,
        ["OEMQUESTION"] = 145,
        ["OEMTILDE"] = 146,
        ["OEMOPENBRACKETS"] = 147, ["OEM4"] = 147, ["LEFTBRACKET"] = 147,
        ["OEMPIPE"] = 148, ["OEM5"] = 148, ["BACKSLASH"] = 148,
        ["OEMCLOSEBRACKETS"] = 149, ["OEM6"] = 149, ["RIGHTBRACKET"] = 149,
        ["OEMQUOTES"] = 150, ["OEM7"] = 150, ["QUOTE"] = 150,
        ["OEMSEMICOLON"] = 140, ["OEM1"] = 140, ["SEMICOLON"] = 140,
        ["OEM8"] = 151,
        ["OEMBACKSLASH"] = 148,
        ["ABNT_C1"] = 152,
        ["ABNT_C2"] = 153,
        ["DEADGRAVE"] = 155,
        ["DEADACUTE"] = 156,
        ["DEADCIRCUMFLEX"] = 157,
        ["DEADTILDE"] = 158,
        ["DEADDIAERESIS"] = 159,
        ["DEADRINGABOVE"] = 160,
        ["DEADDOUBLEACUTE"] = 161,
        ["DEADCARON"] = 162,
        ["DEADBREVE"] = 163,
        ["DEADOGONEK"] = 164,
        ["DEADDOTABOVE"] = 165,
        ["DEADMACRON"] = 166,
        ["DEADCEDILLA"] = 167,
        ["DEADOGONEK2"] = 168,
        ["DEADSTROKE"] = 169,
        ["DEADABOVECOMMA"] = 170,
        ["DEADREVERSECOMMA"] = 171,
    };

    /// <summary>
    /// Key name to its Avalonia Key code; 0 when unknown. Accepts "A", "Z", "0".."9",
    /// "F1".."F24", the names in <see cref="Named"/>, and the literal punctuation a chord
    /// might be described with ("[", "]", "-", "=", ",", ".", "/", "\\", "'", ";", "`").
    /// </summary>
    public static int VirtualKey(string? name)
    {
        if (string.IsNullOrWhiteSpace(name)) return 0;

        var key = name.Trim();
        var upper = key.ToUpperInvariant();

        // single character: letters and digits have contiguous ranges
        if (key.Length == 1)
        {
            var c = upper[0];
            if (c is >= 'A' and <= 'Z') return 44 + (c - 'A');   // A = 44, Z = 69
            if (c is >= '0' and <= '9') return 34 + (c - '0');   // D0 = 34, D9 = 43

            return key switch
            {
                " " => 18,                                        // Space
                "-" => 143, "_" => 143,
                "=" => 141, "+" => 141,
                "," => 142, "<" => 142,
                "." => 144, ">" => 144,
                "/" => 145, "?" => 145,
                "`" => 146, "~" => 146,
                "[" => 147, "{" => 147,
                "\\" => 148, "|" => 148,
                "]" => 149, "}" => 149,
                "'" => 150, "\"" => 150,
                ";" => 140, ":" => 140,
                _ => 0,
            };
        }

        // numpad digits: "NumPad0".."NumPad9", plus the plain "Num0" spelling
        if (upper.StartsWith("NUMPAD") || upper.StartsWith("NUM"))
        {
            var tail = upper.StartsWith("NUMPAD") ? upper[6..] : upper[3..];
            if (tail.Length == 1 && tail[0] is >= '0' and <= '9') return 74 + (tail[0] - '0');
        }

        // D0..D9 (the number row) and F1..F24 as Avalonia spells them
        if (upper.Length == 2 && upper[0] == 'D' && upper[1] is >= '0' and <= '9')
            return 34 + (upper[1] - '0');

        if (upper.Length >= 2 && upper[0] == 'F' && int.TryParse(upper[1..], out var fn)
            && fn is >= 1 and <= 24)
            return 90 + fn - 1;                                   // F1 = 90, F24 = 113

        return Named.TryGetValue(upper, out var code) ? code : 0;
    }

    /// <summary>settings.json stores modifiers as a bit mask: Alt=1, Control=2, Shift=4.</summary>
    public static int Modifiers(bool alt = false, bool control = false, bool shift = false)
        => (alt ? 1 : 0) | (control ? 2 : 0) | (shift ? 4 : 0);

    public static bool Matches(KeyBind? bind, int virtualKey, int modifiers)
        => bind is not null && bind.Key == virtualKey && bind.Modifiers == modifiers;

    /// <summary>"Ctrl+Shift+F5" style label for the UI.</summary>
    public static string Describe(KeyBind? bind)
    {
        if (bind is null || bind.Key == 0) return "—";

        var parts = new List<string>();
        if ((bind.Modifiers & 2) != 0) parts.Add("Ctrl");
        if ((bind.Modifiers & 1) != 0) parts.Add("Alt");
        if ((bind.Modifiers & 4) != 0) parts.Add("Shift");
        parts.Add(Name(bind.Key));
        return string.Join('+', parts);
    }

    private static string Name(int code)
    {
        if (code is >= 44 and <= 69) return ((char)('A' + code - 44)).ToString();
        if (code is >= 34 and <= 43) return ((char)('0' + code - 34)).ToString();
        if (code is >= 90 and <= 113) return $"F{code - 90 + 1}";
        if (code is >= 74 and <= 83) return $"NumPad{code - 74}";

        return code switch
        {
            18 => "Space",
            13 => "Esc",
            6 => "Enter",
            3 => "Tab",
            2 => "Backspace",
            32 => "Delete",
            31 => "Insert",
            22 => "Home",
            21 => "End",
            19 => "PageUp",
            20 => "PageDown",
            23 => "Left",
            24 => "Up",
            25 => "Right",
            26 => "Down",
            140 => ";",
            141 => "=",
            142 => ",",
            143 => "-",
            144 => ".",
            145 => "/",
            146 => "`",
            147 => "[",
            148 => "\\",
            149 => "]",
            150 => "'",
            _ => $"0x{code:X2}",
        };
    }
}
