using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Services.Captcha;

namespace Cybersole.Ui.Views;

/// <summary>
/// Captcha solver window (Cybersole.Ui.Views.Captcha.SolverWindow).
/// Hosts the challenge queue, the solver toggles and a manual solve form.
/// </summary>
public sealed class SolverWindow : Window
{
    /// <summary>Minimises the solver window (bound as <c>Minimise</c>).</summary>
    private void MinimiseCore() => WindowState = WindowState.Minimized;

    /// <summary>
    /// Closes the window and stops its queue polling (bound as <c>Dispose</c>). Avalonia's <c>Window</c> has no
    /// <c>Dispose</c> of its own — the bound name is the only one — so this is the single release path.
    /// </summary>
    public void Dispose() => Close();

    private readonly AppServices _services;

    // Bound to the object the config actually holds — not a fresh SolverSettings. Round 122: the
    // old field was initialised with `new()`, so a toggle edited this throwaway while
    // Config.Save() wrote the untouched list, and every change vanished on restart. Same shape as
    // the captcha-provider bug in round 113.
    private readonly SolverSettings _settings;
    private readonly ListBox _queue = new() { Background = Brushes.Transparent, Height = 220 };
    private readonly TextBox _siteKey = new() { Watermark = "site key" };
    private readonly TextBox _pageUrl = new() { Watermark = "https://store.example/checkout" };
    private readonly TextBox _proxy = new() { Watermark = "host:port (optional)" };
    private readonly ComboBox _kind = new()
    {
        ItemsSource = new[] { "turnstile", "recaptcha", "hcaptcha", "geetest" },
        SelectedIndex = 0,
    };
    private readonly TextBlock _result = new() { TextWrapping = TextWrapping.Wrap, Opacity = 0.85 };

    /// <summary>
    /// Solver panels (Cybersole.Ui.Views.Captcha.SolverWindow.Panels) — one page per captcha
    /// family, matching the recovered Solver.Settings.* keys.
    /// </summary>
    public IReadOnlyList<string> Panels { get; } = new[]
    {
        "General", "ReCaptcha", "HCaptcha", "Turnstile", "Image challenge",
        "Square challenge", "Multi select",
    };

    /// <summary>Configured solvers (SolverWindow.Solvers), backed by solvers.json.</summary>
    public IReadOnlyList<Solver> Solvers => _services.Config.Solvers
        .SelectMany(v => v.Solvers)
        .ToList();

    /// <summary>SolverWindow.Reload — re-read the persisted solver list.</summary>
    public void Reload()
    {
        var count = Solvers.Count;
        _queue.Items.Add($"[{DateTime.Now:HH:mm:ss}] {count} solver(s) loaded");
    }

    /// <summary>SolverWindow.Add — append a solver bound to the current settings.</summary>
    public Solver Add(string? proxy = null, string? filter = null)
    {
        var view = _services.Config.Solvers.FirstOrDefault();
        if (view is null)
        {
            view = new SolverView();
            _services.Config.Solvers.Add(view);
        }

        var solver = new Solver
        {
            Proxy = proxy,
            Filter = filter,
            Settings = new SolverSettings(),
        };
        view.Solvers.Add(solver);
        _services.Config.Save();
        _queue.Items.Add($"[{DateTime.Now:HH:mm:ss}] solver added ({view.Solvers.Count} total)");
        return solver;
    }

    /// <summary>SolverWindow.CloseSolver — drop a solver by index.</summary>
    public bool CloseSolver(int index)
    {
        var view = _services.Config.Solvers.FirstOrDefault();
        if (view is null || index < 0 || index >= view.Solvers.Count) return false;

        view.Solvers.RemoveAt(index);
        _services.Config.Save();
        return true;
    }

    /// <summary>
    /// The settings object the config holds, creating the solver row when the file is empty.
    /// Every toggle writes straight into it, so Config.Save() has something new to write.
    /// </summary>
    public static SolverSettings SettingsOf(AppServices services)
    {
        var view = services.Config.Solvers.FirstOrDefault();
        if (view is null)
        {
            view = new SolverView();
            services.Config.Solvers.Add(view);
        }

        if (view.Solvers.Count == 0)
            view.Solvers.Add(new Solver { Settings = new SolverSettings() });

        return view.Solvers[0].Settings;
    }

    // R499: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Minimise</c>; behaviour unchanged (was a method).</summary>
    public ICommand Minimise { get; }

    public SolverWindow(AppServices services)
    {
        Minimise = new RelayCommand(MinimiseCore);

        _services = services;
        _settings = SettingsOf(services);
        Title = "Solver";
        // R217: measured — Solver is 1536x814, the same frame as Monitor and Login.
        Width = 1536;
        Height = 814;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        var toggles = new WrapPanel { Orientation = Orientation.Horizontal };
        void Toggle(string label, bool initial, Action<bool> setter)
        {
            var cb = new CheckBox { Content = label, IsChecked = initial, Margin = new Thickness(0, 0, 12, 6) };
            cb.IsCheckedChanged += (_, _) =>
            {
                setter(cb.IsChecked ?? false);
                _services.Config.Save();          // solver toggles live in settings.json
            };
            toggles.Children.Add(cb);
        }

        Toggle("Auto bounding box", _settings.AutoBoundingBox, v => _settings.AutoBoundingBox = v);
        Toggle("Auto tick box", _settings.AutoTickBox, v => _settings.AutoTickBox = v);
        Toggle("Auto canvas", _settings.AutoCanvas, v => _settings.AutoCanvas = v);
        Toggle("Question sharing", _settings.QuestionSharing, v => _settings.QuestionSharing = v);
        Toggle("Auto click", _settings.AutoClick, v => _settings.AutoClick = v);
        Toggle("reCAPTCHA segmentation", _settings.ReCaptchaSegmentation, v => _settings.ReCaptchaSegmentation = v);
        Toggle("reCAPTCHA multi-classification", _settings.ReCaptchaMultiClassification, v => _settings.ReCaptchaMultiClassification = v);

        var solve = new Button { Content = "Solve", Padding = new Thickness(14, 5) };
        solve.Click += async (_, _) => await SolveAsync();

        var form = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                new TextBlock { Text = "Challenge queue", FontWeight = FontWeight.Bold },
                _queue,
                new TextBlock { Text = "Manual solve", FontWeight = FontWeight.Bold, Margin = new Thickness(0, 8, 0, 0) },
                _kind,
                _siteKey,
                _pageUrl,
                _proxy,
                solve,
                _result,
                new TextBlock { Text = "Solver toggles", FontWeight = FontWeight.Bold, Margin = new Thickness(0, 12, 0, 0) },
                toggles,
            },
        };

        Content = new ScrollViewer { Content = form, Padding = new Thickness(14) };

        // Bus.Logged is raised from whichever thread produced the log line — the solver runs its
        // requests on pool threads, so this write needs marshalling. Round 122: same class of bug
        // as MonitorWindow in round 121.
        _services.Bus.Logged += (_, e) =>
        {
            if (e.Source is not ("Captcha" or "Solver")) return;
            Avalonia.Threading.Dispatcher.UIThread.Post(() => _queue.Items.Add(e.Message));
        };
    }

    private async Task SolveAsync()
    {
        if (string.IsNullOrWhiteSpace(_siteKey.Text) || string.IsNullOrWhiteSpace(_pageUrl.Text))
        {
            _result.Text = "site key and page url are required";
            return;
        }

        var kind = (_kind.SelectedItem as string) switch
        {
            "recaptcha" => CaptchaKind.ReCaptcha,
            "hcaptcha" => CaptchaKind.HCaptcha,
            "geetest" => CaptchaKind.Geetest,
            _ => CaptchaKind.Turnstile,
        };

        _result.Text = "solving…";
        try
        {
            var res = await _services.Captcha.SolveAsync(new SolveRequest
            {
                Kind = kind,
                SiteKey = _siteKey.Text!,
                PageUrl = _pageUrl.Text!,
                Proxy = string.IsNullOrWhiteSpace(_proxy.Text) ? null : _proxy.Text,
            }).ConfigureAwait(true);

            _result.Text = res.Ok
                ? $"token={res.Token?[..Math.Min(48, res.Token?.Length ?? 0)]}…  {res.ElapsedSeconds:0.0}s  provider={res.Provider}"
                : $"failed: {res.Error}";
        }
        catch (Exception ex)
        {
            // the click handler is async void, so an escape here would tear the app down
            _result.Text = "failed: " + ex.Message;
        }
    }
}
