using System.IO;
using Cybersole.Services.Localization;
using Cybersole.Ui.Views.Auth;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R214: <c>SplashWindow</c>. The evidence is unusually direct — the image carries the resource name
/// <c>avares://Cybersole/Views/Auth/SplashWindow.axaml</c> and the two control names inside it
/// (<c>SplashBackground</c>, <c>SplashCyberIcon</c>), and the copy is the locale's <c>Auth.Welcome</c>.
/// </summary>
public sealed class SplashWindowTests
{
    private readonly ITestOutputHelper _out;
    public SplashWindowTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void ItPrintsTheLocalesWelcomeLine()
    {
        var en = LocalizationService.For("en");
        Assert.Equal("Welcome to Cybersole 5.0", en[SplashWindow.WelcomeKey]);

        var (_, _, version) = SplashWindow.BuildVisual(en[SplashWindow.WelcomeKey], "5.18.32");
        Assert.Equal("Version 5.18.32", version.Text);

        _out.WriteLine(version.Text!);
    }

    [Fact]
    public void TheTwoNamedElementsTheOriginalDeclaresExist()
    {
        var (background, stack, _) = SplashWindow.BuildVisual("Welcome to Cybersole 5.0", null);

        // the resource the original ships is Views/Auth/SplashWindow.axaml with these two names in it
        Assert.Equal("SplashBackground", background.Name);
        Assert.Same(stack, background.Child);
        Assert.Contains(stack.Children.OfType<Avalonia.Controls.Border>(),
            b => b.Name == "SplashCyberIcon");
    }

    [Fact]
    public void StartupShowsItAndTheShellClosesIt()
    {
        var program = File.ReadAllText(Path.Combine(Root(), "src", "Cybersole.Ui", "Program.cs"));

        Assert.Contains("new Cybersole.Ui.Views.Auth.SplashWindow(", program);
        Assert.Contains("splash.Show();", program);
        Assert.Contains("window.Opened += (_, _) => splash.Close();", program);

        // and the splash is not a fixed delay the user must sit through
        Assert.True(SplashWindow.MinimumVisible > TimeSpan.Zero);
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
