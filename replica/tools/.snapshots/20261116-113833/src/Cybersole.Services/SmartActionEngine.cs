using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services;

/// <summary>
/// Smart Actions engine: matches checkout/task events against the rule list and
/// executes the configured action (webhook / notification / stop). Mirrors the
/// original's "Smart Actions" feature driven by smartActions.json.
/// </summary>
public sealed class SmartActionEngine : IDisposable
{
    private readonly ConfigurationStore _config;
    private readonly EventBus _bus;
    private readonly NotificationService _notify;
    private readonly NetClient _http;
    private readonly List<SmartActionExecution> _history = new();

    public SmartActionEngine(ConfigurationStore config, EventBus bus, NotificationService notify, NetClient http)
    {
        _config = config;
        _bus = bus;
        _notify = notify;
        _http = http;

        _bus.Checkout += OnCheckout;
    }

    public IReadOnlyList<SmartActionExecution> History => _history;

    public sealed record SmartActionExecution(
        DateTime At, string RuleName, SmartTrigger Trigger, bool Executed, string? Error);

    private void OnCheckout(object? sender, CheckoutEvent evt)
    {
        var trigger = evt.Success ? SmartTrigger.CheckoutSuccess : SmartTrigger.Decline;
        foreach (var rule in _config.SmartActions.Actions.Where(a => a.Enabled && a.Trigger == trigger))
        {
            if (!Matches(rule, evt)) continue;
            if (!ShouldRun(rule)) continue;
            _ = ExecuteAsync(rule, evt);
        }
    }

    /// <summary>
    /// RunOnce / RunInterval gate (SmartActionSettings.RunOnce / RunInterval).
    /// Returns false when the rule already fired once (RunOnce) or when it fired more
    /// recently than its interval allows.
    /// </summary>
    public bool ShouldRun(SmartAction rule, DateTime? now = null)
    {
        var at = now ?? DateTime.UtcNow;

        if (rule.RunOnce && rule.LastRun is not null) return false;

        if (rule.LastRun is { } last && rule.RunInterval is { } gap && at - last < gap)
            return false;

        return true;
    }

    /// <summary>
    /// Rule filtering: legacy StoreFilter / MinPrice plus the full <see cref="SmartActionFilter"/>
    /// chain (all filters must pass; an empty chain passes).
    /// </summary>
    public bool Matches(SmartAction rule, CheckoutEvent evt)
    {
        if (!string.IsNullOrWhiteSpace(rule.StoreFilter) &&
            !string.Equals(rule.StoreFilter, evt.Store, StringComparison.OrdinalIgnoreCase))
            return false;

        if (rule.MinPrice is { } min &&
            decimal.TryParse(evt.Price, System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var price) &&
            price < min)
            return false;

        return rule.Passes(evt);
    }

    public async Task ExecuteAsync(SmartAction rule, CheckoutEvent evt)
    {
        try
        {
            switch (rule.Kind)
            {
                case SmartActionKind.Webhook:
                    if (string.IsNullOrWhiteSpace(rule.Target))
                        throw new InvalidOperationException("webhook target is empty");
                    await _http.PostJsonAsync(rule.Target,
                        Newtonsoft.Json.JsonConvert.SerializeObject(new
                        {
                            content = $"[{rule.Name}] {evt.Store} {evt.Product} {evt.Size} {evt.Price} " +
                                      (evt.Success ? $"order={evt.OrderNumber}" : "declined"),
                            username = "Cybersole",
                            variables = rule.Variables,
                        }),
                        new RequestOptions { Tag = "smart-action", Timeout = TimeSpan.FromSeconds(10) })
                        .ConfigureAwait(false);
                    break;

                case SmartActionKind.Notification:
                    await _notify.PublishAsync(NotificationKind.Other, $"Smart action: {rule.Name}",
                        $"{evt.Store} · {evt.Product} · {(evt.Success ? "success" : "declined")}")
                        .ConfigureAwait(false);
                    break;

                case SmartActionKind.StopTask:
                    _bus.Info("SmartAction", $"{rule.Name}: stop requested for {evt.Store}");
                    break;
            }

            Record(rule, true, null);
        }
        catch (Exception ex)
        {
            Record(rule, false, ex.Message);
            _bus.Warn("SmartAction", $"{rule.Name} failed: {ex.Message}");
        }
    }

    private void Record(SmartAction rule, bool executed, string? error)
    {
        var at = DateTime.UtcNow;
        _history.Insert(0, new SmartActionExecution(at, rule.Name, rule.Trigger, executed, error));
        while (_history.Count > 200) _history.RemoveAt(_history.Count - 1);

        // Persist the run stamp so RunOnce / RunInterval actually gate the next event.
        rule.LastRun = at;
        rule.LastResult = executed ? "ok" : error ?? "failed";

        if (executed && rule.RunOnce)
        {
            rule.Enabled = false;
            _bus.Info("SmartAction", $"{rule.Name}: run-once rule disabled after firing");
        }
    }

    public void Dispose() => _bus.Checkout -= OnCheckout;
}
