using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Themes.Fluent;
using Cybersole.Services;
using Cybersole.Stores.Modules;
using Cybersole.Ui.ViewModels;
using Cybersole.Ui.Views;

namespace Cybersole.Ui;

public sealed class App : Application
{
    public static AppServices Services { get; private set; } = null!;
    public static MainViewModel Model { get; private set; } = null!;

    public override void Initialize()
    {
        Styles.Add(new FluentTheme());
        RequestedThemeVariant = Avalonia.Styling.ThemeVariant.Dark;
    }

    public override void OnFrameworkInitializationCompleted()
    {
        Services = AppServices.Create((registry, settings) =>
        {
            StoreModuleCatalog.RegisterAll(registry);
            StoreModuleCatalog.RegisterCustom(registry, settings.CustomStores);
        });
        Model = new MainViewModel(Services);

        // full .cyb snapshot on startup and on exit (ConfigurationStore.Backup had no caller before)
        try { Services.Config.Backup(); }
        catch { /* first run / read-only profile: keep going */ }

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            // R214: the original opens on SplashWindow (its XAML resource is in the image) and then shows the shell.
            // The splash is created first so the very first frame the user sees is the brand, not an empty desktop.
            var splash = new Cybersole.Ui.Views.Auth.SplashWindow(
                Cybersole.Ui.Views.Settings.SettingsShell.DisplayVersion, Services.Config.Settings.Language);
            splash.Show();

            var window = new MainWindow(Model);
            window.Opened += (_, _) => splash.Close();
            desktop.MainWindow = window;

            // R215: `--browser [url]` opens the in-app browser window. It has no session until the task engine binds
            // one, and the window says exactly that instead of pretending to be a painted viewport.
            if (WantsBrowserWindow(Environment.GetCommandLineArgs()))
            {
                var browser = new Cybersole.Ui.Views.Browser.CustomBrowser();
                var url = BrowserUrl(Environment.GetCommandLineArgs());
                if (url is not null) browser.Address = url;
                browser.Show();
            }
            desktop.Exit += (_, _) =>
            {
                try
                {
                    Services.Config.Save();
                    Services.Config.Backup();
                    Services.Dispose();
                }
                catch
                {
                    // exiting — best effort
                }
            };
        }

        base.OnFrameworkInitializationCompleted();
    }

    /// <summary>
    /// True when the command line asks for the in-app browser window (<c>--browser</c>). Split out from the start-up
    /// block so the switch is testable without a desktop.
    /// </summary>
    public static bool WantsBrowserWindow(IReadOnlyList<string> args)
    {
        for (var i = 0; i < args.Count; i++)
            if (string.Equals(args[i], "--browser", StringComparison.OrdinalIgnoreCase))
                return true;

        return false;
    }

    /// <summary>The URL after <c>--browser</c>, or null. A bare switch opens the window on a blank address.</summary>
    public static string? BrowserUrl(IReadOnlyList<string> args)
    {
        for (var i = 0; i < args.Count - 1; i++)
        {
            if (!string.Equals(args[i], "--browser", StringComparison.OrdinalIgnoreCase)) continue;
            var next = args[i + 1];
            return next.StartsWith("--", StringComparison.Ordinal) ? null : next;
        }

        return null;
    }
}

internal static class Program
{
    [STAThread]
    public static void Main(string[] args)
        => BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
}
