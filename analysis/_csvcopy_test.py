import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ProfileCsvCopyTests.cs"
code = '''using System.Linq;
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
        Assert.Equal(39, ProfileCsvEditorView.Copy.Count);
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
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('test written')
