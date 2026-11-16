using System.Linq;
using Cybersole.Ui.Views.Profiles;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R410: the whole <c>ProfileCsv.*</c> family captured verbatim (39 strings) in one table.
///
/// <para>
/// <c>python tools/locale_text_gap.py ProfileCsv</c> listed 33 values with no counterpart in the source. They are now a
/// dictionary on <see cref="ProfileCsvEditorView"/> keyed by short names, each line carrying the locale key it came from.
/// Two keys stay out: <c>ProfileCsv.Error.UnknownCountry</c> and <c>.UnknownState</c> are TRUNCATED in the string pool
/// (their values end with a backslash), so writing them would mean inventing the rest.
/// </para>
/// </summary>
public sealed class ProfileCsvCopyTests
{
    private readonly ITestOutputHelper _out;
    public ProfileCsvCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheTableHoldsEveryCapturedString()
    {
        _out.WriteLine(string.Join(", ", ProfileCsvEditorView.Copy.Keys.OrderBy(k => k)));
        // R552: ProfileCsv.HintText was added to the editor table, so it grew from 39 to 40.
        // R704: the country/state validation messages are now referenced by code, so it grew from 40 to 42.
        // Both keys existed in the image all along -- what was missing was anything that emitted them.
        Assert.Equal(42, ProfileCsvEditorView.Copy.Count);
        Assert.DoesNotContain(string.Empty, ProfileCsvEditorView.Copy.Values);
    }

    [Theory]
    [InlineData("Title", "CSV Editor")]
    [InlineData("Apply", "Apply Changes")]
    [InlineData("Import", "Import CSV")]
    [InlineData("Export", "Export CSV")]
    [InlineData("MenuFillDown", "Fill Down")]
    [InlineData("StatusNoHeader", "The CSV needs a header row with known column names")]
    [InlineData("ErrorNameRequired", "Profile name is required")]
    [InlineData("SummaryNone", "No changes")]
    public void TheWordingIsTheImagesWording(string name, string expected)
    {
        Assert.Equal(expected, ProfileCsvEditorView.Text(name));
    }

    [Fact]
    public void AnUnknownNameIsEmptyRatherThanThrowing()
    {
        Assert.Equal(string.Empty, ProfileCsvEditorView.Text("no-such-string"));
    }

    [Fact]
    public void TheUtilitiesTableHoldsItsStringsToo()
    {
        // R411: same pattern, the Utilities.StoreGroups.* family.
        var copy = Cybersole.Ui.Views.Utilities.UtilitiesView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        // R549: two delete-message templates were added (DeleteMessageFormat / DeleteUsedMessageFormat), so the
        // table grew from 18 to 20. Bumping the expected count is the guard's job: it exists so that a silent
        // change to the copy table cannot go unnoticed.
        Assert.Equal(20, copy.Count);
        Assert.Equal("Utilities", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("Title"));
        Assert.Equal("Store Groups", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("StoreGroupsTitle"));
        Assert.Equal("Add a store", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("ModalStoresPlaceholder"));
        Assert.Equal("Enter a group name", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("ModalErrorNoName"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Utilities.UtilitiesView.Text("nope"));
    }
}
