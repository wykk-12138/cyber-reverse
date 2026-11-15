using System.Text.RegularExpressions;
using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Custom Stores / Custom Sizes, pinned to the live 5.18.32 pages
/// (docs/GUI_BASELINE.md).
///
/// Both pages are Shopify-only presets. Stores take a URL and derive name + currency.
/// Sizes are discovered from a product URL rather than typed in, so the URL → handle
/// extraction is the piece worth locking down.
/// </summary>
public class CustomPresetsTests
{
    [Fact]
    public void CustomStoreCarriesACurrency()
    {
        var store = new CustomStore();
        Assert.Equal("USD", store.Currency);

        store.Currency = "GBP";
        Assert.Equal("GBP", store.Currency);
    }

    [Fact]
    public void ViewsConstruct()
    {
        using var services = TestServices.Create();

        Assert.IsAssignableFrom<UserControl>(new CustomStoresView(services));
        Assert.IsAssignableFrom<UserControl>(new CustomSizesView(services));
    }

    [Theory]
    [InlineData("https://shop.example.com/products/air-max-90", "air-max-90")]
    [InlineData("https://shop.example.com/en-gb/products/air-max-90?variant=123", "air-max-90")]
    [InlineData("shop.example.com/products/air-max-90", "air-max-90")]
    public void ProductHandleIsExtractedFromTheUrl(string url, string expected)    {
        // the same regex CustomSizesView uses to build /products/{handle}.js
        var handle = Regex.Match(url, @"/products/([^/?#]+)").Groups[1].Value;
        Assert.Equal(expected, handle);
    }

    [Fact]
    public void AUrlWithoutAProductSegmentYieldsNoHandle()
    {
        var handle = Regex.Match("https://shop.example.com/collections/new",
            @"/products/([^/?#]+)").Groups[1].Value;
        Assert.Equal(string.Empty, handle);
    }
}
