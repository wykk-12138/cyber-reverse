using System.Collections.ObjectModel;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Services;

namespace Cybersole.Ui.ViewModels;

/// <summary>
/// Main window view model: exposes the live collections and the commands that
/// the original UI surfaces (start/stop, create, import, test, save).
/// </summary>
public sealed class MainViewModel : ObservableObject
{
    private readonly AppServices _services;
    private string _status = "Ready";
    private string _monitorDelayText = "2500";
    private string _retryDelayText = "2500";
    private string _timeoutText = "10";
    private string _proxyImportText = string.Empty;

    public MainViewModel(AppServices services)
    {
        _services = services;

        TaskLines = new ObservableCollection<string>();
        CheckoutLines = new ObservableCollection<string>();
        LogLines = new ObservableCollection<string>();

        // Every one of these can be raised from a pool thread: the HTTP layer logs, the engine
        // raises checkout events, modules warn. Touching an ObservableCollection off the UI thread
        // throws "Call from invalid thread", and because the throw happens inside the event
        // invoker it propagates back into whoever made the request — round 121 saw a licence check
        // fail with that message instead of its real error.
        _services.Bus.Logged += (_, e) =>
            Avalonia.Threading.Dispatcher.UIThread.Post(() => AppendLog(e.ToString()));

        _services.Bus.Checkout += (_, e) =>
            Avalonia.Threading.Dispatcher.UIThread.Post(() => CheckoutLines.Insert(0,
                $"{e.Store,-10} {e.Product,-32} {e.Size,-4} {e.Price,-10} " +
                (e.Success ? "OK " + e.OrderNumber : "FAIL")));

        // notifications raised through the bus (Smart Actions, module warnings) belong in the log
        _services.Bus.Notification += (_, message) =>
            Avalonia.Threading.Dispatcher.UIThread.Post(() => AppendLog($"[notify] {message}"));

        // task runtime changes must reach the grid, otherwise the tasks page shows stale states
        _services.Tasks.StateChanged += (_, rt) => Avalonia.Threading.Dispatcher.UIThread.Post(() =>
        {
            Status = $"{rt.Task.Name}: {rt.State}" + (rt.LastError is null ? string.Empty : $" — {rt.LastError}");
            RefreshTasks();
        });

        // desktop/centre notifications surface in the status bar too
        _services.Notify.Shown += (_, n) => Avalonia.Threading.Dispatcher.UIThread.Post(
            () => Status = $"[{n.Kind}] {n.Title}");

        foreach (var line in _services.Bus.History) AppendLog(line.ToString());
        RefreshTasks();
        RefreshAccounts();
        RefreshProxies();

        MonitorDelayText = _services.Config.Settings.MonitorDelay.ToString();
        RetryDelayText = _services.Config.Settings.RetryDelay.ToString();
        TimeoutText = _services.Config.Settings.Timeout.ToString();
    }

    public ObservableCollection<string> TaskLines { get; }
    /// <summary>R54: the proxies page can now create and edit groups, so it needs the real list.</summary>
    public System.Collections.Generic.List<Cybersole.Core.Models.ProxyGroup> ProxyGroups => _services.Config.ProxyGroups;

    public ObservableCollection<string> CheckoutLines { get; }
    public ObservableCollection<string> LogLines { get; }

    public string Status { get => _status; private set => SetProperty(ref _status, value); }
    public string MonitorDelayText { get => _monitorDelayText; set => SetProperty(ref _monitorDelayText, value); }
    public string RetryDelayText { get => _retryDelayText; set => SetProperty(ref _retryDelayText, value); }
    public string TimeoutText { get => _timeoutText; set => SetProperty(ref _timeoutText, value); }
    public string ProxyImportText { get => _proxyImportText; set => SetProperty(ref _proxyImportText, value); }

    public string SessionText =>
        _services.Auth.IsSignedIn
            ? $"Signed in: {_services.Auth.Email}  •  license {_services.Config.Settings.License?[..Math.Min(8, _services.Config.Settings.License?.Length ?? 0)]}…"
            : "Not signed in";

    public AppServices Services => _services;

    public CheckoutStats Stats => _services.Stats;

    // ---------------- tasks ----------------

    public void StartAll()
    {
        var tasks = _services.Config.TaskGroups.SelectMany(g => g.Tasks).ToList();
        if (tasks.Count == 0)
        {
            Status = "No tasks — create one first";
            return;
        }

        _services.Tasks.StartAll(tasks);
        Status = $"Started {tasks.Count} task(s)";
        RefreshTasks();
    }

    public void StopAll()
    {
        _services.Tasks.StopAll();
        Status = "Stopped all tasks";
        RefreshTasks();
    }

    public void AddDemoTask()
    {
        var group = _services.Config.TaskGroups[0];
        var task = new BotTask
        {
            Name = $"Task {group.Tasks.Count + 1}",
            Store = "shopify",
            Product = new Product
            {
                Name = "Demo Product",
                Url = "https://example.myshopify.com/products/demo",
                Sizes = new List<string> { "9", "10" },
            },
            MonitorDelay = _services.Config.Settings.MonitorDelay,
            RetryDelay = _services.Config.Settings.RetryDelay,
            Timeout = _services.Config.Settings.Timeout,
        };
        group.Tasks.Add(task);
        _services.Config.Save();
        RefreshTasks();
        Status = $"Task '{task.Name}' created";
    }

    public void RefreshTasks()
    {
        TaskLines.Clear();

        // settings.pinGroups: pinned groups are shown first
        foreach (var group in Cybersole.Core.Store.TaskGroupOrdering.Sort(_services.Config.TaskGroups))
        {
            var pin = group.Pinned ? "📌 " : string.Empty;
            TaskLines.Add($"{pin}[{group.Name}] ({group.Tasks.Count} task(s)) captcha={group.CaptchaSource}");
            foreach (var task in group.Tasks)
            {
                var rt = _services.Tasks.Runtime.FirstOrDefault(r => r.Task.Id == task.Id);
                var state = rt?.State.ToString() ?? task.State.ToString();
                TaskLines.Add($"   {task.Name,-16} store={task.Store,-10} state={state,-12} price={task.Product.Price ?? "-"}");
            }
        }
    }

    // ---------------- accounts ----------------

    public void AddDemoAccount()
    {
        _services.Config.Accounts.AccountGroups.Add(new AccountGroup
        {
            Name = $"Group {_services.Config.Accounts.AccountGroups.Count + 1}",
            Accounts = { new Account { Email = $"user{_services.Config.Accounts.AccountGroups.Count + 1}@example.com", Password = "pa55word" } },
        });
        _services.Config.Save();
        RefreshAccounts();
        Status = "Account group added";
    }

    public void RefreshAccounts()
    {
        // R55: this used to rebuild AccountLines, a string list the accounts page rendered. That
        // page is now AccountView (a real table over the model), so the string list had no reader
        // left — this method would have kept building it for nobody.
        //
        // What remains is the part that was always real work: making sure a config that has no
        // groups at all gets one, so the table has somewhere to put an import.
        if (_services.Config.Accounts.AccountGroups.Count == 0)
        {
            _services.Config.Accounts.AccountGroups.Add(new AccountGroup { Name = "Group 1" });
            _services.Config.Save();
        }
    }

    // ---------------- proxies ----------------

    public void ImportProxies()
    {
        var parsed = Cybersole.Services.ImportParser.ParseProxies(ProxyImportText);
        if (parsed.Count == 0)
        {
            Status = "Nothing to import";
            return;
        }

        var group = _services.Config.ProxyGroups[0];
        foreach (var proxy in parsed)
            group.Proxies.Add(proxy);

        ProxyImportText = string.Empty;
        _services.Config.Save();
        RefreshProxies();
        Status = $"Imported {parsed.Count} proxy line(s)";
    }

    /// <summary>
    /// Tests every proxy, optionally against a particular store instead of the neutral echo.
    /// </summary>
    /// <param name="targetUrl">
    /// R58: <c>Proxies.More.TestAllOn</c> ("Test All On:") + <c>Select Site</c>. Null means the
    /// echo service — "does this proxy work at all". A store origin asks the different question a
    /// drop actually cares about: can this proxy reach <em>that</em> store, or is it blocked there
    /// while still reaching ipify.
    /// </param>
    public async Task TestProxiesAsync(string? targetUrl = null)
    {
        var proxies = _services.Config.ProxyGroups.SelectMany(g => g.Proxies).ToList();
        if (proxies.Count == 0)
        {
            Status = "No proxies to test";
            return;
        }

        var where = string.IsNullOrWhiteSpace(targetUrl) ? "ip echo" : targetUrl!;
        Status = $"Testing {proxies.Count} proxies against {where}…";
        var results = await _services.ProxyTester
            .TestAllAsync(proxies, 25, targetUrl: targetUrl).ConfigureAwait(true);
        Status = $"Tested against {where}: {results.Count(r => r.Ok)}/{results.Count} ok";
        RefreshProxies();
    }

    /// <summary>
    /// Tests a single proxy. <c>Proxies.More.TestOn</c> ("Test On:") — the per-row counterpart of
    /// "Test All On".
    /// </summary>
    /// <remarks>
    /// R58 gave the tester a target; R59 gives the row a way to use it. The single-proxy path does
    /// not go through <c>TestAllAsync</c>: that one fans out over a list and reports a total, and a
    /// total of one is a worse answer than the row's own result.
    /// </remarks>
    public async Task<ProxyTestResult> TestProxyAsync(Proxy proxy, string? targetUrl = null)
    {
        var where = string.IsNullOrWhiteSpace(targetUrl) ? "ip echo" : targetUrl!;
        Status = $"Testing {proxy.Address} against {where}…";

        var result = await _services.ProxyTester
            .TestAsync(proxy, targetUrl: targetUrl).ConfigureAwait(true);

        Status = result.Ok
            ? $"{proxy.Address} ok in {result.LatencyMs}ms{(result.ExitIp is null ? "" : " via " + result.ExitIp)}"
            : $"{proxy.Address} failed: {result.Error}";

        RefreshProxies();
        return result;
    }

    /// <summary>
    /// Raised when the proxy collection changed and the table should be rebuilt.
    /// </summary>
    /// <remarks>
    /// R56: this used to be <c>RefreshProxies()</c> rebuilding a <c>ProxyLines</c> string list.
    /// Once the page became <c>ProxyView</c> that list had no reader — the same orphan R55 caught
    /// on the accounts page, repeated one round later on the proxies page.
    ///
    /// The signal survives as an event because three call sites need to tell the view something
    /// happened, and the view owns the controls. R180's lesson is that an event declared, raised
    /// and never subscribed is worse than a direct call — so <c>MainWindow.BuildProxies</c>
    /// subscribes before it can be raised, and <c>TheProxyTableRebuildsOnChange</c> fails if that
    /// subscription is ever removed.
    /// </remarks>
    public event EventHandler? ProxiesChanged;

    public void RefreshProxies() => ProxiesChanged?.Invoke(this, EventArgs.Empty);

    // ---------------- settings ----------------

    public void SaveSettings()
    {
        var settings = _services.Config.Settings;
        settings.MonitorDelay = int.TryParse(MonitorDelayText, out var md) ? md : settings.MonitorDelay;
        settings.RetryDelay = int.TryParse(RetryDelayText, out var rd) ? rd : settings.RetryDelay;
        settings.Timeout = int.TryParse(TimeoutText, out var to) ? to : settings.Timeout;
        _services.Config.Save();
        Status = "Settings saved";
    }

    // ---------------- auth ----------------

    public async Task SignOutAsync()
    {
        _services.Auth.SignOut();
        _services.Config.Save();
        Status = "Signed out";
        OnPropertyChanged(nameof(SessionText));
        await Task.CompletedTask;
    }

    public void RefreshSession()
    {
        OnPropertyChanged(nameof(SessionText));
    }

    private void AppendLog(string line)
    {
        LogLines.Add(line);
        while (LogLines.Count > 500) LogLines.RemoveAt(0);
    }
}
