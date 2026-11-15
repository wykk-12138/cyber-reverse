import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CopyTablesHygieneTests.cs"
code = '''using System.Collections.Generic;
using System.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R425: one guard over every copy table, so a new table cannot ship an empty or duplicated value.
///
/// <para>
/// Seven tables now carry the image's wording (ProfileCsv, Utilities, TaskCreator, SmartActions, Data, Auth, HistoryWindow,
/// Settings, Analytics). Each entry is `short name → text`; an empty text or two names pointing at the same text is a data
/// error, not a style question. This test walks them all and reports the counts.
/// </para>
/// </summary>
public sealed class CopyTablesHygieneTests
{
    private readonly ITestOutputHelper _out;
    public CopyTablesHygieneTests(ITestOutputHelper output) => _out = output;

    private static IEnumerable<(string Owner, IReadOnlyDictionary<string, string> Table)> Tables() => new[]
    {
        ("ProfileCsvEditorView", Cybersole.Ui.Views.Profiles.ProfileCsvEditorView.Copy),
        ("UtilitiesView", Cybersole.Ui.Views.Utilities.UtilitiesView.Copy),
        ("TaskCreatorView", Cybersole.Ui.Views.Tasks.TaskCreatorView.Copy),
        ("SmartActionsView", Cybersole.Ui.Views.SmartActions.SmartActionsView.Copy),
        ("DataView", Cybersole.Ui.Views.Settings.DataView.Copy),
        ("LoginControl", Cybersole.Ui.Views.Auth.LoginControl.Copy),
        ("HistoryWindow", Cybersole.Ui.Views.SmartActions.HistoryWindow.Copy),
        ("SettingsShell", Cybersole.Ui.Views.Settings.SettingsShell.Copy),
        ("CheckoutView", Cybersole.Ui.Views.Analytics.CheckoutView.Copy),
    };

    [Fact]
    public void NoTableShipsAnEmptyString()
    {
        foreach (var (owner, table) in Tables())
        {
            var empty = table.Where(kv => string.IsNullOrWhiteSpace(kv.Value)).Select(kv => kv.Key).ToList();
            _out.WriteLine($"{owner}: {table.Count} entries, empty: {empty.Count}");
            Assert.Empty(empty);
        }
    }

    [Fact]
    public void TheTablesTogetherHoldAtLeastTwoHundredStrings()
    {
        var total = Tables().Sum(t => t.Table.Count);
        _out.WriteLine("total captured strings: " + total);
        Assert.True(total >= 200, "expected at least 200 captured strings, got " + total);
    }

    [Fact]
    public void ShortNamesAreUniqueWithinEachTable()
    {
        foreach (var (owner, table) in Tables())
        {
            var dupes = table.Keys.Count() - table.Keys.Distinct().Count();
            Assert.True(dupes == 0, owner + " has duplicate keys");
        }
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('hygiene test written')
