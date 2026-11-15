using Cybersole.Core.Models;
using Cybersole.Http.Stores;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Drives a <see cref="StoreFlow"/> through the same ordered step sequence the shipped
/// binary uses (<c>&lt;GetHome&gt;d__</c> → <c>&lt;GetCsrf&gt;d__</c> → … → <c>&lt;SubmitOrder&gt;d__</c>).
/// Every step is recorded as a <see cref="TaskStep"/> so a failure names the frame that broke.
/// </summary>
public static class StoreFlowRunner
{
    /// <summary>Runs the monitoring half of a flow and projects it into a MonitorResult.</summary>
    public static async Task<MonitorResult> RunMonitorAsync(StoreFlow flow, FlowContext ctx,
        CancellationToken ct)
    {
        try
        {
            var guard = await GuardAsync(flow, ctx, ct, "Init", flow.InitAsync).ConfigureAwait(false);
            if (!guard.Ok) return MonitorResult.Fail(guard.Error ?? "init failed");

            var anti = await AntiBotAsync(flow, ctx, ct).ConfigureAwait(false);
            if (!anti.Ok) return new MonitorResult { Status = MonitorStatus.Blocked, Error = anti.Error };

            var home = await GuardAsync(flow, ctx, ct, "GetHome", flow.GetHomeAsync).ConfigureAwait(false);
            if (!home.Ok) return ClassifyMonitorFailure(ctx, home.Error);

            var csrf = await GuardAsync(flow, ctx, ct, "GetCsrf", flow.GetCsrfAsync).ConfigureAwait(false);
            if (!csrf.Ok) return ClassifyMonitorFailure(ctx, csrf.Error);

            var find = await GuardAsync(flow, ctx, ct, "FindProduct", flow.FindProductFlowAsync)
                .ConfigureAwait(false);
            if (!find.Ok) return ClassifyMonitorFailure(ctx, find.Error);

            var variant = await GuardAsync(flow, ctx, ct, "FindVariant", flow.FindVariantAsync)
                .ConfigureAwait(false);
            if (!variant.Ok) return MonitorResult.Fail(variant.Error ?? "variant failed");

            var avail = await GuardAsync(flow, ctx, ct, "ScrapeVariantAvailability",
                flow.ScrapeVariantAvailabilityAsync).ConfigureAwait(false);
            if (!avail.Ok) return MonitorResult.Fail(avail.Error ?? "availability failed");

            var price = await GuardAsync(flow, ctx, ct, "CheckPriceLimit", flow.CheckPriceLimitAsync)
                .ConfigureAwait(false);
            if (!price.Ok) return new MonitorResult { Status = MonitorStatus.Unavailable, Error = price.Error };

            return BuildMonitorResult(ctx);
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception ex)
        {
            return MonitorResult.Fail(ex.Message);
        }
    }

    /// <summary>Runs the checkout half of a flow and projects it into a CheckoutOutcome.</summary>
    public static async Task<CheckoutOutcome> RunCheckoutAsync(StoreFlow flow, FlowContext ctx,
        CancellationToken ct)
    {
        try
        {
            var init = await GuardAsync(flow, ctx, ct, "Init", flow.InitAsync).ConfigureAwait(false);
            if (!init.Ok) return Error(init.Error);

            var anti = await AntiBotAsync(flow, ctx, ct).ConfigureAwait(false);
            if (!anti.Ok) return Blocked(anti.Error);

            foreach (var (name, step) in new (string, Func<FlowContext, CancellationToken, Task<StepOutcome>>)[]
                     {
                         ("GetHome", flow.GetHomeAsync),
                         ("GetCsrf", flow.GetCsrfAsync),
                         ("GetSession", flow.GetSessionAsync),
                     })
            {
                var r = await GuardAsync(flow, ctx, ct, name, step).ConfigureAwait(false);
                if (!r.Ok) return Error($"{name}: {r.Error}");
            }

            if (flow.RequiresAccount)
            {
                var login = await GuardAsync(flow, ctx, ct, "AccountLogin", flow.AccountLoginAsync)
                    .ConfigureAwait(false);
                if (!login.Ok) return Error("AccountLogin: " + login.Error);
            }

            foreach (var (name, step) in new (string, Func<FlowContext, CancellationToken, Task<StepOutcome>>)[]
                     {
                         ("FindProduct", flow.FindProductFlowAsync),
                         ("FindVariant", flow.FindVariantAsync),
                         ("CreateCart", flow.CreateCartAsync),
                         ("AddToCart", flow.AddToCartAsync),
                         ("GetCart", flow.GetCartAsync),
                         ("EditLine", flow.EditLineAsync),
                         ("InitiateCheckout", flow.InitiateCheckoutAsync),
                         ("GetCheckout", flow.GetCheckoutAsync),
                         ("SubmitEmail", flow.SubmitEmailAsync),
                         ("SubmitShipping", flow.SubmitShippingAsync),
                         ("GetShippingRates", flow.GetShippingRatesAsync),
                         ("SubmitShippingMethod", flow.SubmitShippingMethodAsync),
                         ("SubmitBilling", flow.SubmitBillingAsync),
                         ("SubmitDiscount", flow.SubmitDiscountAsync),
                         ("SubmitPayment", flow.SubmitPaymentAsync),
                         ("GetPaymentToken", flow.GetPaymentTokenAsync),
                         ("SubmitOrder", flow.SubmitOrderAsync),
                         ("ProcessOrder", flow.ProcessOrderAsync),
                     })
            {
                var r = await GuardAsync(flow, ctx, ct, name, step).ConfigureAwait(false);
                if (!r.Ok)
                {
                    if (r.Abort) return Error($"{name}: {r.Error}");
                    return Error(DescribeCheckoutFailure(ctx, StageOf(name), r.Error),
                        checkoutResult: ClassifyCheckoutFailure(ctx));
                }
            }

            var success = !string.IsNullOrEmpty(ctx.Session.OrderNumber) ||
                          !string.IsNullOrEmpty(ctx.Session.OrderId);

            return new CheckoutOutcome
            {
                Success = success,
                OrderNumber = ctx.Session.OrderNumber ?? ctx.Session.OrderId,
                TrackingUrl = ctx.Session.TrackingUrl,
                Price = ctx.Product?.Price,
                Result = success ? CheckoutResult.Success : CheckoutResult.Unknown,
                Details = ctx.Session.Vars.ToDictionary(kv => kv.Key, kv => kv.Value),
            };
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception ex)
        {
            return Error(ex.Message);
        }
    }

    /// <summary>Kasada / captcha gate that runs before any store request is issued.</summary>
    private static async Task<StepOutcome> AntiBotAsync(StoreFlow flow, FlowContext ctx,
        CancellationToken ct)
    {
        if (!flow.UsesKasada) return StepOutcome.Success();

        var script = await GuardAsync(flow, ctx, ct, "GetScript", flow.GetScriptAsync)
            .ConfigureAwait(false);
        if (!script.Ok) return script;

        var gen = await GuardAsync(flow, ctx, ct, "GenerateSensor", flow.GenerateSensorAsync)
            .ConfigureAwait(false);
        if (!gen.Ok) return gen;

        return await GuardAsync(flow, ctx, ct, "SubmitSensor", flow.SubmitSensorAsync)
            .ConfigureAwait(false);
    }

    private static async Task<StepOutcome> GuardAsync(StoreFlow flow, FlowContext ctx,
        CancellationToken ct, string name,
        Func<FlowContext, CancellationToken, Task<StepOutcome>> step)
    {
        ct.ThrowIfCancellationRequested();
        var s = ctx.Step(name);
        try
        {
            var outcome = await step(ctx, ct).ConfigureAwait(false);
            ctx.Finish(s, outcome.Ok, outcome.Error);
            return outcome;
        }
        catch (OperationCanceledException)
        {
            ctx.Finish(s, false, "cancelled");
            throw;
        }
        catch (Exception ex)
        {
            ctx.Finish(s, false, ex.Message);
            return StepOutcome.Fail(ex.Message, retryable: true);
        }
    }

    private static MonitorResult BuildMonitorResult(FlowContext ctx)
    {
        var v = ctx.Session.Vars;
        var available = v.TryGetValue("available", out var a) &&
                        string.Equals(a, "true", StringComparison.OrdinalIgnoreCase);

        return new MonitorResult
        {
            Status = available ? MonitorStatus.Available : MonitorStatus.SoldOut,
            ProductName = v.TryGetValue("product", out var p) ? p : ctx.Product?.Name,
            Price = v.TryGetValue("price", out var pr) ? pr : ctx.Product?.Price,
            Image = v.TryGetValue("image", out var img) ? img : ctx.Product?.Image,
            VariantId = ctx.Session.VariantId,
            VariantTitle = ctx.Session.VariantTitle,
            Sizes = v.TryGetValue("sizes", out var sz)
                ? sz.Split('|', StringSplitOptions.RemoveEmptyEntries).ToList()
                : new List<string>(),
            Raw = v.TryGetValue("raw", out var raw) ? raw : null,
        };
    }

    /// <summary>
    /// Turn the last HTTP status into a monitor verdict. A 403 from an anti-bot is a captcha
    /// wall, a 429 is a rate limit, and both are very different from "the host is down".
    /// </summary>
    private static MonitorResult ClassifyMonitorFailure(FlowContext ctx, string? error)
    {
        var status = LastStatus(ctx);

        // The reason text comes from the same catalogue the original shows under Get Help,
        // so a 403 reads "[General] Forbidden" rather than a bare code.
        var entry = ErrorCatalog.Classify(status ?? 0, StepStage.Monitor);
        var message = Describe(entry, error);

        return status switch
        {
            403 => new MonitorResult { Status = MonitorStatus.Captcha, Error = message },
            429 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
            401 => new MonitorResult { Status = MonitorStatus.Blocked, Error = message },
            503 or 502 or 504 => new MonitorResult
            {
                Status = MonitorStatus.Error,
                Error = message,
            },
            _ => MonitorResult.Fail(message),
        };
    }

    /// <summary>Catalogue wording, plus the flow's own detail when it has one.</summary>
    private static string Describe(ErrorCatalog.Entry entry, string? detail) =>
        string.IsNullOrWhiteSpace(detail)
            ? entry.Title + ": " + entry.Detail
            : entry.Title + " - " + detail;

    /// <summary>
    /// A 422 means the store understood the request and rejected it — retrying costs time and
    /// can burn the account. A 409 (sold out during checkout) is the same story.
    /// </summary>
    private static CheckoutResult ClassifyCheckoutFailure(FlowContext ctx) => LastStatus(ctx) switch
    {
        422 or 409 => CheckoutResult.Declined,
        402 => CheckoutResult.Declined,
        _ => CheckoutResult.Error,
    };

    /// <summary>
    /// Same classification, but also naming the stage so the surfaced reason can match the
    /// catalogue entry the original would show for that step.
    /// </summary>
    private static string DescribeCheckoutFailure(FlowContext ctx, StepStage stage,
        string? detail) =>
        Describe(ErrorCatalog.Classify(LastStatus(ctx) ?? 0, stage), detail);


    /// <summary>Map a step name onto the catalogue's stage enum.</summary>
    private static StepStage StageOf(string? step) => step switch
    {
        "FindProduct" => StepStage.FindProduct,
        "FindVariant" => StepStage.FindVariant,
        "AddToCart" => StepStage.AddToCart,
        "GetCart" => StepStage.GetCart,
        "GetCheckout" => StepStage.GetCheckout,
        "SubmitShipping" => StepStage.SubmitShipping,
        "SubmitPayment" => StepStage.SubmitPayment,
        "SubmitOrder" => StepStage.SubmitOrder,
        _ => StepStage.Monitor,
    };

    private static int? LastStatus(FlowContext ctx) =>
        ctx.Session.Vars.TryGetValue("lastStatus", out var raw) && int.TryParse(raw, out var code)
            ? code
            : null;

    private static CheckoutOutcome Error(string? error, CheckoutResult checkoutResult = CheckoutResult.Error) =>
        new() { Success = false, Error = error, Result = checkoutResult };

    private static CheckoutOutcome Blocked(string? error) =>
        new() { Success = false, Error = error, Result = CheckoutResult.Error };
}
