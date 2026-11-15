import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
code = '''using Cybersole.Ui.Views.Proxies;
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
        Assert.Equal("Are you sure you want to delete {0} proxies?\\nYou cannot undo this action.",
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
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('tests written')
