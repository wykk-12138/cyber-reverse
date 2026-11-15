using Cybersole.Http.Stores;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Adapter that exposes a step-driven <see cref="StoreFlow"/> through the legacy
/// two-method <see cref="IStoreModule"/> surface, so the task engine and the UI do not
/// care whether a store is implemented as steps or as a single loop.
/// </summary>
public sealed class FlowStoreModule : Abstractions.StoreModuleBase
{
    private readonly StoreFlow _flow;

    public FlowStoreModule(StoreFlow flow) => _flow = flow;

    public StoreFlow Flow => _flow;

    public override string Id => _flow.Id;
    public override string Name => _flow.Name;
    public override IReadOnlyList<string> Domains => _flow.Domains;

    public override bool CanHandle(Uri url) => _flow.CanHandle(url);

    public override Task<MonitorResult> MonitorAsync(MonitorContext context, CancellationToken ct)
    {
        var ctx = new FlowContext
        {
            Http = context.Http,
            Url = context.Url,
            Product = context.Product,
            Proxy = context.Proxy,
            BrowserProfile = context.Profile,
            TimeoutSeconds = context.TimeoutSeconds,
            MonitorOnly = true,
        };
        return StoreFlowRunner.RunMonitorAsync(_flow, ctx, ct);
    }

    public override Task<CheckoutOutcome> CheckoutAsync(CheckoutContext context, CancellationToken ct)
    {
        var ctx = new FlowContext
        {
            Http = context.Http,
            Url = context.Url,
            ProfileData = context.ProfileData,
            Account = context.Account,
            Proxy = context.Proxy,
            BrowserProfile = context.BrowserProfile,
            TimeoutSeconds = context.TimeoutSeconds,
            MonitorOnly = false,
        };

        ctx.Session.VariantId = context.VariantId;
        ctx.Session.VariantTitle = context.Size;
        if (!string.IsNullOrEmpty(context.Size)) ctx.Session.Vars["size"] = context.Size;
        foreach (var kv in context.Extra) ctx.Session.Vars[kv.Key] = kv.Value;

        return StoreFlowRunner.RunCheckoutAsync(_flow, ctx, ct);
    }
}
