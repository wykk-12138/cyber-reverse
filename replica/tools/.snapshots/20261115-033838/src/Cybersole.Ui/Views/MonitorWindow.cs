using Avalonia;
using Cybersole.Core.Models;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Http;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Live request monitor (Cybersole.Ui.Views.Monitor.MonitorWindow):
/// every request/connection event streamed from <see cref="HttpAnalytics"/>.
/// </summary>
public sealed class MonitorWindow : Window
{
    private readonly AppServices _services;
    private readonly ListBox _stream = new() { Background = Brushes.Transparent };
    private readonly TextBlock _summary = new() { Opacity = 0.8 };
    private readonly TextBox _filter = new() { Watermark = "filter by host / tag", Width = 260 };
    private int _total;
    private int _failed;

    // R499: bound names for no-arg actions (each already existed as a method).
    /// <summary>Bound as <c>Exit</c>; behaviour unchanged (was a method).</summary>
    public ICommand Exit { get; }

    /// <summary>Bound as <c>Minimise</c>; behaviour unchanged (was a method).</summary>
    public ICommand Minimise { get; }

    /// <summary>Bound as <c>ShowMonitor</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowMonitor { get; }

    /// <summary>Bound as <c>ShowSmartActions</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowSmartActions { get; }

    /// <summary>Bound as <c>ShowUtilities</c>; behaviour unchanged (was a method).</summary>
    public ICommand ShowUtilities { get; }

    public MonitorWindow(AppServices services)
    {
        Exit = new RelayCommand(ExitCore);
        Minimise = new RelayCommand(MinimiseCore);
        ShowMonitor = new RelayCommand(ShowMonitorCore);
        ShowSmartActions = new RelayCommand(ShowSmartActionsCore);
        ShowUtilities = new RelayCommand(ShowUtilitiesCore);

        _services = services;
        Title = "Monitor";
        // R217: measured on the running 5.18.32 build — the hidden Monitor window is 1536x814, same as Solver
        // and Login. The replica had 980x620, which no evidence ever supported.
        Width = 1536;
        Height = 814;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        var clear = new Button { Content = "Clear" };
        clear.Click += (_, _) => { _stream.Items.Clear(); _total = 0; _failed = 0; UpdateSummary(); };

        var bar = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            Children = { _filter, clear, _summary },
        };

        // Both handlers arrive on the thread that finished the request — a pool thread. The
        // ListBox and the summary TextBlock belong to the UI thread, so every write is marshalled.
        // Round 121: without this, the throw escaped into the caller and a licence check reported
        // "Call from invalid thread" instead of its real result.
        _services.Analytics.RequestRecorded += (_, e) =>
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                if (!Matches(e)) return;
                _stream.Items.Insert(0,
                    $"{e.At:HH:mm:ss.fff} {e.Method,-4} {e.Status,3} {e.ElapsedMs,5}ms {e.Bytes,7}B {e.Protocol,-8} {e.Tag ?? "-",-16} {e.Url}");
                _total++;
                if (e.Status >= 400) _failed++;
                UpdateSummary();
            });

        _services.Analytics.ConnectionRecorded += (_, e) =>
            Avalonia.Threading.Dispatcher.UIThread.Post(() =>
            {
                if (e.State == "failed") _failed++;
                UpdateSummary();
            });

        var root = new DockPanel { LastChildFill = true, Margin = new Thickness(10) };
        DockPanel.SetDock(bar, Dock.Top);
        root.Children.Add(bar);
        root.Children.Add(_stream);

        // R234: the original binds ShowMonitor / ShowSmartActions / ShowUtilities on this window, which is only possible
        // if the window holds all three panes. The replica had the request stream alone.
        _tabs = new TabControl
        {
            Items =
            {
                new TabItem { Header = "Monitor", Content = root },
                new TabItem { Header = "Smart Actions", Content = new SmartActions.SmartActionsView(_services) },
                new TabItem { Header = "Utilities", Content = new Utilities.UtilitiesView(_services) },
            },
        };

        Content = _tabs;
        UpdateSummary();
    }

    // ------------------------------------------------ bound commands (R234)

    private readonly TabControl? _tabs;

    /// <summary>Shows the request stream (bound as <c>ShowMonitor</c>).</summary>
    private void ShowMonitorCore() => Select(0);

    /// <summary>Shows the smart-actions pane (bound as <c>ShowSmartActions</c>).</summary>
    private void ShowSmartActionsCore() => Select(1);

    /// <summary>Shows the utilities pane (bound as <c>ShowUtilities</c>).</summary>
    private void ShowUtilitiesCore() => Select(2);

    /// <summary>
    /// Puts the cursor in the filter box and selects what is there, so typing replaces the old filter
    /// (bound as <c>OpenFilter</c> on the original's MonitorView).
    /// </summary>
    public void OpenFilter()
    {
        _filter.Focus();
        _filter.SelectAll();
    }

    /// <summary>Minimises the window (bound as <c>Minimise</c>).</summary>
    private void MinimiseCore() => WindowState = WindowState.Minimized;

    /// <summary>Closes the window (bound as <c>Exit</c>).</summary>
    private void ExitCore() => Close();

    /// <summary>Which pane is showing; 0 Monitor, 1 Smart Actions, 2 Utilities.</summary>
    public int Pane => _tabs?.SelectedIndex ?? 0;

    private void Select(int index)
    {
        if (_tabs is null) return;
        _tabs.SelectedIndex = index;
    }

    private bool Matches(HttpRequestEvent e)
    {
        var f = _filter.Text;
        if (string.IsNullOrWhiteSpace(f)) return true;
        return e.Url.Contains(f, StringComparison.OrdinalIgnoreCase) ||
               (e.Tag?.Contains(f, StringComparison.OrdinalIgnoreCase) ?? false);
    }

    private void UpdateSummary() => _summary.Text = $"requests={_total}  failures={_failed}";
}
