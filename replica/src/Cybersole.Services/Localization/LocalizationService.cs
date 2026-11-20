using System.Collections.Concurrent;
using System.Globalization;
using System.Reflection;
using Newtonsoft.Json.Linq;

namespace Cybersole.Services.Localization;

/// <summary>
/// Loads the four dictionaries the live build ships and resolves keys against them.
///
/// Round 131 corrected round 126. Round 126 concluded the original only localised the four
/// language names; that was wrong, and the reason was a bad search: the string table shows the
/// resources as `Cybersole.Locales.xx.json` entries but the *contents* live elsewhere in the
/// single-file image, so grepping for `"Language.` found four keys and nothing more.
///
/// Carving the payloads out (round 131) gave four files of **1142 keys each**, identical key sets,
/// covering Analytics / Common / Tasks / Proxies / Settings and the rest. The resource names are
/// the original's own: <c>Cybersole.Locales.en.json</c>, <c>.ja</c>, <c>.ko</c>, <c>.zh-Hans</c>.
/// </summary>
public sealed class LocalizationService
{
    /// <summary>Culture tag, resource name and display name, in the live selector's order.</summary>
    public static readonly IReadOnlyList<(string Tag, string Resource, string Display)> Languages = new[]
    {
        ("en", "Cybersole.Locales.en.json", "English"),
        ("ja", "Cybersole.Locales.ja.json", "Japanese"),
        ("ko", "Cybersole.Locales.ko.json", "Korean"),
        ("zh-Hans", "Cybersole.Locales.zh-Hans.json", "Chinese (Simplified)"),
    };

    private static readonly ConcurrentDictionary<string, IReadOnlyDictionary<string, string>> Cache = new();

    private readonly Cybersole.Core.Settings.GlobalSettings _settings;

    public LocalizationService(Cybersole.Core.Settings.GlobalSettings settings) => _settings = settings;

    public static IReadOnlyList<string> DisplayNames { get; } = Languages.Select(x => x.Display).ToList();

    /// <summary>The dictionary for a culture tag; empty when the resource is missing.</summary>
    public static IReadOnlyDictionary<string, string> For(string? tag)
    {
        var resolved = ResolveTag(tag);
        return Cache.GetOrAdd(resolved, Load);
    }

    /// <summary>Display name for a stored value, which may be a tag, a display name or a bare word.</summary>
    public static string DisplayOf(string? stored) => Entry(ResolveTag(stored)).Display;

    /// <summary>Culture tag for a stored value; unknown input falls back to English.</summary>
    public static string ResolveTag(string? stored)
    {
        if (string.IsNullOrWhiteSpace(stored)) return "en";

        var value = stored.Trim();
        foreach (var (tag, _, display) in Languages)
        {
            if (string.Equals(tag, value, StringComparison.OrdinalIgnoreCase)) return tag;
            if (string.Equals(display, value, StringComparison.OrdinalIgnoreCase)) return tag;
        }

        // older settings stored "English" / "ChineseSimplified"
        if (value.StartsWith("zh", StringComparison.OrdinalIgnoreCase)
            || value.Equals("ChineseSimplified", StringComparison.OrdinalIgnoreCase)) return "zh-Hans";

        return "en";
    }

    private static (string Tag, string Resource, string Display) Entry(string tag) =>
        Languages.FirstOrDefault(x => x.Tag == tag) is var hit && hit.Tag is not null ? hit : Languages[0];

    /// <summary>
    /// Resolve one key for one culture. Falls back to English, then to the key itself — a missing
    /// string must never render as blank, because a blank label looks like a layout bug.
    /// </summary>
    public string this[string key] => Translate(CurrentTag, key);

    public string CurrentTag => ResolveTag(_settings.Language);

    public string Current => DisplayOf(_settings.Language);

    public int CurrentIndex
    {
        get
        {
            var tag = CurrentTag;
            for (var i = 0; i < Languages.Count; i++)
                if (Languages[i].Tag == tag) return i;
            return 0;
        }
    }

    public static string Translate(string? tag, string key)
    {
        if (string.IsNullOrEmpty(key)) return string.Empty;

        var dictionary = For(tag);
        if (dictionary.TryGetValue(key, out var value) && !string.IsNullOrEmpty(value)) return value;

        var fallback = For("en");
        if (fallback.TryGetValue(key, out var english) && !string.IsNullOrEmpty(english)) return english;

        return key;
    }

    /// <summary>
    /// Format a translated key against one or more values (mirrors <c>LocalizeFormatExtension</c>, 0x1407BCF00).
    /// Returns empty when any argument is null so partial binding inputs never throw or leak raw <c>{0}</c>.
    /// </summary>
    public static string TranslateFormat(string? tag, string key, params object?[] values)
    {
        if (string.IsNullOrEmpty(key)) return string.Empty;
        var template = Translate(tag, key);
        if (values is null || values.Length == 0) return template;

        foreach (var arg in values)
            if (arg is null) return string.Empty;

        try
        {
            return string.Format(CultureInfo.CurrentCulture, template, values);
        }
        catch (FormatException)
        {
            return template;
        }
    }

    /// <summary>
    /// Translate an enum/token value using <c>{prefix}{value}</c> (mirrors <c>LocalizeEnumExtension</c>, 0x1407BD1D0).
    /// Returns empty when <paramref name="value"/> is null.
    /// </summary>
    public static string TranslateEnum(string? tag, string prefix, object? value)
    {
        if (value is null) return string.Empty;
        var text = value.ToString();
        if (string.IsNullOrEmpty(text)) return string.Empty;
        return Translate(tag, (prefix ?? string.Empty) + text);
    }

    /// <summary>
    /// Return <paramref name="value"/> when non-null and non-empty; otherwise resolve <paramref name="fallbackKey"/>
    /// (mirrors <c>LocalizeFallbackExtension</c>, 0x1407BD0C0).
    /// </summary>
    public static string TranslateFallback(string? tag, object? value, string? fallbackKey, bool translateFallbackKey = true)
    {
        if (value is string s)
        {
            if (s.Length > 0) return s;
        }
        else if (value is not null)
        {
            var rendered = value.ToString();
            if (!string.IsNullOrEmpty(rendered)) return rendered;
        }

        if (string.IsNullOrEmpty(fallbackKey)) return string.Empty;
        return translateFallbackKey ? Translate(tag, fallbackKey) : fallbackKey;
    }

    /// <summary>
    /// Choose <paramref name="trueKey"/> or <paramref name="falseKey"/> by <paramref name="condition"/> and translate
    /// (mirrors <c>LocalizeSwitchExtension</c>, 0x1407BCC30).
    /// </summary>
    public static string TranslateSwitch(string? tag, bool condition, string? trueKey, string? falseKey)
    {
        var key = condition ? trueKey : falseKey;
        return string.IsNullOrEmpty(key) ? string.Empty : Translate(tag, key);
    }

    public string Format(string key, object? value) => TranslateFormat(CurrentTag, key, value);
    public string Format(string key, object? value, object? value2) => TranslateFormat(CurrentTag, key, value, value2);
    public string Format(string key, params object?[] values) => TranslateFormat(CurrentTag, key, values);
    public string Enum(string prefix, object? value) => TranslateEnum(CurrentTag, prefix, value);
    public string Fallback(object? value, string? fallbackKey, bool translateFallbackKey = true) =>
        TranslateFallback(CurrentTag, value, fallbackKey, translateFallbackKey);
    public string Switch(bool condition, string? trueKey, string? falseKey) =>
        TranslateSwitch(CurrentTag, condition, trueKey, falseKey);

    /// <summary>Store a choice by display name or tag. Returns false when it is not one of the four.</summary>
    public bool Select(string? choice)
    {
        if (string.IsNullOrWhiteSpace(choice)) return false;

        var value = choice.Trim();
        foreach (var (tag, _, display) in Languages)
        {
            if (!string.Equals(tag, value, StringComparison.OrdinalIgnoreCase)
                && !string.Equals(display, value, StringComparison.OrdinalIgnoreCase)) continue;

            _settings.Language = display;
            return true;
        }

        return false;
    }

    private static IReadOnlyDictionary<string, string> Load(string tag)
    {
        var entry = Entry(tag);
        // the dictionaries live in Cybersole.Core, not here — this type is in Cybersole.Services
        var asm = typeof(Cybersole.Core.Settings.GlobalSettings).Assembly;
        using var stream = asm.GetManifestResourceStream(entry.Resource);
        if (stream is null) return new Dictionary<string, string>();

        using var reader = new StreamReader(stream, System.Text.Encoding.UTF8);
        var json = reader.ReadToEnd();

        var parsed = JObject.Parse(json);
        var map = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var property in parsed.Properties())
            map[property.Name] = property.Value.Type == JTokenType.String
                ? property.Value.Value<string>() ?? string.Empty
                : property.Value.ToString();

        return map;
    }

    /// <summary>Resource names present in this assembly, for diagnostics.</summary>
    public static IEnumerable<string> AvailableResources() =>
        typeof(Cybersole.Core.Settings.GlobalSettings).Assembly.GetManifestResourceNames()
            .Where(n => n.Contains("Locales", StringComparison.OrdinalIgnoreCase));
}
