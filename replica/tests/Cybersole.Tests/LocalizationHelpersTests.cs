using System;
using Avalonia;
using Avalonia.Data;
using Cybersole.Core.Settings;
using Cybersole.Services.Localization;
using Cybersole.Ui.Localization;
using Cybersole.Ui.Views.Analytics;
using Cybersole.Ui.Views.SmartActions;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Verifies all five <c>Cybersole.Ui.Localization</c> behaviors (<c>LocalizeEnumExtension.Value</c>,
/// <c>LocalizeFallbackExtension.Value</c>, <c>LocalizeFormatExtension.{Value,Value2}</c>, and
/// <c>LocalizeSwitchExtension.Condition</c>) across <see cref="LocalizationService"/> and
/// <see cref="LocalizeHelpers"/>.
/// </summary>
public sealed class LocalizationHelpersTests
{
    private static BindingNotification ErrorNotification =>
        new(new InvalidOperationException("x"), BindingErrorType.Error);

    [Fact]
    public void LocalizeEnumTranslatesPrefixPlusEnumAcrossLanguages()
    {
        Assert.Equal("Today", AnalyticsView.PeriodLabel("Today", "en"));
        Assert.Equal(
            LocalizationService.Translate("ja", "Analytics.TimeSpan.Week"),
            AnalyticsView.PeriodLabel("Week", "ja"));
        Assert.Equal(string.Empty, LocalizeHelpers.Enum("Analytics.TimeSpan.", null));
        Assert.Equal(string.Empty, LocalizeHelpers.Enum("Analytics.TimeSpan.", AvaloniaProperty.UnsetValue));
        Assert.Equal(string.Empty, LocalizeHelpers.Enum("Analytics.TimeSpan.", ErrorNotification));
    }

    [Fact]
    public void LocalizeFallbackUsesNonEmptyValueOtherwiseTranslatesFallbackKey()
    {
        Assert.Equal("1234", LocalizeHelpers.Fallback("1234", "Auth.License.PlaceholderName"));
        Assert.Equal("License", LocalizeHelpers.Fallback("", "Auth.License.PlaceholderName"));
        Assert.Equal("License", LocalizeHelpers.Fallback(null, "Auth.License.PlaceholderName"));
        Assert.Equal("License", LocalizeHelpers.Fallback(AvaloniaProperty.UnsetValue, "Auth.License.PlaceholderName"));
        Assert.Equal("License", LocalizeHelpers.Fallback(ErrorNotification, "Auth.License.PlaceholderName"));
        Assert.Equal("FallbackLiteral", LocalizeHelpers.Fallback(AvaloniaProperty.UnsetValue, "FallbackLiteral", translateFallbackKey: false));
    }

    [Fact]
    public void LocalizeFormatSupportsOneAndTwoValuesAndGuardsUnset()
    {
        Assert.Equal("Ending in 4242", LocalizeHelpers.Format("Auth.License.EndingIn", "4242"));
        Assert.Equal("Triggered today (2)", LocalizeHelpers.Format("SmartActions.LastRun.Format", "today", 2));
        Assert.Equal("Webhook (3 more)", LocalizeHelpers.Format("SmartActions.Actions.MoreFormat", "Webhook", 3));
        Assert.Equal(string.Empty, LocalizeHelpers.Format("Auth.License.EndingIn", AvaloniaProperty.UnsetValue));
        Assert.Equal(string.Empty, LocalizeHelpers.Format("SmartActions.LastRun.Format", "today", AvaloniaProperty.UnsetValue));
        Assert.Equal(string.Empty, LocalizeHelpers.Format("SmartActions.LastRun.Format", ErrorNotification, 2));
    }

    [Fact]
    public void LocalizeSwitchSelectsTrueOrFalseKey()
    {
        Assert.Equal("Enabled", LocalizeHelpers.Switch(true, "Common.Enabled", "Common.Disabled"));
        Assert.Equal("Disabled", LocalizeHelpers.Switch(false, "Common.Enabled", "Common.Disabled"));

        var svc = new LocalizationService(new GlobalSettings { Language = "Japanese" });
        Assert.Equal(LocalizationService.Translate("ja", "Common.Save"), svc.Switch(true, "Common.Save", "Common.Cancel"));
        Assert.Equal(LocalizationService.Translate("ja", "Common.Cancel"), svc.Switch(false, "Common.Save", "Common.Cancel"));
        Assert.Equal("Save", svc.Fallback("Save", "Common.Cancel"));
        Assert.Equal(LocalizationService.Translate("ja", "Common.Cancel"), svc.Fallback("", "Common.Cancel"));
        Assert.Equal(LocalizationService.Translate("ja", "Analytics.TimeSpan.Year"), svc.Enum("Analytics.TimeSpan.", "Year"));
        Assert.Equal(LocalizationService.Translate("ja", "SmartActions.Actions.MoreFormat").Replace("{0}", "A").Replace("{1}", "2"),
            svc.Format("SmartActions.Actions.MoreFormat", "A", 2));
    }

    [Fact]
    public void HistoryWindowAndAccountViewUseLocalizationHelpers()
    {
        Assert.Equal("All smart actions - Logs", HistoryWindow.FormatLogsTitle(null));
        Assert.Equal("All smart actions - Logs", HistoryWindow.FormatLogsTitle(string.Empty));
        Assert.Equal("Drop Watcher - Logs", HistoryWindow.FormatLogsTitle("Drop Watcher"));
        Assert.Equal("1 Account Group Loaded", Cybersole.Ui.Views.Accounts.AccountView.GroupsLoaded(1));
        Assert.Equal("3 Account Groups Loaded", Cybersole.Ui.Views.Accounts.AccountView.GroupsLoaded(3));
        Assert.Equal("1 ACCOUNT SELECTED", Cybersole.Ui.Views.Accounts.AccountView.SelectionCaption(1));
        Assert.Equal("2 ACCOUNTS SELECTED", Cybersole.Ui.Views.Accounts.AccountView.SelectionCaption(2));
    }
}
