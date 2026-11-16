using System.Globalization;
using Avalonia;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Services;
using Cybersole.Ui.ViewModels;

using Cybersole.Core.Models;
using Cybersole.Ui.Views.Accounts;
using Cybersole.Ui.Views.Modals;
using Cybersole.Ui.Views.Common;
using Cybersole.Ui.Views.Proxies;

namespace Cybersole.Ui.Views;

/// <summary>
/// Main window — rebuilt from the original's view model surface
/// (Tasks / Accounts / Proxies / Analytics / Settings + log console).
/// </summary>
public sealed class MainWindow : Window
{
    private readonly MainViewModel _vm;
    private readonly TextBlock _session = new() { VerticalAlignment = VerticalAlignment.Center, Opacity = 0.75 };
    private readonly TextBlock _status = new() { Text = "Ready", Margin = new Thickness(8, 4) };
    private readonly TabControl _tabs = new();

    /// <summary>0=Home 1=Tasks 2=Proxies 3=Billing 4=Accounts 5=Settings</summary>
    private int TabIndex => Math.Max(0, _tabs.SelectedIndex);

    // ------------------------------------------------ bound commands (R232)
    //
    // The original binds these on MainWindow (analysis/xaml_bindings.json):
    //   Clock, Exit, Minimise, Navigate, OpenMonitor, OpenNotifications, OpenProfile
    // plus one property per view. Several were reachable only as inline toolbar lambdas; the rest were missing.

    /// <summary>The settings page the Settings tab hosts (bound as <c>SettingsView</c>).</summary>
    public Control? SettingsView =>
        _tabs.ItemCount > 5 && _tabs.Items[5] is TabItem tab ? tab.Content as Control : null;

    /// <summary>Opens the monitor window (bound as <c>OpenMonitor</c>).</summary>
    private void OpenMonitorCore() => new MonitorWindow(_vm.Services).Show(this);

    /// <summary>Opens the notification centre (bound as <c>OpenNotifications</c>).</summary>
    private void OpenNotificationsCore() => new NotificationView(_vm.Services).Show(this);

    /// <summary>Opens the account/profile window (bound as <c>OpenProfile</c>).</summary>
    private void OpenProfileCore() => new UserView(_vm.Services).Show(this);

    /// <summary>
    /// Switches to a tab by name — the same six names the tabs carry (bound as <c>Navigate</c>). Returns false for a
    /// name it does not know, so a caller can tell "switched" from "no such tab".
    /// </summary>
    public bool Navigate(string? tab)
    {
        if (string.IsNullOrWhiteSpace(tab)) return false;

        for (var i = 0; i < _tabs.ItemCount; i++)
        {
            if (_tabs.Items[i] is not TabItem item) continue;
            if (!string.Equals(item.Header as string, tab, StringComparison.OrdinalIgnoreCase)) continue;

            _tabs.SelectedIndex = i;
            return true;
        }

        return false;
    }

    /// <summary>Minimises the shell (bound as <c>Minimise</c>).</summary>
    private void MinimiseCore() => WindowState = WindowState.Minimized;

    /// <summary>Closes the shell (bound as <c>Exit</c>).</summary>
    private void ExitCore() => Close();

    /// <summary>The local time as the title bar shows it (bound as <c>Clock</c>).</summary>
    public string Clock => DateTime.Now.ToString("HH:mm:ss", CultureInfo.InvariantCulture);

    // R498: bound names for no-arg window actions (each already existed as a method).
    /// <summary>Bound as <c>Exit</c>; behaviour unchanged (was a method).</summary>
    public ICommand Exit { get; }

    /// <summary>Bound as <c>Minimise</c>; behaviour unchanged (was a method).</summary>
    public ICommand Minimise { get; }

    /// <summary>Bound as <c>OpenMonitor</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenMonitor { get; }

    /// <summary>Bound as <c>OpenNotifications</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenNotifications { get; }

    /// <summary>Bound as <c>OpenProfile</c>; behaviour unchanged (was a method).</summary>
    public ICommand OpenProfile { get; }

    public MainWindow(MainViewModel vm)
    {
        Exit = new RelayCommand(ExitCore);
        Minimise = new RelayCommand(MinimiseCore);
        OpenMonitor = new RelayCommand(OpenMonitorCore);
        OpenNotifications = new RelayCommand(OpenNotificationsCore);
        OpenProfile = new RelayCommand(OpenProfileCore);

        _vm = vm;
        Title = "Cybersole 5.18.32 — functional replica";
        Width = 1280;
        Height = 800;
        MinWidth = 960;
        MinHeight = 600;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;

        var header = new Border
        {
            Background = new SolidColorBrush(Color.Parse("#15161C")),
            Padding = new Thickness(12, 8),
            Child = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                Spacing = 16,
                Children =
                {
                    new TextBlock
                    {
                        Text = "CYBERSOLE",
                        FontWeight = FontWeight.Bold,
                        FontSize = 16,
                        Foreground = new SolidColorBrush(Color.Parse("#E6E6F0")),
                        VerticalAlignment = VerticalAlignment.Center,
                    },
                    _session,
                    Btn("Sign in", async () =>
                    {
                        var dialog = new SignInWindow(_vm.Services);
                        var ok = await dialog.ShowDialog<bool>(this);
                        if (ok) _vm.RefreshSession();
                    }),
                    Btn("Sign out", async () =>
                    {
                        await _vm.SignOutAsync();
                        _vm.RefreshSession();
                    }),
                    Btn("License", () => new LicenseWindow(_vm.Services).ShowDialog(this)),
                    Btn("Solver", () => new SolverWindow(_vm.Services).Show(this)),
                    Btn("Browser", () => new CustomBrowserWindow(_vm.Services).Show(this)),
                    Btn("Monitor", () => OpenMonitor.Execute(null)),
                    Btn("3DS", async () =>
                    {
                        var win = new ThreeDSWindow("demo", "Profile 1");
                        var code = await win.ShowDialog<string?>(this);
                        if (!string.IsNullOrEmpty(code))
                            _status.Text = $"3DS code captured ({code.Length} digits)";
                    }),
                },
            },
        };

        _tabs = new TabControl
        {
            Margin = new Thickness(8),
            Items =
            {
                // Order and membership read off the running 5.18.32 window (docs/GUI_BASELINE.md):
                // Home / Tasks / Proxies / Billing / Accounts / Settings — six tabs.
                // Home is the analytics dashboard; the replica used to carry it as its own tab
                // and also carried a Logs tab the real build does not have.
                new TabItem { Header = "Home", Content = new Analytics.AnalyticsView(_vm.Services) },
                new TabItem { Header = "Tasks", Content = new Tasks.TaskView(_vm.Services) },
                new TabItem { Header = "Proxies", Content = BuildProxies() },
                new TabItem { Header = "Billing", Content = new BillingView(_vm.Services) },
                new TabItem { Header = "Accounts", Content = BuildAccounts() },
                new TabItem { Header = "Settings", Content = new Settings.SettingsShell(_vm.Services) },
            },
        };

        var statusBar = new Border
        {
            Background = new SolidColorBrush(Color.Parse("#15161C")),
            Child = _status,
        };

        var root = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(header, Dock.Top);
        DockPanel.SetDock(statusBar, Dock.Bottom);
        root.Children.Add(header);
        root.Children.Add(statusBar);
        root.Children.Add(_tabs);
        Content = root;

        foreach (var problem in Cybersole.Stores.Modules.CatalogValidator
                     .Validate(_vm.Services.Stores.Modules))
            _vm.Services.Bus.Warn("Stores", problem);

        // settings.autoOpen3DS / autoOpen3DSLimit → pop the 3DS window automatically
        var opened3DS = 0;
        _vm.Services.Tasks.ThreeDSRequired += (_, e) =>
        {
            var settings = _vm.Services.Config.Settings;
            if (!settings.AutoOpen3DS) return;

            var limit = settings.AutoOpen3DSLimit <= 0 ? 0 : settings.AutoOpen3DSLimit;
            if (limit > 0 && opened3DS >= limit) return;

            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                if (limit > 0 && opened3DS >= limit) return;
                opened3DS++;
                new ThreeDSWindow(e.Store, e.Profile).Show(this);
                _vm.Services.Bus.Info("3DS",
                    $"auto-opened for {e.Store}/{e.Profile} ({opened3DS}/{limit})");
            });
        };

        // settings.keyBinds → live shortcuts (StartAll / StopAll / New / Delete)
        KeyDown += (_, e) =>
        {
            var binds = _vm.Services.Config.Settings.KeyBinds.Tasks;
            var vk = Cybersole.Core.Input.KeyBindMatcher.VirtualKey(e.Key.ToString());
            if (vk == 0) return;

            var mods = Cybersole.Core.Input.KeyBindMatcher.Modifiers(
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Alt),
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Control),
                e.KeyModifiers.HasFlag(Avalonia.Input.KeyModifiers.Shift));

            if (Cybersole.Core.Input.KeyBindMatcher.Matches(binds.StartAll, vk, mods))
            {
                _vm.StartAll();
                _vm.Services.Bus.Info("KeyBind", $"start all ({Cybersole.Core.Input.KeyBindMatcher.Describe(binds.StartAll)})");
                e.Handled = true;
            }
            else if (Cybersole.Core.Input.KeyBindMatcher.Matches(binds.StopAll, vk, mods))
            {
                _vm.StopAll();
                _vm.Services.Bus.Info("KeyBind", $"stop all ({Cybersole.Core.Input.KeyBindMatcher.Describe(binds.StopAll)})");
                e.Handled = true;
            }
            else if (Cybersole.Core.Input.KeyBindMatcher.Matches(binds.New, vk, mods)
                     && TabIndex == 1)
            {
                _ = new TaskEditorWindow(_vm.Services).ShowDialog(this);
                e.Handled = true;
            }
            else if (TabIndex == 2)
            {
                var proxyBinds = _vm.Services.Config.Settings.KeyBinds.Proxies;
                if (Cybersole.Core.Input.KeyBindMatcher.Matches(proxyBinds.TestAll, vk, mods))
                {
                    _ = _vm.TestProxiesAsync();
                    e.Handled = true;
                }
                else if (Cybersole.Core.Input.KeyBindMatcher.Matches(proxyBinds.Add, vk, mods))
                {
                    _vm.ImportProxies();
                    e.Handled = true;
                }
            }
            else if (TabIndex == 3)
            {
                var billingBinds = _vm.Services.Config.Settings.KeyBinds.Billing;
                if (Cybersole.Core.Input.KeyBindMatcher.Matches(billingBinds.New, vk, mods))
                {
                    _ = new ProfileEditorWindow(_vm.Services).ShowDialog(this);
                    e.Handled = true;
                }
            }
        };

        RefreshSession();
        vm.PropertyChanged += (_, e) =>
        {
            if (e.PropertyName == nameof(MainViewModel.Status)) _status.Text = vm.Status;
            if (e.PropertyName == nameof(MainViewModel.SessionText)) RefreshSession();
        };
    }

    private void RefreshSession() => _session.Text = _vm.SessionText;

    private static Button Btn(string text, Action onClick)
    {
        var b = new Button { Content = text, Padding = new Thickness(10, 4) };
        b.Click += (_, _) => onClick();
        return b;
    }

    private Control BuildTasks()
    {
        var list = new ListBox
        {
            ItemsSource = _vm.TaskLines,
            Margin = new Thickness(0, 8, 0, 0),
            Background = Brushes.Transparent,
        };

        var bar = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children =
            {
                Btn("Start All", () => { _vm.StartAll(); _vm.RefreshTasks(); }),
                Btn("Stop All", () => { _vm.StopAll(); _vm.RefreshTasks(); }),
                Btn("New Task", () =>
                {
                    var editor = new TaskEditorWindow(_vm.Services);
                    editor.Closed += (_, _) => _vm.RefreshTasks();
                    _ = editor.ShowDialog(this);
                }),
                Btn("Refresh", _vm.RefreshTasks),
            },
        };

        var root = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(bar, Dock.Top);
        root.Children.Add(bar);
        root.Children.Add(list);
        return root;
    }

    private Control BuildAccounts()
    {
        // R55: this was an ObservableCollection<string> — one interpolated line per account.
        // R70: it became a real table with a selection model.
        //
        // R71: the page is now what the original is — a two-pane Accounts page (ACCOUNT GROUPS on
        // the left, one group at a time on the right) whose toolbar belongs to the group, not to
        // the page. The old flat table over every group's accounts could not answer "which group
        // am I looking at", which is why its toolbar had to say "Refresh".
        _accountsHost = new AccountView(_vm.Services.Config.Accounts, () =>
        {
            _vm.Services.Config.Save();
            _vm.RefreshAccounts();
        });
        return _accountsHost;
    }

    private Control? _accountsHost;

    /// <summary>
    /// Rebuilds the Accounts page in place. The page owns its own panes now, so a refresh is a
    /// fresh <see cref="AccountView"/> rather than a body swap inside a fixed host.
    /// </summary>
    private void RebuildAccountsPage()
    {
        _vm.RefreshAccounts();
        if (_accountsHost is not ContentControl host) return;
        host.Content = new AccountView(_vm.Services.Config.Accounts, () =>
        {
            _vm.Services.Config.Save();
            _vm.RefreshAccounts();
        });
    }

    private Control BuildProxies()
    {
        // R56: this was a ListBox over ProxyLines — "[Group 1] (12) behaviour=RoundRobin" plus one
        // indented line per proxy.
        //
        // R72: the page is what the original is — PROXY GROUPS on the left with a count badge per
        // group, one group at a time on the right. That is also what makes "Clear Over" honest: a
        // flat list cannot say which group's MaxUsage governs a row, and R56 had to guess.
        var sites = _vm.Services.Stores.Modules.Select(m => m.Name).Distinct().OrderBy(n => n).ToList();

        var page = new ProxyView(_vm.ProxyGroups, () =>
        {
            _vm.Services.Config.Save();
            _vm.RefreshProxies();
        })
            .WithTester(proxy => _vm.TestProxyAsync(proxy))
            .WithTestAll(async () => await _vm.TestProxiesAsync())
            .WithSites(sites, SiteUrl, url => _vm.TestProxiesAsync(url))
            .WithMover((proxy, from) =>
            {
                ProxyMoveView.Show(this, proxy, _vm.ProxyGroups, from, () =>
                {
                    _vm.Services.Config.Save();
                    _vm.RefreshProxies();
                });
                return Task.CompletedTask;
            })
            .WithImporter(group => ImportProxiesInto(group));

        _proxyPage = page;
        // R72: keep the round-180 subscriber. The page owns its panes now, so a change rebuilds the
        // page in place instead of swapping a table inside a fixed host.
        _vm.ProxiesChanged += (_, _) => _proxyPage?.Reload();
        return page;
    }

    private ProxyView? _proxyPage;

    /// <summary>
    /// "Add Proxies" — <c>ProxyCreator.Title</c> / <c>.Label</c> / <c>.Placeholder</c> /
    /// <c>.DragDrop</c> / <c>.ImportFormat</c>, the same dialog shape as Add Accounts.
    /// </summary>
    private bool ImportProxiesInto(ProxyGroup group)
    {
        var box = new TextBox
        {
            AcceptsReturn = true,
            Height = 220,
            Watermark = "Enter proxies as ip:port:username:password",
            FontFamily = new FontFamily("Consolas,monospace"),
        };
        var status = new TextBlock { Opacity = 0.8 };

        var body = new StackPanel
        {
            Spacing = 8,
            Children =
            {
                new TextBlock { Text = group.Name, FontWeight = FontWeight.SemiBold },
                new TextBlock { Text = "Proxies" },
                box,
                new TextBlock { Text = "Or drag and drop a .txt file here", Opacity = 0.7 },
                status,
            },
        };

        var import = new Button { Padding = new Thickness(16, 5) };
        import.Content = "Import (0) New Proxies";
        box.TextChanged += (_, _) =>
            import.Content = $"Import ({ImportParser.ParseProxies(box.Text).Count}) New Proxies";

        import.Click += (_, _) =>
        {
            var parsed = ImportParser.ParseProxies(box.Text);
            var added = 0;
            foreach (var proxy in parsed)
            {
                proxy.GroupId = group.Id;
                group.Proxies.Add(proxy);
                added++;
            }

            status.Text = $"Imported {added}.";
            if (added > 0 && TopLevel.GetTopLevel(this) is Window window) window.Close();
        };

        var opened = ViewHostModal.Show(this, "Add Proxies", UiKit.Scroll(body), 560, 460, import);
        if (opened)
        {
            _vm.Services.Config.Save();
            _vm.RefreshProxies();
        }
        return opened;
    }

    /// <summary>
    /// The origin of the site picked in "Test All On", or null for the neutral echo.
    /// </summary>
    /// <remarks>
    /// Taken from the module's first claimed domain rather than its display name: the name is a
    /// label ("Nike US") and the domain is what a request can actually be sent to.
    /// </remarks>
    private string? SiteUrl(string name)
    {
        var module = _vm.Services.Stores.Modules.FirstOrDefault(m => m.Name == name);
        var domain = module?.Domains.FirstOrDefault();
        return string.IsNullOrWhiteSpace(domain) ? null : $"https://{domain}/";
    }

    private Control BuildCheckouts()
    {
        var stats = _vm.Stats;
        var summary = new TextBlock { Opacity = 0.85, Margin = new Thickness(0, 0, 0, 4) };
        var chart = new StoreBarChart { Height = 180 };

        void Refresh()
        {
            summary.Text =
                $"total {stats.Total}   success {stats.Success}   failed {stats.Failed}   " +
                $"rate {stats.SuccessRate:P0}   spent {stats.Spent:0.00}";
            chart.Update(stats.ByStore);
        }

        stats.Changed += (_, _) => Avalonia.Threading.Dispatcher.UIThread.Post(Refresh);
        Refresh();

        var export = new Button { Content = "Export CSV", HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left };
        export.Click += (_, _) =>
        {
            try
            {
                var dir = Path.Combine(Cybersole.Core.Store.AppPaths.DataRoot, "exports");
                var path = ExportService.ExportToFile(stats.Events, dir);
                summary.Text = $"exported {stats.Events.Count} rows → {path}";
                _vm.Services.Bus.Info("Analytics", $"checkout CSV exported: {path}");
            }
            catch (Exception ex)
            {
                summary.Text = $"export failed: {ex.Message}";
            }
        };

        var top = new StackPanel { Spacing = 6, Children = { summary, chart, export } };

        var list = new ListBox
        {
            ItemsSource = _vm.CheckoutLines,
            Margin = new Thickness(0, 8, 0, 0),
            Background = Brushes.Transparent,
        };

        var root = new DockPanel { LastChildFill = true };
        DockPanel.SetDock(top, Dock.Top);
        root.Children.Add(top);
        root.Children.Add(list);
        return root;
    }

    private Control BuildSettings()
    {
        var monitor = new TextBox { Text = _vm.MonitorDelayText, Width = 120 };
        var retry = new TextBox { Text = _vm.RetryDelayText, Width = 120 };
        var timeout = new TextBox { Text = _vm.TimeoutText, Width = 120 };
        monitor.TextChanged += (_, _) => _vm.MonitorDelayText = monitor.Text ?? string.Empty;
        retry.TextChanged += (_, _) => _vm.RetryDelayText = retry.Text ?? string.Empty;
        timeout.TextChanged += (_, _) => _vm.TimeoutText = timeout.Text ?? string.Empty;

        var grid = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("160,140"),
            RowDefinitions = new RowDefinitions("Auto,Auto,Auto,Auto"),
        };

        void Row(int i, string label, Control input)
        {
            var l = new TextBlock { Text = label, VerticalAlignment = VerticalAlignment.Center };
            Grid.SetRow(l, i);
            Grid.SetColumn(l, 0);
            Grid.SetRow(input, i);
            Grid.SetColumn(input, 1);
            grid.Children.Add(l);
            grid.Children.Add(input);
        }

        Row(0, "Monitor delay (ms)", monitor);
        Row(1, "Retry delay (ms)", retry);
        Row(2, "Timeout (s)", timeout);

        var profiles = Btn("Billing profiles", () =>
        {
            var editor = new ProfileEditorWindow(_vm.Services);
            _ = editor.ShowDialog(this);
        });
        Grid.SetRow(profiles, 4);
        Grid.SetColumn(profiles, 1);
        grid.Children.Add(profiles);

        var smartActions = Btn("Smart actions", () =>
        {
            var editor = new SmartActionEditorWindow(_vm.Services);
            _ = editor.ShowDialog(this);
        });
        Grid.SetRow(smartActions, 5);
        Grid.SetColumn(smartActions, 1);
        grid.Children.Add(smartActions);

        var save = Btn("Save", _vm.SaveSettings);
        Grid.SetRow(save, 3);
        Grid.SetColumn(save, 1);
        grid.Children.Add(save);

        return new ScrollViewer { Content = grid, Margin = new Thickness(0, 12, 0, 0) };
    }

    private Control BuildLogs()
    {
        var list = new ListBox
        {
            ItemsSource = _vm.LogLines,
            Margin = new Thickness(0, 8, 0, 0),
            Background = Brushes.Transparent,
        };
        return list;
    }
}
