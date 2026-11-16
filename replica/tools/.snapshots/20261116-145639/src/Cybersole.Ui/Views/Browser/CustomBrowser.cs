using System;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services.Localization;

namespace Cybersole.Ui.Views.Browser;

/// <summary>What the window is allowed to do to a real session. Supplied by the host, so the view stays testable.</summary>
public sealed record CustomBrowserActions(
    Func<string, Task> Navigate,
    Func<string, Task<string?>>? Autofill = null,
    Func<string, Task<string?>>? Evaluate = null);

/// <summary>
/// The in-app browser window (R215) — the last class on the original's view list this replica had no counterpart for.
///
/// <para>
/// Its copy is the locale's <c>Browser.*</c> set, measured in the image:
/// <c>Browser.Header</c> "Browser", <c>Browser.AddressBar</c> "Search or enter address",
/// <c>Browser.Autofill</c> "Autofill", <c>Browser.NewTab</c> "New Tab".
/// </para>
///
/// <para>
/// The surface itself is not embedded: this replica drives a headless Chromium over CDP, and a CDP session has no
/// viewport to paint. So the window draws the chrome it can draw (address bar, New Tab, Autofill, a status line) and
/// sends every action through <see cref="CustomBrowserActions"/>, which the host binds to
/// <c>ChromiumBridge.NavigateAsync</c> / <c>EvaluateAsync</c>. That is stated in <see cref="SurfaceNote"/> on screen
/// rather than hidden: a window that silently does nothing would be worse than one that says what it is.
/// </para>
/// </summary>
public sealed class CustomBrowser : Window
{
    /// <summary>The window title, from the locale.</summary>
    public const string HeaderKey = "Browser.Header";

    /// <summary>The address bar's watermark, from the locale.</summary>
    public const string AddressKey = "Browser.AddressBar";

    /// <summary>The two buttons, from the locale.</summary>
    public const string AutofillKey = "Browser.Autofill";

    /// <inheritdoc cref="AutofillKey"/>
    public const string NewTabKey = "Browser.NewTab";

    /// <summary>What the window says about its own surface.</summary>
    public const string SurfaceNote = "This window drives the session's headless browser over CDP; there is no painted viewport.";

    private readonly CustomBrowserActions? _actions;
    private readonly TextBox _address;
    private readonly TextBlock _status;

    public CustomBrowser(CustomBrowserActions? actions = null, string? language = null)
    {
        _actions = actions;

        var title = LocalizationService.Translate(language, HeaderKey);
        Title = title;
        Width = 980;
        Height = 640;
        Background = new SolidColorBrush(Color.FromRgb(22, 24, 32));

        var chrome = BuildChrome(
            addressWatermark: LocalizationService.Translate(language, AddressKey),
            newTabLabel: LocalizationService.Translate(language, NewTabKey),
            autofillLabel: LocalizationService.Translate(language, AutofillKey),
            out var address, out var status);

        _address = address;
        _status = status;

        Content = chrome;
    }

    /// <summary>The address bar, so a host can prefill it.</summary>
    public string Address
    {
        get => _address.Text ?? string.Empty;
        set => _address.Text = value;
    }

    /// <summary>The status line the window prints under the chrome.</summary>
    public string StatusText
    {
        get => _status.Text ?? string.Empty;
        set => _status.Text = value;
    }

    /// <summary>
    /// Builds the window's tree without a <see cref="Window"/>, so a headless test can read the labels and click the
    /// buttons. Constructing a window needs a platform; this does not.
    /// </summary>
    public static Control BuildChrome(string addressWatermark, string newTabLabel, string autofillLabel,
        out TextBox address, out TextBlock status)
    {
        address = new TextBox { Watermark = addressWatermark, Width = 640 };
        status = new TextBlock { Text = string.Empty, Opacity = 0.7, FontSize = 12 };

        var newTab = new Button { Content = newTabLabel };
        var autofill = new Button { Content = autofillLabel };

        var bar = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, Margin = new Thickness(10) };
        bar.Children.Add(newTab);
        bar.Children.Add(address);
        bar.Children.Add(autofill);

        var surface = new Border
        {
            Background = new SolidColorBrush(Color.FromRgb(30, 33, 44)),
            Child = new TextBlock
            {
                Text = SurfaceNote,
                Opacity = 0.5,
                FontSize = 12,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                TextWrapping = TextWrapping.Wrap,
                MaxWidth = 520,
            },
        };

        return new DockPanel
        {
            LastChildFill = true,
            Children =
            {
                Docked(bar, Dock.Top),
                Docked(status, Dock.Bottom),
                surface,
            },
        };
    }

    /// <summary>Navigates the bound session; the address bar and New Tab call this.</summary>
    public async Task NavigateAsync(string url)
    {
        Address = url;
        if (_actions is null)
        {
            StatusText = "No session bound.";
            return;
        }

        StatusText = "Navigating " + url + " …";
        try
        {
            await _actions.Navigate(url).ConfigureAwait(true);
            StatusText = url;
        }
        catch (Exception ex)
        {
            StatusText = "Navigation failed: " + ex.GetType().Name;
        }
    }

    /// <summary>Runs the autofill script against the bound session, if there is one.</summary>
    public async Task<string?> AutofillAsync(string script)
    {
        if (_actions?.Autofill is null)
        {
            StatusText = "Autofill needs a session.";
            return null;
        }

        try
        {
            var result = await _actions.Autofill(script).ConfigureAwait(true);
            StatusText = "Autofill ran.";
            return result;
        }
        catch (Exception ex)
        {
            StatusText = "Autofill failed: " + ex.GetType().Name;
            return null;
        }
    }

    /// <summary>
    /// The seven members the original binds on this window besides Navigate/Autofill — its compiled XAML lists
    /// <c>Back, Exit, Forward, Minimise, Refresh, Status, Type</c> (R225, `analysis/xaml_bindings.json`).
    /// </summary>

    /// <summary>Goes back in the bound session's history.</summary>
    public Task Back() => RunScriptAsync("history.back()");

    /// <summary>Goes forward in the bound session's history.</summary>
    public Task Forward() => RunScriptAsync("history.forward()");

    /// <summary>Reloads the bound session's page.</summary>
    public Task Refresh() => RunScriptAsync("location.reload()");

    /// <summary>Minimises the window, as the title bar's own button does.</summary>
    public void Minimise() => WindowState = WindowState.Minimized;

    /// <summary>Closes the window.</summary>
    public void Exit() => Close();

    /// <summary>
    /// Which surface this window shows. The original binds a <c>Type</c> member here; the replica has exactly one kind of
    /// surface, so it defaults to "Task" and is only a label.
    /// </summary>
    public string Type { get; set; } = "Task";

    /// <summary>The status line, which is what the original's <c>Status</c> binding shows.</summary>
    public string Status => StatusText;

    private async Task RunScriptAsync(string script)
    {
        if (_actions?.Evaluate is null)
        {
            StatusText = "No session bound.";
            return;
        }

        try
        {
            await _actions.Evaluate(script).ConfigureAwait(true);
            StatusText = script;
        }
        catch (Exception ex)
        {
            StatusText = "Script failed: " + ex.GetType().Name;
        }
    }

    /// <summary>Opens the window against a live CDP session.</summary>
    public static CustomBrowser FromBridge(Cybersole.Stores.Scripts.ChromiumBridge bridge, string? language = null) =>
        new(new CustomBrowserActions(
            url => bridge.NavigateAsync(url),
            script => bridge.EvaluateAsync(script),
            script => bridge.EvaluateAsync(script)), language);

    private static Control Docked(Control control, Dock dock)
    {
        DockPanel.SetDock(control, dock);
        return control;
    }
}
