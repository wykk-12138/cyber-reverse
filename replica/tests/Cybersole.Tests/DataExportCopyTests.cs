using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R349: the export result copy comes from the locale, not from a sentence written here.
///
/// <para>
/// The image carries <c>Data.Export.Fail.Title</c> = "Export Fail", <c>Data.Export.Fail.Message</c> =
/// "Failed to export data." and an <c>Data.Export.Success.*</c> pair. The replica used to print a home-grown
/// "Export failed: {exception}"; the failure line now leads with the title the window would show.
/// </para>
/// </summary>
public sealed class DataExportCopyTests
{
    private readonly ITestOutputHelper _out;
    public DataExportCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheFailureCopyIsTheLocaleText()
    {
        _out.WriteLine(DataView.ExportFailTitle + " / " + DataView.ExportFailMessage);

        Assert.Equal("Export Fail", DataView.ExportFailTitle);
        Assert.Equal("Failed to export data.", DataView.ExportFailMessage);
        Assert.Equal("Export Success", DataView.ExportSuccessTitle);
    }
}
