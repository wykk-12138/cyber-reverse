using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Actions;

/// <summary>
/// A named, replayable unit of work made of flow steps — the original's per-store action
/// vocabulary. Each id below was recovered verbatim from the binary's string heap:
/// <c>Account-Login</c>, <c>Account-LoginVerify2FA</c>, <c>Account-SubmitRegistration</c>,
/// <c>Account-VerifyTwoFactorEmailCode</c>, <c>Account-CheckLogin</c>,
/// <c>Adyen-Authorize3DS2</c>, <c>Adyen-PaymentFromComponent</c>, <c>Adyen-PaymentsDetails</c>,
/// <c>COShipping-Form</c>, <c>CSRF-Generate</c>, <c>Product-Variant</c>, <c>Sites-asics</c>.
/// </summary>
public sealed class StepAction
{
    public required string Id { get; init; }
    public required string Category { get; init; }
    public required string Name { get; init; }
    public string? Description { get; init; }

    /// <summary>Flow step names, executed in order. Must exist on <see cref="StoreFlow"/>.</summary>
    public required IReadOnlyList<string> Steps { get; init; }

    public override string ToString() => Id;
}

/// <summary>Resolved result of running one action.</summary>
public sealed class StepActionResult
{
    public bool Ok { get; set; } = true;
    public string? Error { get; set; }
    public string? FailedStep { get; set; }
    public List<TaskStepRecord> Records { get; } = new();
}

public readonly struct TaskStepRecord
{
    public string Name { get; init; }
    public bool Ok { get; init; }
    public TimeSpan Elapsed { get; init; }
    public string? Error { get; init; }
}

/// <summary>Registry of every recovered action id plus its step sequence.</summary>
public sealed class StepActionRegistry
{
    private readonly Dictionary<string, StepAction> _actions = new(StringComparer.OrdinalIgnoreCase);

    public IReadOnlyCollection<StepAction> All => _actions.Values;

    public void Register(StepAction action) => _actions[action.Id] = action;

    public StepAction? Resolve(string id) => _actions.TryGetValue(id, out var a) ? a : null;

    public IReadOnlyList<StepAction> ByCategory(string category) =>
        _actions.Values.Where(a => string.Equals(a.Category, category, StringComparison.OrdinalIgnoreCase))
            .OrderBy(a => a.Id, StringComparer.Ordinal)
            .ToList();

    public static StepActionRegistry CreateDefault()
    {
        var r = new StepActionRegistry();

        r.Register(new StepAction
        {
            Id = "Account-Login",
            Category = "Account",
            Name = "Login",
            Description = "Session, CSRF, credential submit, then verify the session stuck.",
            Steps = new[] { "GetHome", "GetCsrf", "AccountLogin", "CheckLogin" },
        });

        r.Register(new StepAction
        {
            Id = "Account-LoginVerify2FA",
            Category = "Account",
            Name = "Login + 2FA",
            Description = "Login then satisfy the second factor before returning.",
            Steps = new[] { "GetHome", "GetCsrf", "AccountLogin", "SendTwoFactor", "CheckLogin" },
        });

        r.Register(new StepAction
        {
            Id = "Account-SubmitRegistration",
            Category = "Account",
            Name = "Register",
            Description = "Create a store account from a profile.",
            Steps = new[] { "GetHome", "GetCsrf", "Register", "CompleteRegistration" },
        });

        r.Register(new StepAction
        {
            Id = "Account-VerifyTwoFactorEmailCode",
            Category = "Account",
            Name = "Verify email code",
            Description = "Submit the mailbox code for an email-based second factor.",
            Steps = new[] { "SetEmail", "SendTwoFactor" },
        });

        r.Register(new StepAction
        {
            Id = "Account-CheckLogin",
            Category = "Account",
            Name = "Check session",
            Description = "Probe whether the current cookies still hold a login.",
            Steps = new[] { "GetSession", "VerifySession", "CheckLogin" },
        });

        r.Register(new StepAction
        {
            Id = "Adyen-Authorize3DS2",
            Category = "Adyen",
            Name = "Authorize 3DS2",
            Description = "Run the 3-D Secure 2 challenge and submit the result.",
            Steps = new[] { "SubmitPayment", "ThreeDS", "Handle3DS", "Process3DS" },
        });

        r.Register(new StepAction
        {
            Id = "Adyen-PaymentFromComponent",
            Category = "Adyen",
            Name = "Payment from component",
            Description = "Post the drop-in component state blob to /payments.",
            Steps = new[] { "SubmitPayment", "GetPaymentToken", "CompletePayment" },
        });

        r.Register(new StepAction
        {
            Id = "Adyen-PaymentsDetails",
            Category = "Adyen",
            Name = "Payments details",
            Description = "Finish the payment on /payments/details after the action returns.",
            Steps = new[] { "GetPaymentDetails", "SubmitPaymentDetails", "CompletePayment" },
        });

        r.Register(new StepAction
        {
            Id = "COShipping-Form",
            Category = "Checkout",
            Name = "Shipping form",
            Description = "Fill and submit the shipping form, then pick a rate.",
            Steps = new[] { "GetCheckout", "SubmitShipping", "GetShippingRates", "SubmitShippingMethod" },
        });

        r.Register(new StepAction
        {
            Id = "CSRF-Generate",
            Category = "Session",
            Name = "Generate CSRF",
            Description = "Mint or scrape the anti-forgery token and attach it to the session.",
            Steps = new[] { "GetHome", "GetCsrf", "SetRequest" },
        });

        r.Register(new StepAction
        {
            Id = "Product-Variant",
            Category = "Product",
            Name = "Resolve variant",
            Description = "Load the product, resolve the requested variant, read availability.",
            Steps = new[] { "FindProduct", "FindVariant", "ScrapeVariantAvailability" },
        });

        r.Register(new StepAction
        {
            Id = "Sites-asics",
            Category = "Sites",
            Name = "Asics",
            Description = "Site-scoped bootstrap for asics.com (product feed + variant).",
            Steps = new[] { "GetHome", "FindProduct", "FindVariant", "ScrapeVariantAvailability",
                            "AddToCart", "GetCart" },
        });

        r.Register(new StepAction
        {
            Id = "Kasada-Sensor",
            Category = "AntiBot",
            Name = "Kasada sensor",
            Description = "Fetch ips.js, generate the client token locally, warm it against the host.",
            Steps = new[] { "GetScript", "GenerateSensor", "SubmitSensor" },
        });

        r.Register(new StepAction
        {
            Id = "Queue-Pass",
            Category = "AntiBot",
            Name = "Queue pass",
            Description = "Wait out a queue gate before the cart is touched.",
            Steps = new[] { "GetHome", "PollQueue", "WaitForRelease" },
        });

        return r;
    }
}

/// <summary>Runs a <see cref="StepAction"/> against a flow by reflecting the step names.</summary>
public static class StepActionRunner
{
    // R869: internal rather than private, so StoreFlow.StepDispatch can expose this table instead of building a
    // second one. Two ways to invoke a step by name is one too many, and this is the older and better one — it uses
    // MethodInfo.Invoke, which is why it never hit the delegate-binding failure R868 ran into.
    internal static readonly Dictionary<string, Func<StoreFlow, FlowContext, CancellationToken, Task<StepOutcome>>>
        Invokers = Build();

    private static Dictionary<string, Func<StoreFlow, FlowContext, CancellationToken, Task<StepOutcome>>> Build()
    {
        var map = new Dictionary<string, Func<StoreFlow, FlowContext, CancellationToken, Task<StepOutcome>>>(
            StringComparer.OrdinalIgnoreCase);

        foreach (var m in typeof(StoreFlow).GetMethods(
                     System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance))
        {
            if (!m.Name.EndsWith("Async")) continue;
            if (m.ReturnType != typeof(Task<StepOutcome>)) continue;
            if (m.GetParameters().Length != 2) continue;

            var name = m.Name[..^5];
            map[name] = (flow, ctx, ct) =>
                (Task<StepOutcome>)m.Invoke(flow, new object[] { ctx, ct })!;
        }

        return map;
    }

    public static bool Knows(string step) => Invokers.ContainsKey(step);

    public static async Task<StepActionResult> RunAsync(StoreFlow flow, FlowContext ctx,
        StepAction action, CancellationToken ct)
    {
        var result = new StepActionResult { Ok = true };

        foreach (var step in action.Steps)
        {
            ct.ThrowIfCancellationRequested();

            if (!Invokers.TryGetValue(step, out var invoke))
            {
                result.Ok = false;
                result.FailedStep = step;
                result.Error = $"unknown step '{step}' in action {action.Id}";
                return result;
            }

            var record = ctx.Step(step);
            var sw = System.Diagnostics.Stopwatch.StartNew();
            try
            {
                var outcome = await invoke(flow, ctx, ct).ConfigureAwait(false);
                sw.Stop();
                ctx.Finish(record, outcome.Ok, outcome.Error);
                result.Records.Add(new TaskStepRecord
                {
                    Name = step,
                    Ok = outcome.Ok,
                    Elapsed = sw.Elapsed,
                    Error = outcome.Error,
                });

                if (!outcome.Ok)
                {
                    result.Ok = false;
                    result.FailedStep = step;
                    result.Error = outcome.Error;
                    return result;
                }
            }
            catch (OperationCanceledException)
            {
                ctx.Finish(record, false, "cancelled");
                throw;
            }
            catch (Exception ex)
            {
                sw.Stop();
                ctx.Finish(record, false, ex.Message);
                result.Records.Add(new TaskStepRecord
                {
                    Name = step,
                    Ok = false,
                    Elapsed = sw.Elapsed,
                    Error = ex.Message,
                });
                result.Ok = false;
                result.FailedStep = step;
                result.Error = ex.Message;
                return result;
            }
        }

        return result;
    }
}
