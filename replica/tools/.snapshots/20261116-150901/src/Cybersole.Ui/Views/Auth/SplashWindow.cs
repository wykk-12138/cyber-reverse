using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Threading;
using Cybersole.Services.Localization;

namespace Cybersole.Ui.Views.Auth;

/// <summary>
/// The start-up window (R214). The original ships it as a XAML resource — the image carries
/// <c>avares://Cybersole/Views/Auth/SplashWindow.axaml</c> plus the two control names inside it,
/// <c>SplashBackground</c> and <c>SplashCyberIcon</c> — and its copy is the locale's
/// <c>Auth.Welcome</c>: <i>"Welcome to Cybersole 5.0"</i>.
///
/// <para>
/// This replica used to go straight to <c>MainWindow</c>, which is why <c>SplashWindow</c> sat in the not-built list.
/// It is now shown first and hands over as soon as the main window reports itself ready (or after
/// <see cref="MinimumVisible"/>, so a fast machine still shows the brand rather than a flash).
/// </para>
///
/// <para>
/// The two named elements are real controls with those names, because the original's XAML names them and anything that
/// looks them up (a test, a theme) should find them.
/// </para>
/// </summary>
public sealed class SplashWindow : Window
{
    /// <summary>The headline, from the locale key the window binds.</summary>
    public const string WelcomeKey = "Auth.Welcome";

    /// <summary>
    /// How long the splash stays even when start-up is instant. Measured on the running build (R220): the window is up
    /// from 607 ms and still up at 4351 ms, i.e. it follows start-up rather than a fixed timer. The floor only stops a
    /// fast start from flashing it; the exit is the shell's <c>Opened</c> event.
    /// </summary>
    public static readonly TimeSpan MinimumVisible = TimeSpan.FromMilliseconds(1200);

    private readonly TextBlock _status = new() { Opacity = 0.7, FontSize = 12 };

    public SplashWindow(string? version = null, string? language = null)
        : this(BuildVisual(LocalizationService.Translate(language, WelcomeKey), version).Background,
               LocalizationService.Translate(language, WelcomeKey), version)
    {
    }

    private SplashWindow(Border background, string welcome, string? version)
    {
        Title = "Cybersole";
        // R217: measured by polling the process's window rects from launch — the splash is 529x630 (portrait),
        // titled "Cybersole" like the shell. It was 460x260, which was a guess.
        Width = 529;
        Height = 630;
        CanResize = false;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        SystemDecorations = SystemDecorations.None;
        Background = new SolidColorBrush(Color.FromRgb(18, 20, 28));

        Background1 = background;
        Content = Background1;
    }

    /// <summary>The named background element the original's XAML declares.</summary>
    public Border Background1 { get; }

    /// <summary>
    /// Builds the splash's visual tree without a <see cref="Window"/>, so a headless test can read it — constructing a
    /// window needs a platform, and the interesting part of this control is the named elements and the copy.
    /// </summary>
    public static (Border Background, StackPanel Stack, TextBlock Version) BuildVisual(
        string welcome, string? version)
    {
        var background = new Border
        {
            Name = "SplashBackground",
            Background = new LinearGradientBrush
            {
                StartPoint = new RelativePoint(0, 0, RelativeUnit.Relative),
                EndPoint = new RelativePoint(1, 1, RelativeUnit.Relative),
                GradientStops =
                {
                    new GradientStop(Color.FromRgb(18, 20, 28), 0),
                    new GradientStop(Color.FromRgb(28, 34, 52), 1),
                },
            },
        };

        var icon = new Border
        {
            Name = "SplashCyberIcon",
            Width = 84,
            Height = 84,
            CornerRadius = new CornerRadius(42),
            BorderThickness = new Thickness(2),
            BorderBrush = new SolidColorBrush(Color.FromArgb(120, 120, 200, 160)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Child = new TextBlock
            {
                Text = "C",
                FontSize = 40,
                FontWeight = FontWeight.Bold,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };

        var headline = new TextBlock
        {
            Text = welcome,
            FontSize = 18,
            FontWeight = FontWeight.SemiBold,
            HorizontalAlignment = HorizontalAlignment.Center,
        };

        var versionLine = new TextBlock
        {
            Text = string.IsNullOrWhiteSpace(version) ? string.Empty : "Version " + version,
            Opacity = 0.7,
            FontSize = 12,
        };

        var stack = new StackPanel
        {
            Spacing = 10,
            VerticalAlignment = VerticalAlignment.Center,
            HorizontalAlignment = HorizontalAlignment.Center,
            Children = { icon, headline, versionLine },
        };

        background.Child = stack;
        return (background, stack, versionLine);
    }

    /// <summary>The version line, once start-up knows it.</summary>
    public string StatusText
    {
        get => _status.Text ?? string.Empty;
        set => _status.Text = value;
    }

    /// <summary>
    /// Shows the splash, runs <paramref name="startup"/>, then continues. The splash closes on the UI thread after
    /// <see cref="MinimumVisible"/> at the earliest, so the hand-over is never a flicker.
    /// </summary>
    public static async Task ShowWhile(Func<Task> startup, string? version = null, string? language = null)
    {
        var splash = new SplashWindow(version, language);
        splash.Show();

        var started = DateTime.UtcNow;
        try
        {
            await startup().ConfigureAwait(true);
        }
        finally
        {
            var elapsed = DateTime.UtcNow - started;
            if (elapsed < MinimumVisible)
                await Task.Delay(MinimumVisible - elapsed).ConfigureAwait(true);

            await Dispatcher.UIThread.InvokeAsync(splash.Close);
        }
    }
}
