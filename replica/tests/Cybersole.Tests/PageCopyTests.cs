using Cybersole.Ui.Views.Profiles;
using Cybersole.Ui.Views.Proxies;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R393: the Proxies page copy, verbatim from the image's locale (Proxies.* in the string table) — the same exercise as
/// AccountCopyTests, driven by <c>python tools/locale_text_gap.py Proxies</c>.
/// </summary>
public sealed class PageCopyTests
{
    private readonly ITestOutputHelper _out;
    public PageCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheProxyDeleteConfirmationIsTheImagesWording()
    {
        Assert.Equal("Delete {0} proxies?", ProxyView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} proxies?\nYou cannot undo this action.",
            ProxyView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) proxies", ProxyView.DeleteConfirmActionFormat);
    }

    [Theory]
    [InlineData(0, "0 Proxies Loaded")]
    [InlineData(2, "2 Proxies Loaded")]
    public void TheProxyFooterIsTheImagesWording(int count, string expected)
    {
        _out.WriteLine(ProxyView.Loaded(count));
        Assert.Equal(expected, ProxyView.Loaded(count));
    }

    [Theory]
    [InlineData(1, "1 PROXY SELECTED")]
    [InlineData(5, "5 PROXIES SELECTED")]
    public void TheProxySelectionCounterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(ProxyView.SelectionCaption(count));
        Assert.Equal(expected, ProxyView.SelectionCaption(count));
    }

    [Fact]
    public void TheTaskDeleteConfirmationIsTheImagesWording()
    {
        Assert.Equal("Delete {0} tasks?", TaskView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} tasks?\nYou cannot undo this action.",
            TaskView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) tasks", TaskView.DeleteConfirmActionFormat);
        Assert.Equal("Copy URL", TaskView.ContextCopyUrl);
        Assert.Equal("Move tasks to", TaskView.ContextMoveTo);
    }

    [Fact]
    public void TheTaskEmptySearchLineIsTheImagesLine()
    {
        Assert.Equal("There are no tasks matching your search", TaskView.NoResultsSubtitle);
        Assert.Equal("Multiple Products ({0})", TaskView.MultipleProductsFormat);
    }

    [Theory]
    [InlineData(1, "1 TASK SELECTED")]
    [InlineData(6, "6 TASKS SELECTED")]
    public void TheTaskSelectionCounterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(TaskView.SelectionCaption(count));
        Assert.Equal(expected, TaskView.SelectionCaption(count));
    }

    [Theory]
    [InlineData(0, "0 Selected")]
    [InlineData(3, "3 Selected")]
    public void TheGridCounterIsTheImagesWording(int count, string expected)
    {
        _out.WriteLine(TaskView.GridSelected(count));
        Assert.Equal(expected, TaskView.GridSelected(count));
    }

    [Fact]
    public void TheProfileContextMenuIsTheImagesWording()
    {
        Assert.Equal("Clone Profiles", ProfileView.ContextClone);
        Assert.Equal("Create Test Profile", ProfileView.ContextCreateTest);
        Assert.Equal("Open in CSV Editor", ProfileView.ContextCsvEditor);
        Assert.Equal("Delete Profiles", ProfileView.ContextDelete);
        Assert.Equal("Edit Profiles", ProfileView.ContextEdit);
    }

    [Fact]
    public void TheProfileDeleteConfirmationIsTheImagesWording()
    {
        Assert.Equal("Delete {0} profiles?", ProfileView.DeleteConfirmTitleFormat);
        Assert.Equal("Are you sure you want to delete {0} profiles?\nYou cannot undo this action.",
            ProfileView.DeleteConfirmMessageFormat);
        Assert.Equal("Delete ({0}) profiles", ProfileView.DeleteConfirmActionFormat);
        Assert.Equal("There are no profiles matching your search", ProfileView.NoResultsSubtitle);
    }

    [Theory]
    [InlineData(0, "No Profiles Loaded")]
    [InlineData(1, "1 Profile Loaded")]
    [InlineData(4, "4 Profiles Loaded")]
    public void TheProfileFooterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(ProfileView.Loaded(count));
        Assert.Equal(expected, ProfileView.Loaded(count));
    }

    [Theory]
    [InlineData(1, "1 PROFILE SELECTED")]
    [InlineData(2, "2 PROFILES SELECTED")]
    public void TheProfileSelectionCounterSplitsOnOne(int count, string expected)
    {
        _out.WriteLine(ProfileView.SelectionCaption(count));
        Assert.Equal(expected, ProfileView.SelectionCaption(count));
    }

    [Fact]
    public void TheGroupDialogLabelsAreTheImagesLabels()
    {
        // the image capitalises these; the dialog used to print "Monitor delay" / "Cloudflare solver"
        Assert.Equal("Monitor Delay", TaskGroupView.MonitorDelayLabel);
        Assert.Equal("Error Delay", TaskGroupView.ErrorDelayLabel);
        Assert.Equal("Total Checkout Limit", TaskGroupView.TotalCheckoutLimitLabel);
        Assert.Equal("Resetting at", TaskGroupView.ResettingAtLabel);
        Assert.Equal("Captcha Solving Source", TaskGroupView.CaptchaSourceLabel);
        Assert.Equal("Cloudflare Solver", TaskGroupView.CloudflareSolverLabel);
        Assert.Equal("Webhook Filter", TaskGroupView.WebhookFilterLabel);
    }

    [Fact]
    public void TheGroupTooltipsAndPlaceholdersAreTheImagesWords()
    {
        Assert.Equal("When toggled, both monitor and retry delays will stay the same", TaskGroupView.LinkTooltip);
        Assert.Equal("Select source", TaskGroupView.CaptchaSourceSelect);
        Assert.Equal("Select webhook(s)", TaskGroupView.WebhookFilterSelect);
    }

    [Fact]
    public void TheTwoRemainingCountersAreTheImagesWords()
    {
        // R409: ProfileCsv.Menu.SelectedCells and Utilities.StoreGroups.CountFormat were the last caption keys with no
        // counterpart anywhere in the source.
        Assert.Equal("{0} CELLS SELECTED", ProfileCsvEditorView.SelectedCellsFormat);
        Assert.Equal("3 CELLS SELECTED", ProfileCsvEditorView.SelectedCells(3));
        Assert.Equal("{0} stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCountFormat);
        Assert.Equal("2 stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(2));
        Assert.Equal("No stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(0));
        Assert.Equal("1 store", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(1));
    }

    [Fact]
    public void TheMonitorPageCarriesTheSevenStringsAndItsSizesCaption()
    {
        // R423: Monitor.* was the last locale family with no host class. The page now exists with ONLY the wording the
        // image states — its inner layout is unverified, which the class remarks say out loud.
        var view = new Cybersole.Ui.Views.Monitor.MonitorView();
        _out.WriteLine($"{view.Entries.Count} entries");

        Assert.Equal("Monitor Feed", Cybersole.Ui.Views.Monitor.MonitorView.TabLabel);
        Assert.Equal("Search feed", Cybersole.Ui.Views.Monitor.MonitorView.SearchPlaceholder);
        Assert.Equal("Waiting for monitor entries", Cybersole.Ui.Views.Monitor.MonitorView.EmptyHeadline);
        Assert.Equal("New products and restocks will appear here", Cybersole.Ui.Views.Monitor.MonitorView.EmptySubtitle);
        Assert.Equal("No results", Cybersole.Ui.Views.Monitor.MonitorView.NoResultsTitle);

        Assert.Equal("Available sizes", Cybersole.Ui.Views.Monitor.MonitorView.SizesCaption(3));
        Assert.Equal("No available sizes", Cybersole.Ui.Views.Monitor.MonitorView.SizesCaption(0));

        view.SetEntries(new[] { "one", "two" });
        Assert.Equal(2, view.Entries.Count);
    }

    [Fact]
    public void TheAccountGroupDeleteConfirmationIsTheImagesWords()
    {
        // R430: the last Accounts.* value with no counterpart (the consolidated report caught it; the per-area tool had
        // counted "the {0} account group" as present because a similar sentence existed elsewhere).
        Assert.Equal("Are you sure you want to delete the {0} account group?\nYou cannot undo this action.",
            Cybersole.Ui.Views.Accounts.AccountView.DeleteGroupConfirmFormat);
        Assert.Contains("delete the Family account group?", Cybersole.Ui.Views.Accounts.AccountView.DeleteGroupConfirm("Family"));
    }
}
