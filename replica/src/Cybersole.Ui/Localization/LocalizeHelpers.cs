using Avalonia;
using Avalonia.Data;
using Cybersole.Services.Localization;

namespace Cybersole.Ui.Localization;

/// <summary>
/// Runtime helpers corresponding to the original's XAML localization markup extensions
/// (<c>LocalizeEnumExtension</c>, <c>LocalizeFallbackExtension</c>, <c>LocalizeFormatExtension</c>,
/// <c>LocalizeSwitchExtension</c>).
///
/// <para>
/// Decompiled binary parity (0x1407BC890..0x1407BD1D0): each extension constructs an Avalonia binding/multi-binding
/// guarding against <see cref="AvaloniaProperty.UnsetValue"/> and <see cref="BindingNotification"/> before delegating
/// to <see cref="LocalizationService"/>. In the code-first Avalonia UI, callers invoke these helpers directly.
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
