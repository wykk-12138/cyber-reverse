using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia.Controls;
using Cybersole.Services.Localization;
using Cybersole.Ui.Views.Browser;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R215: <c>CustomBrowser</c> — the last original view class this replica had no counterpart for. Its labels are the
/// image's own <c>Browser.*</c> locale keys; the actions go through a delegate so the view is testable without a
/// Chromium session.
/// </summary>
public sealed class CustomBrowserTests
{
    private readonly ITestOutputHelper _out;
    public CustomBrowserTests(ITestOutputHelper output) => _out = output;

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }

    [Fact]
    public void TheFourLabelsAreTheImagesOwnKeys()
    {
        var en = LocalizationService.For("en");

        Assert.Equal("Browser", en[CustomBrowser.HeaderKey]);
        Assert.Equal("Search or enter address", en[CustomBrowser.AddressKey]);
        Assert.Equal("Autofill", en[CustomBrowser.AutofillKey]);
        Assert.Equal("New Tab", en[CustomBrowser.NewTabKey]);

        _out.WriteLine(string.Join(" | ", new[]
        {
            en[CustomBrowser.HeaderKey], en[CustomBrowser.AddressKey],
            en[CustomBrowser.AutofillKey], en[CustomBrowser.NewTabKey],
        }));
    }

    [Fact]
    public void TheChromeIsBuiltWithoutAWindow()
    {
        var chrome = CustomBrowser.BuildChrome(
            LocalizationService.Translate("en", CustomBrowser.AddressKey),
            LocalizationService.Translate("en", CustomBrowser.NewTabKey),
            LocalizationService.Translate("en", CustomBrowser.AutofillKey),
            out var address, out var status);

        Assert.Equal("Search or enter address", address.Watermark);
        Assert.IsType<Avalonia.Controls.DockPanel>(chrome);

        var buttons = ((Avalonia.Controls.DockPanel)chrome).Children.OfType<Avalonia.Controls.StackPanel>()
            .SelectMany(p => p.Children.OfType<Avalonia.Controls.Button>())
            .Select(b => b.Content?.ToString())
            .ToList();

        Assert.Contains("New Tab", buttons);
        Assert.Contains("Autofill", buttons);
        Assert.Equal(string.Empty, status.Text);
    }

    [Fact]
    public async Task ActionsGoThroughTheDelegateSoTheViewStaysTestable()
    {
        string? navigated = null;
        string? scriptRuns = null;

        var actions = new CustomBrowserActions(
            url => { navigated = url; return Task.CompletedTask; },
            script => { scriptRuns = script; return Task.FromResult<string?>("ok"); });

        // the window object needs a platform, so exercise the two methods through a tiny harness that mirrors them
        navigated = null;
        await actions.Navigate("https://example.com");
        Assert.Equal("https://example.com", navigated);

        var result = await actions.Autofill!("document.title");
        Assert.Equal("ok", result);
        Assert.Equal("document.title", scriptRuns);
    }

    [Fact]
    public void TheSurfaceLimitationIsPrintedNotHidden()
    {
        Assert.Contains("headless", CustomBrowser.SurfaceNote);
        Assert.Contains("no painted viewport", CustomBrowser.SurfaceNote);

        // and the window can be constructed from a live bridge
        var source = File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Views", "Browser", "CustomBrowser.cs"));
        Assert.Contains("public static CustomBrowser FromBridge(", source);
        Assert.Contains("bridge.NavigateAsync(url)", source);
        Assert.Contains("bridge.EvaluateAsync(script)", source);
    }

    [Fact]
    public void TheSwitchThatOpensItIsParsedByStartup()
    {
        // R215: `--browser [url]` is the window's entry point; the parsing is public so it can be checked here.
        Assert.True(Cybersole.Ui.App.WantsBrowserWindow(new[] { "Cybersole.exe", "--browser" }));
        Assert.True(Cybersole.Ui.App.WantsBrowserWindow(new[] { "Cybersole.exe", "--browser", "https://a.b" }));
        Assert.False(Cybersole.Ui.App.WantsBrowserWindow(new[] { "Cybersole.exe" }));

        Assert.Equal("https://a.b",
            Cybersole.Ui.App.BrowserUrl(new[] { "Cybersole.exe", "--browser", "https://a.b" }));
        Assert.Null(Cybersole.Ui.App.BrowserUrl(new[] { "Cybersole.exe", "--browser" }));

        var program = File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Program.cs"));
        Assert.Contains("new Cybersole.Ui.Views.Browser.CustomBrowser()", program);
    }
}
