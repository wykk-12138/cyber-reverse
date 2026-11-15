using System.Linq;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R412: the TaskCreator.* strings that had no counterpart, captured verbatim in one table.
///
/// <para>
/// <c>python tools/locale_text_gap.py TaskCreator</c> reported 19 missing values — every "select"/"multiple" placeholder the
/// creator shows when a field holds more than one value, plus the create/save buttons and the monitor-input row.
/// </para>
/// </summary>
public sealed class TaskCreatorCopyTests
{
    private readonly ITestOutputHelper _out;
    public TaskCreatorCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheTableHoldsTheNineteenStrings()
    {
        _out.WriteLine(string.Join(", ", TaskCreatorView.Copy.Keys.OrderBy(k => k)));
        Assert.Equal(19, TaskCreatorView.Copy.Count);
        Assert.DoesNotContain(string.Empty, TaskCreatorView.Copy.Values);
    }

    [Theory]
    [InlineData("CreateTask", "Create Task")]
    [InlineData("CreateTasksFormat", "Create {0} Tasks")]
    [InlineData("MonitorInputFormat", "Enter {0}")]
    [InlineData("MonitorInputMultiple", "Multiple inputs")]
    [InlineData("StoreSelect", "Select store")]
    [InlineData("SizeMultiple", "Multiple sizes")]
    public void TheWordingIsTheImagesWording(string name, string expected)
    {
        Assert.Equal(expected, TaskCreatorView.Text(name));
    }

    [Fact]
    public void TheSmartActionTableHoldsItsStringsAndForms()
    {
        // R413: SmartActions.* table plus the filters caption's zero / one / many forms.
        var copy = Cybersole.Ui.Views.SmartActions.SmartActionsView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(13, copy.Count);
        Assert.Equal("New Action", Cybersole.Ui.Views.SmartActions.SmartActionsView.Text("NewAction"));
        Assert.Equal("Smart Actions ({0})", Cybersole.Ui.Views.SmartActions.SmartActionsView.Text("HeaderFormat"));

        Assert.Equal("No Filters", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(0));
        Assert.Equal("1 Filter", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(1));
        Assert.Equal("4 Filters", Cybersole.Ui.Views.SmartActions.SmartActionsView.FiltersCaption(4));
    }

    [Fact]
    public void TheDataPageTableHoldsItsStrings()
    {
        // R414: the Data.* family — backup / import / restore / reset, all in the image's words.
        var copy = Cybersole.Ui.Views.Settings.DataView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(15, copy.Count);
        Assert.Equal("Backup Success", Cybersole.Ui.Views.Settings.DataView.Text("BackupTitle"));
        Assert.Equal("This file type is unsupported. Please import a JSON file.",
            Cybersole.Ui.Views.Settings.DataView.Text("ImportUnsupportedJson"));
        Assert.Equal("Restored Successfully", Cybersole.Ui.Views.Settings.DataView.Text("RestoreSuccessTitle"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Settings.DataView.Text("nope"));
    }

    [Fact]
    public void TheAnalyticsTablesHoldTheirStrings()
    {
        // R415: Checkout.* and Release.* — the five words the analytics pages were missing.
        var copy = Cybersole.Ui.Views.Analytics.CheckoutView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(5, copy.Count);
        Assert.Equal("Order {0}", Cybersole.Ui.Views.Analytics.CheckoutView.Text("OrderFormat"));
        Assert.Equal("Out for delivery", Cybersole.Ui.Views.Analytics.CheckoutView.Text("OutForDelivery"));
        Assert.Equal("Scheduled Delivery", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ScheduledDelivery"));
        Assert.Equal("Add Tasks", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ReleaseAddTasks"));
        Assert.Equal("Check back later", Cybersole.Ui.Views.Analytics.CheckoutView.Text("ReleaseEmptyCheckBack"));
    }

    [Fact]
    public void TheSettingsTableHoldsTheCapturedStrings()
    {
        // R416: 54 Settings.* values were missing; 52 were capturable in one pass and 2 long delete-confirm messages were
        // added by hand. The one key still absent is truncated in the pool ("…when using the \").
        var copy = Cybersole.Ui.Views.Settings.SettingsShell.Copy;
        _out.WriteLine($"{copy.Count} strings");

        Assert.True(copy.Count >= 54, "expected at least 54 captured settings strings, got " + copy.Count);
        Assert.Equal("Add Source", Cybersole.Ui.Views.Settings.SettingsShell.Text("AddSource"));
        Assert.Equal("Balance ${0}", Cybersole.Ui.Views.Settings.SettingsShell.Text("BalanceFormat"));
        Assert.Equal("Disconnect AYCD Inbox", Cybersole.Ui.Views.Settings.SettingsShell.Text("Title"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Settings.SettingsShell.Text("nope"));
    }

    [Fact]
    public void TheAuthAndHistoryTablesHoldTheirStrings()
    {
        // R421: Auth (15 + the Back to login leftover) and HistoryWindow (8 + Clear History).
        var auth = Cybersole.Ui.Views.Auth.LoginControl.Copy;
        var history = Cybersole.Ui.Views.SmartActions.HistoryWindow.Copy;
        _out.WriteLine($"auth {auth.Count}, history {history.Count}");

        Assert.Equal(16, auth.Count);
        Assert.Equal(9, history.Count);
        Assert.Equal("License Selector", Cybersole.Ui.Views.Auth.LoginControl.CopyText("LicenseTitle"));
        Assert.Equal("Back to login", Cybersole.Ui.Views.Auth.LoginControl.CopyText("BackToLogin"));
        Assert.Equal("Search history", Cybersole.Ui.Views.SmartActions.HistoryWindow.Text("SearchPlaceholder"));
        Assert.Equal("Clear History", Cybersole.Ui.Views.SmartActions.HistoryWindow.Text("Clear"));
    }
}
