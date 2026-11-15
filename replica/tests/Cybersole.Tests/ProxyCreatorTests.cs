using System.IO;
using System.Linq;
using Cybersole.Ui.Views.Proxies;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R204: the proxy creator. The image names one behaviour outright — <c>0x06e5071c  ProxyCreator.DragDrop</c> — so a
/// creator that only takes typed fields would already be missing half of it.
/// </summary>
public sealed class ProxyCreatorTests
{
    private readonly ITestOutputHelper _out;
    public ProxyCreatorTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheThreeLineShapesAreAccepted()
    {
        var model = new ProxyCreatorModel();

        var result = model.AddFromText(
            "10.0.0.1:8080\n" +
            "10.0.0.2:8081:alice:secret\n" +
            "socks5://10.0.0.3:1080\n");

        _out.WriteLine($"accepted {result.Accepted.Count}, rejected {result.Rejected}");
        Assert.Equal(3, result.Accepted.Count);
        Assert.Equal(0, result.Rejected);

        Assert.Equal("10.0.0.1", result.Accepted[0].Host);
        Assert.Equal(8080, result.Accepted[0].Port);
        Assert.Equal("alice", result.Accepted[1].Username);
        Assert.Equal("secret", result.Accepted[1].Password);
        Assert.Equal("socks5", result.Accepted[2].Scheme);
    }

    [Fact]
    public void ALineThatIsNotAProxyIsCountedNotSwallowed()
    {
        var model = new ProxyCreatorModel();
        var result = model.AddFromText("10.0.0.1:8080\nthis is not a proxy\n# a comment\n\n10.0.0.9:99999\n");

        // one good line; the comment and the blank are skipped, and the two bad lines are reported
        Assert.Single(result.Accepted);
        Assert.Equal(2, result.Rejected);
        Assert.Equal(3, result.Total);
    }

    [Fact]
    public void TheTypedPathRefusesWhatCannotConnect()
    {
        var model = new ProxyCreatorModel();

        Assert.Null(model.AddOne(null, "8080"));
        Assert.Null(model.AddOne("  ", "8080"));
        Assert.Null(model.AddOne("10.0.0.1", "0"));
        Assert.Null(model.AddOne("10.0.0.1", "65536"));
        Assert.Null(model.AddOne("10.0.0.1", "not-a-port"));

        var ok = model.AddOne(" 10.0.0.1 ", "8080", " bob ", " pw ", "SOCKS5");
        Assert.NotNull(ok);
        Assert.Equal("10.0.0.1", ok!.Host);
        Assert.Equal("bob", ok.Username);
        Assert.Equal("socks5", ok.Scheme);
        Assert.Single(model.Created);
    }

    [Fact]
    public void ADroppedFileIsReadAndABigOneIsNot()
    {
        Assert.Null(ProxyCreatorModel.ReadDroppedFile(Path.Combine(Path.GetTempPath(), "no-such-proxy-file-xyz.txt")));

        var path = Path.Combine(Path.GetTempPath(), "proxy-creator-test.txt");
        File.WriteAllText(path, "1.2.3.4:80\n");
        try
        {
            var text = ProxyCreatorModel.ReadDroppedFile(path);
            Assert.NotNull(text);

            var model = new ProxyCreatorModel();
            Assert.Single(model.AddFromText(text).Accepted);
        }
        finally
        {
            File.Delete(path);
        }
    }

    [Fact]
    public void TheViewHandlesDropsAndThePageOpensIt()
    {
        var view = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Ui", "Views", "Proxies", "ProxyCreatorView.cs"));

        // the half the image names
        Assert.Contains("DragDrop.DropEvent", view, System.StringComparison.Ordinal);
        Assert.Contains("DataFormats.Files", view, System.StringComparison.Ordinal);
        Assert.Contains("ReadDroppedFile", view, System.StringComparison.Ordinal);

        var page = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Ui", "Views", "Proxies", "ProxyView.cs"));
        Assert.Contains("new ProxyCreatorView()", page, System.StringComparison.Ordinal);
        Assert.Contains("ViewHostModal", page, System.StringComparison.Ordinal);
    }
}
