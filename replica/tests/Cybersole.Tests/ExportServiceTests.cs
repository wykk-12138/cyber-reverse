using Cybersole.Core.Store;
using Cybersole.Services;
using Xunit;

namespace Cybersole.Tests;

public class ExportServiceTests
{
    private static CheckoutEvent Evt(string product = "Jordan 1", string price = "180.00",
        bool success = true, string? order = "A123", string store = "shopify", string size = "10")
        => new(store, product, size, price, success, order, "Profile A");

    [Fact]
    public void Csv_Has_Header_And_One_Row_Per_Event()
    {
        var csv = ExportService.BuildCheckoutCsv(new[] { Evt(), Evt(product: "Dunk Low") });
        var lines = csv.TrimEnd().Split('\n');

        Assert.Equal(3, lines.Length);
        Assert.StartsWith("timestamp,store,product", lines[0]);
    }

    [Fact]
    public void Csv_Quotes_Values_Containing_Commas()
    {
        var csv = ExportService.BuildCheckoutCsv(new[] { Evt(product: "Jordan 1, Retro") });
        Assert.Contains("\"Jordan 1, Retro\"", csv);
    }

    [Fact]
    public void Csv_Escapes_Embedded_Quotes()
    {
        var csv = ExportService.BuildCheckoutCsv(new[] { Evt(product: "Air \"Max\" 90") });
        Assert.Contains("\"Air \"\"Max\"\" 90\"", csv);
    }

    [Fact]
    public void Csv_Writes_Boolean_And_Empty_Order()
    {
        var csv = ExportService.BuildCheckoutCsv(new[] { Evt(success: false, order: null) });
        Assert.Contains(",false,", csv);
    }

    [Fact]
    public void ExportToFile_Creates_File()
    {
        var dir = Path.Combine(Path.GetTempPath(), "cyb-export-" + Guid.NewGuid().ToString("N"));
        try
        {
            var path = ExportService.ExportToFile(new[] { Evt() }, dir);
            Assert.True(File.Exists(path));
            Assert.Contains("Jordan 1", File.ReadAllText(path));
        }
        finally
        {
            if (Directory.Exists(dir)) Directory.Delete(dir, true);
        }
    }
}
