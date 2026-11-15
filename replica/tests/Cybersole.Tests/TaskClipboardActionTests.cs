using Cybersole.Core.Models;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R372: the two clipboard actions on the tasks page, with the image's own failure wording.
///
/// <para>
/// The locale states both flows in full: "Link Change" fails with "Invalid URL" /
/// "The value retrieved from clipboard is not a valid URL."; "Quicktask" fails with "Invalid Quicktask" /
/// "The value retrieved from clipboard is not a valid Quicktask format." Both read the clipboard, which is why
/// <see cref="TaskView.Clipboard"/> is a seam — a test drives them without a real clipboard.
/// </para>
/// </summary>
public sealed class TaskClipboardActionTests
{
    private readonly ITestOutputHelper _out;
    public TaskClipboardActionTests(ITestOutputHelper output) => _out = output;

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("not a url")]
    [InlineData("ftp://example.com/x")]
    public void LinkChangeRejectsAnythingThatIsNotAWebUrl(string? clipboard)
    {
        using var services = TestServices.Create();
        var view = new TaskView(services) { Clipboard = () => clipboard };

        var result = view.LinkChangeCore();

        _out.WriteLine(result);
        Assert.StartsWith(TaskView.InvalidLinkChangeTitle, result);
        Assert.Contains(TaskView.InvalidLinkChangeMessage, result);
    }

    [Fact]
    public void LinkChangeAcceptsAWebUrl()
    {
        using var services = TestServices.Create();
        var view = new TaskView(services) { Clipboard = () => "https://store.example/p/1" };

        var result = view.LinkChangeCore();

        _out.WriteLine(result);
        Assert.DoesNotContain("Invalid", result);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("no separator here")]
    public void QuicktaskRejectsWhatIsNotAQuicktask(string? clipboard)
    {
        using var services = TestServices.Create();
        var view = new TaskView(services) { Clipboard = () => clipboard };

        var result = view.QuicktaskCore();

        _out.WriteLine(result);
        Assert.StartsWith(TaskView.InvalidQuicktaskTitle, result);
        Assert.Contains(TaskView.InvalidQuicktaskMessage, result);
    }

    [Fact]
    public void TheFailureWordingIsTheImagesWording()
    {
        Assert.Equal("Invalid URL", TaskView.InvalidLinkChangeTitle);
        Assert.Equal("The value retrieved from clipboard is not a valid URL.", TaskView.InvalidLinkChangeMessage);
        Assert.Equal("Invalid Quicktask", TaskView.InvalidQuicktaskTitle);
        Assert.Equal("The value retrieved from clipboard is not a valid Quicktask format.", TaskView.InvalidQuicktaskMessage);
    }
}
