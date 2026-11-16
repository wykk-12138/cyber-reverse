using System.Collections.Concurrent;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;

namespace Cybersole.Services;

/// <summary>Runtime state of one executing task.</summary>
public sealed class TaskRuntime
{
    public required BotTask Task { get; init; }
    public TaskState State { get; set; } = TaskState.Idle;
    /// <summary>
    /// Monitor polls that came back out of stock.
    ///
    /// Not "checkout attempts" despite the name: the in-stock branch raises state and hands off
    /// to checkout without touching this, and the checkout path either returns (success) or backs
    /// off on <c>retryDelay</c>. Only the idle poll loop increments it.
    ///
    /// Round 103 added an assertion that this advances after a real checkout and it did not —
    /// that was the test guessing the wrong semantic, not the engine missing a count. Renaming a
    /// field that never leaves memory would buy nothing; the summary plus the integration test
    /// now state what it actually means.
    /// </summary>
    public int Attempts { get; set; }
    public int Checkouts { get; set; }
    public string? LastError { get; set; }
    public DateTime? StartedAt { get; set; }
    public DateTime? LastPollAt { get; set; }
    public CancellationTokenSource? Cts { get; set; }
}

/// <summary>
/// The task engine (Cybersole.Services.TaskEngine): one worker per task,
/// monitor loop with delay/backoff, checkout hand-off, concurrency limiting.
/// </summary>
public sealed class TaskEngine
{
    private readonly NetClient _http;
    private readonly EventBus _bus;
    private readonly StoreRegistry _stores;
    private readonly GlobalSettings _settings;
    private readonly ConfigurationStore _config;
    private readonly Captcha.CaptchaSolverService _captcha;
    private readonly ClockService _clock;

    private readonly ConcurrentDictionary<string, TaskRuntime> _runtime = new();

    /// <summary>profile id → successful checkouts (drives profile.oneCheckout + group.profileLimit).</summary>
    private readonly ConcurrentDictionary<string, int> _profileUsage = new();

    /// <summary>Caps how many tasks may actively monitor/checkout at once (settings.concurrency).</summary>
    private readonly ConcurrencyGate _slots;

    public TaskEngine(NetClient http, EventBus bus, StoreRegistry stores, GlobalSettings settings,
        ConfigurationStore config, Captcha.CaptchaSolverService captcha, ClockService clock)
    {
        _http = http;
        _bus = bus;
        _stores = stores;
        _settings = settings;
        _config = config;
        _captcha = captcha;
        _clock = clock;
        _slots = new ConcurrencyGate(settings.MonitorConcurrency.Maximum <= 0 ? 3 : settings.MonitorConcurrency.Maximum);
    }

    public IReadOnlyCollection<TaskRuntime> Runtime => _runtime.Values.ToArray();
    public event EventHandler<TaskRuntime>? StateChanged;
    public event EventHandler<CheckoutEvent>? CheckoutCompleted;

    /// <summary>Raised when a checkout parks on a 3-D Secure challenge (store, profile name).</summary>
    public event EventHandler<(string Store, string Profile)>? ThreeDSRequired;

    public TaskRuntime Ensure(BotTask task)
        => _runtime.GetOrAdd(task.Id, _ => new TaskRuntime { Task = task });

    public void Start(BotTask task)
    {
        var rt = Ensure(task);
        if (rt.State is TaskState.Monitoring or TaskState.Waiting or TaskState.CheckingOut) return;

        rt.Cts = new CancellationTokenSource();
        rt.StartedAt = DateTime.UtcNow;
        rt.State = TaskState.Starting;
        Raise(rt);
        _bus.Info("Task", $"start {task.Name} ({task.Store})");

        _ = RunAsync(rt, rt.Cts.Token);
    }

    public void StartAll(IEnumerable<BotTask> tasks)
    {
        foreach (var t in tasks) Start(t);
    }

    public void Stop(BotTask task)
    {
        if (!_runtime.TryGetValue(task.Id, out var rt)) return;
        rt.Cts?.Cancel();
        rt.State = TaskState.Stopped;
        Raise(rt);
        _bus.Info("Task", $"stop {task.Name}");
    }

    public void StopAll() => StopAll(_runtime.Keys);

    public void StopAll(IEnumerable<string> ids)
    {
        foreach (var id in ids.ToList())
            if (_runtime.TryGetValue(id, out var rt)) Stop(rt.Task);
    }

    private async Task RunAsync(TaskRuntime rt, CancellationToken ct)
    {
        using var lease = await _slots.EnterAsync(ct).ConfigureAwait(false);
        await RunCoreAsync(rt, ct).ConfigureAwait(false);
    }

    private async Task RunCoreAsync(TaskRuntime rt, CancellationToken ct)
    {
        var task = rt.Task;
        var module = _stores.Resolve(task.Store)
                     ?? _stores.Modules.FirstOrDefault();

        if (module is null)
        {
            rt.State = TaskState.Failed;
            rt.LastError = $"no store module for '{task.Store}'";
            Raise(rt);
            return;
        }

        if (!MonitorFilterPolicy.IsEnabled(_settings.MonitorFilters, module.Id))
        {
            rt.State = TaskState.Stopped;
            rt.LastError = $"monitoring for '{module.Id}' is disabled in Settings → Monitor filters";
            _bus.Warn("Task", $"{task.Name}: {rt.LastError}");
            Raise(rt);
            return;
        }

        // scheduled start (task.StartTime): wait until the release moment before monitoring
        if (task.StartTime is { } scheduled)
        {
            var wait = scheduled - DateTime.UtcNow;
            if (wait > TimeSpan.FromHours(12)) wait = TimeSpan.FromHours(12); // guard against absurd values
            if (wait > TimeSpan.Zero)
            {
                rt.State = TaskState.Waiting;
                Raise(rt);
                _bus.Info("Task", $"{task.Name}: waiting {wait.TotalSeconds:0}s for scheduled start");
                await Task.Delay(wait, ct).ConfigureAwait(false);
            }
        }

        var proxyGroup = _config.ProxyGroups.FirstOrDefault(g => g.Id == task.ProxyGroupId);
        var rotator = proxyGroup is null ? null : new ProxyRotator(proxyGroup);
        var monitorDelay = task.MonitorDelay ?? _settings.MonitorDelay;
        var retryDelay = task.RetryDelay ?? _settings.RetryDelay;
        var timeout = task.Timeout ?? _settings.Timeout;

        rt.State = TaskState.Monitoring;
        Raise(rt);

        // A task may carry several products (the original's Cart tab has an "Add Input" row).
        // Poll them round-robin rather than in parallel: the whole point of a task is that it
        // holds one slot, and firing N requests per interval would quietly multiply the load.
        var products = task.AllProducts;
        var productIndex = 0;

        while (!ct.IsCancellationRequested)
        {
            var current = products[productIndex % products.Count];
            productIndex++;

            try
            {
                var proxy = rotator?.Next();
                MonitorResult monitor;
                try
                {
                    monitor = await module.MonitorAsync(new MonitorContext
                {
                    Http = _http,
                    Url = current.Url ?? string.Empty,
                    Product = current,
                    Proxy = proxy,
                    TimeoutSeconds = timeout,
                    }, ct).ConfigureAwait(false);
                }
                catch (Exception ex)
                {
                    // a module throwing must not kill the worker
                    monitor = MonitorResult.Fail(ex.Message);
                }

                rt.LastPollAt = DateTime.UtcNow;
                _bus.Log(LogLevel.Debug, "Monitor",
                    $"{task.Name}: {monitor.Status} {(monitor.Price is null ? "" : monitor.Price)}");

                if (monitor.Status == MonitorStatus.Captcha)
                {
                    rt.State = TaskState.Waiting;
                    Raise(rt);
                }
                else if (monitor.InStock)
                {
                    rt.State = TaskState.CheckingOut;
                    Raise(rt);

                    var allProfiles = _config.BillingGroups.SelectMany(g => g.Profiles).ToList();
                    var group = task.GroupId is null
                        ? null
                        : _config.TaskGroups.FirstOrDefault(g => g.Id == task.GroupId);

                    var profile = (task.ProfileId is null
                            ? null
                            : allProfiles.FirstOrDefault(p => p.Id == task.ProfileId))
                        ?? Cybersole.Core.Store.ProfileAllocation.Select(
                            allProfiles, _profileUsage, group?.ProfileLimit ?? 0);

                    if (profile is null)
                    {
                        rt.LastError = "no billing profile configured";
                        rt.State = TaskState.Failed;
                        Raise(rt);
                        return;
                    }

                    // the task's bound account supplies credentials/email; modules use it when present
                    var account = task.AccountId is null
                        ? null
                        : _config.Accounts.AccountGroups.SelectMany(g => g.Accounts)
                            .FirstOrDefault(a => a.Id == task.AccountId);

                    // botTask.monitorMode: report availability but never spend money
                    if (!Cybersole.Core.Store.TaskPolicy.ShouldCheckout(task))
                    {
                        _bus.Info("Task",
                            $"{task.Name}: {monitor.ProductName ?? current.Name} in stock — " +
                            Cybersole.Core.Store.TaskPolicy.SkipReason(task));
                        rt.State = TaskState.Monitoring;
                        await Task.Delay(monitorDelay, ct).ConfigureAwait(false);
                        continue;
                    }

                    // botTask.checkoutDelay: a deliberate pause between "in stock" and the checkout POST
                    if (task.CheckoutDelay is { } checkoutDelayMs && checkoutDelayMs > 0)
                        await Task.Delay(TimeSpan.FromMilliseconds(Math.Min(checkoutDelayMs, 60_000)), ct)
                            .ConfigureAwait(false);

                    var size = current.Sizes.FirstOrDefault() ?? string.Empty;

                    // one form for every module: identity + billing, handed over via Extra
                    var form = Cybersole.Http.Stores.CheckoutFormBuilder.Build(profile, account, size);

                    // TaskGroup.ShippingRate ("Preferred shipping method/price for this group")
                    // had no reader anywhere: the field was declared, ShippingRatesCreatorView
                    // wrote it, and no code ever consumed it — the same shape as the
                    // raised-but-unsubscribed events found in round 180, one layer down.
                    //
                    // It travels to the flow through Extra, the channel the checkout form already
                    // uses, so this needs no change to CheckoutContext.
                    if (!string.IsNullOrWhiteSpace(group?.ShippingRate))
                        form["shippingRate"] = group!.ShippingRate!;

                    var outcome = await module.CheckoutAsync(new CheckoutContext
                    {
                        Http = _http,
                        Url = current.Url ?? string.Empty,
                        VariantId = monitor.VariantId ?? string.Empty,
                        Size = size,
                        ProfileData = profile,
                        Account = account,
                        Proxy = proxy,
                        TimeoutSeconds = timeout,
                        Extra = form,
                    }, ct).ConfigureAwait(false);

                    rt.Checkouts++;

                    // R52: the original keeps per-group running totals (get_TotalCheckouts /
                    // get_TotalDeclines on TaskGroup). CheckoutStats is global and keyed by store,
                    // so it cannot answer "how many has this group landed". The group object is
                    // shared by every task in it, so plain ++ would lose increments under
                    // concurrency; a lock per checkout is negligible against a checkout.
                    if (group is not null)
                    {
                        lock (group)
                        {
                            if (outcome.Success) group.TotalCheckouts++;
                            else group.TotalDeclines++;
                        }
                    }

                    if (outcome.Success)
                        _profileUsage.AddOrUpdate(profile.Id, 1, (_, n) => n + 1);

                    if (outcome.Result == CheckoutResult.ThreeDSRequired)
                        ThreeDSRequired?.Invoke(this, (task.Store, profile.Name));

                    CheckoutCompleted?.Invoke(this, new CheckoutEvent(
                        task.Store, monitor.ProductName ?? current.Name,
                        current.Sizes.FirstOrDefault() ?? string.Empty,
                        outcome.Price ?? monitor.Price ?? string.Empty,
                        outcome.Success, outcome.OrderNumber, profile.Name)
        {
            TrackingUrl = outcome.TrackingUrl,
        });

                    rt.State = outcome.Success ? TaskState.Success : TaskState.Failed;
                    rt.LastError = outcome.Error;
                    Raise(rt);

                    if (outcome.Success)
                    {
                        _bus.Info("Checkout", $"SUCCESS {task.Name} order={outcome.OrderNumber}");
                        return;
                    }

                    rt.State = TaskState.Monitoring;
                    Raise(rt);
                    await Task.Delay(retryDelay, ct).ConfigureAwait(false);
                }
                else
                {
                    rt.Attempts++;
                    await Task.Delay(monitorDelay, ct).ConfigureAwait(false);
                }
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                rt.LastError = ex.Message;
                _bus.Warn("Task", $"{task.Name}: {ex.Message}");
                await Task.Delay(retryDelay, ct).ConfigureAwait(false);
            }
        }

        rt.State = TaskState.Stopped;
        Raise(rt);
    }

    private void Raise(TaskRuntime rt) => StateChanged?.Invoke(this, rt);
}
