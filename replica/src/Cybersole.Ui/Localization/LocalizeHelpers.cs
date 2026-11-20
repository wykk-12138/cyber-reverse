using System;
using System.Collections.Generic;
using System.Globalization;
using Avalonia;
using Avalonia.Data;
using Avalonia.Data.Converters;
using Cybersole.Services.Localization;

namespace Cybersole.Ui.Localization;

/// <summary>
/// Runtime helpers and Avalonia multi-value converters corresponding to the original's XAML markup extensions
/// (<c>LocalizeEnumExtension</c>, <c>LocalizeFallbackExtension</c>, <c>LocalizeFormatExtension</c>,
/// <c>LocalizeSwitchExtension</c>).
///
/// <para>
/// Decompiled binary parity (0x1407BC890..0x1407BD1D0): each extension constructs an Avalonia binding/multi-binding
/// paired with one of four value converters that guard against <see cref="AvaloniaProperty.UnsetValue"/> and
/// <see cref="BindingNotification"/> before delegating to <see cref="LocalizationService"/>.
/// </para>
/// </summary>
public static class LocalizeHelpers
{
    internal static bool IsUnsetOrNotification(object? value) =>
        value is null
        || ReferenceEquals(value, AvaloniaProperty.UnsetValue)
        || value is BindingNotification;

    public static string Enum(string prefix, object? value, string? tag = null) =>
        IsUnsetOrNotification(value)
            ? string.Empty
            : LocalizationService.TranslateEnum(tag ?? "en", prefix, value);

    public static string Fallback(object? value, string? fallbackKey, string? tag = null, bool translateFallbackKey = true)
    {
        var primary = IsUnsetOrNotification(value) ? null : value;
        return LocalizationService.TranslateFallback(tag ?? "en", primary, fallbackKey, translateFallbackKey);
    }

    public static string Format(string key, object? value, string? tag = null) =>
        IsUnsetOrNotification(value)
            ? string.Empty
            : LocalizationService.TranslateFormat(tag ?? "en", key, value);

    public static string Format(string key, object? value, object? value2, string? tag = null) =>
        IsUnsetOrNotification(value) || IsUnsetOrNotification(value2)
            ? string.Empty
            : LocalizationService.TranslateFormat(tag ?? "en", key, value, value2);

    public static string Switch(bool condition, string? trueKey, string? falseKey, string? tag = null) =>
        LocalizationService.TranslateSwitch(tag ?? "en", condition, trueKey, falseKey);
}

/// <summary>Converter backing <c>LocalizeEnumExtension.Value</c> (0x1407BD1D0).</summary>
public sealed class LocalizeEnumConverter : IMultiValueConverter
{
    public LocalizeEnumConverter(string prefix, string? languageTag = null)
    {
        Prefix = prefix ?? string.Empty;
        LanguageTag = languageTag;
    }

    public string Prefix { get; }
    public string? LanguageTag { get; }

    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        if (values is null || values.Count == 0 || LocalizeHelpers.IsUnsetOrNotification(values[0]))
            return string.Empty;

        return LocalizationService.TranslateEnum(LanguageTag ?? "en", Prefix, values[0]);
    }
}

/// <summary>Converter backing <c>LocalizeFallbackExtension.Value</c> (0x1407BD0C0).</summary>
public sealed class LocalizeFallbackConverter : IMultiValueConverter
{
    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        if (values is null || values.Count == 0) return string.Empty;

        var primary = values[0];
        if (!LocalizeHelpers.IsUnsetOrNotification(primary))
        {
            if (primary is not string s || s.Length > 0)
                return primary;
        }

        if (values.Count >= 2 && !LocalizeHelpers.IsUnsetOrNotification(values[1]))
            return values[1];

        return string.Empty;
    }
}

/// <summary>Converter backing <c>LocalizeFormatExtension.{Value,Value2}</c> (0x1407BCF00).</summary>
public sealed class LocalizeFormatConverter : IMultiValueConverter
{
    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        if (values is null || values.Count == 0) return string.Empty;

        var template = values[0] as string ?? string.Empty;
        if (values.Count == 1) return template;

        var args = new object?[values.Count - 1];
        for (var i = 1; i < values.Count; i++)
        {
            if (LocalizeHelpers.IsUnsetOrNotification(values[i]))
                return string.Empty;
            args[i - 1] = values[i];
        }

        try
        {
            return string.Format(culture ?? CultureInfo.CurrentCulture, template, args);
        }
        catch (FormatException)
        {
            return template;
        }
    }
}

/// <summary>Converter backing <c>LocalizeSwitchExtension.Condition</c> (0x1407BCC30).</summary>
public sealed class LocalizeSwitchConverter : IMultiValueConverter
{
    public LocalizeSwitchConverter(string? trueKey, string? falseKey, string? languageTag = null)
    {
        TrueKey = trueKey;
        FalseKey = falseKey;
        LanguageTag = languageTag;
    }

    public string? TrueKey { get; }
    public string? FalseKey { get; }
    public string? LanguageTag { get; }

    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
    {
        var condition = values is not null && values.Count > 0 && values[0] is bool b && b;
        return LocalizationService.TranslateSwitch(LanguageTag ?? "en", condition, TrueKey, FalseKey);
    }
}
