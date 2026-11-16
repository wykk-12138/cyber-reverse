using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Payments;

/// <summary>Outcome of a gateway authorisation attempt.</summary>
public sealed class PaymentResult
{
    public bool Ok { get; init; }
    public bool RequiresAction { get; init; }
    public string? Error { get; init; }
    public string? GatewayReference { get; init; }
    public string? OrderId { get; init; }
    public string? ThreeDsUrl { get; init; }
    public string? ThreeDsPayload { get; init; }
    public Dictionary<string, string> Fields { get; } = new(StringComparer.OrdinalIgnoreCase);

    public static PaymentResult Success(string? reference = null) =>
        new() { Ok = true, GatewayReference = reference };

    public static PaymentResult Action(string url, string payload) =>
        new() { RequiresAction = true, ThreeDsUrl = url, ThreeDsPayload = payload };

    public static PaymentResult Fail(string error) => new() { Ok = false, Error = error };
}

/// <summary>Card authorisation surface shared by every gateway integration.</summary>
public interface IPaymentGateway
{
    string Id { get; }
    string Name { get; }

    /// <summary>Create a token / nonce for the card without charging it.</summary>
    Task<PaymentResult> TokenizeAsync(FlowContext c, CancellationToken ct);

    /// <summary>Authorise using either a token or the raw card.</summary>
    Task<PaymentResult> AuthorizeAsync(FlowContext c, CancellationToken ct);

    /// <summary>Finish a payment that came back requiring an extra action (3-D Secure).</summary>
    Task<PaymentResult> CompleteActionAsync(FlowContext c, string payload, CancellationToken ct);
}

/// <summary>Gateway lookup by id, mirroring the per-store gateway assignment in settings.</summary>
public sealed class PaymentGatewayRegistry
{
    private readonly Dictionary<string, IPaymentGateway> _gateways =
        new(StringComparer.OrdinalIgnoreCase);

    public IReadOnlyCollection<IPaymentGateway> All => _gateways.Values;

    public void Register(IPaymentGateway gateway) => _gateways[gateway.Id] = gateway;

    public IPaymentGateway? Resolve(string? id) =>
        id is not null && _gateways.TryGetValue(id, out var g) ? g : null;

    /// <summary>Every gateway the shipped binary references, wired up and ready.</summary>
    public static PaymentGatewayRegistry CreateDefault()
    {
        var r = new PaymentGatewayRegistry();
        r.Register(new AdyenGateway());
        r.Register(new SquareGateway());
        r.Register(new StripeGateway());
        r.Register(new UnzerGateway());
        r.Register(new CommerceHubGateway());
        r.Register(new OmiseGateway());
        r.Register(new PaynamicsGateway());
        r.Register(new SibsGateway());
        r.Register(new PayPalGateway());
        return r;
    }
}
