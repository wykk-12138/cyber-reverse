namespace Cybersole.Stores.Flows;

/// <summary>
/// Nike's <b>persisted GraphQL</b> checkout operations, read out of the 5.18.32 image in R101.
///
/// <para>
/// This is the most useful thing found about Nike since R87. The image carries:
/// </para>
///
/// <code>
/// checkouts/internal/graphql
/// checkouts/internal/graphql/persisted?operationName=CheckoutExtensionSessionToken
/// checkouts/internal/graphql/persisted?operationName=PaypalDetails
/// checkouts/internal/graphql/persisted?operationName=PaypalToken
/// checkouts/internal/graphql/persisted?operationName=PollForReceipt
/// checkouts/internal/graphql/persisted?operationName=Proposal
/// checkouts/internal/graphql/persisted?operationName=SubmitForCompletion
/// </code>
///
/// <para>
/// A persisted query is addressed by <b>name only</b> — the server holds the document. That explains
/// why the fourteen Nike steps never showed up as URL literals in R87/R88: the per-step sub-paths
/// the replica invented (<c>buy/orders/v2/{id}/shipping</c> and friends) do not exist because the
/// steps are not REST sub-resources at all. They are <c>operationName</c>s against
/// <c>buy/checkouts/v3/{id}</c>'s GraphQL twin.
/// </para>
///
/// <para>
/// <b>What this does not prove:</b> which of the fourteen steps maps to which operation. Six names
/// and fourteen steps is not a bijection, and guessing one would repeat the mistake this session has
/// now made five times. The names are recorded so the next round can look for the rest rather than
/// re-derive these.
/// </para>
/// </summary>
public static class NikePersistedOperations
{
    /// <summary>The GraphQL endpoint's persisted-query base, verbatim.</summary>
    public const string Base = "checkouts/internal/graphql/persisted?operationName=";

    /// <summary>The plain (non-persisted) endpoint, verbatim.</summary>
    public const string Endpoint = "/checkouts/internal/graphql";

    public const string CheckoutExtensionSessionToken = "CheckoutExtensionSessionToken";
    public const string PaypalDetails = "PaypalDetails";
    public const string PaypalToken = "PaypalToken";
    public const string PollForReceipt = "PollForReceipt";
    public const string Proposal = "Proposal";
    public const string SubmitForCompletion = "SubmitForCompletion";

    /// <summary>The six operation names, in the image's order.</summary>
    public static readonly IReadOnlyList<string> All = new[]
    {
        CheckoutExtensionSessionToken, PaypalDetails, PaypalToken, PollForReceipt, Proposal,
        SubmitForCompletion,
    };

    /// <summary>
    /// The three that look like the payment half of a checkout. Kept as a separate list so it is
    /// obvious this is a reading of the names, not a mapping of the steps.
    /// </summary>
    public static readonly IReadOnlyList<string> PaymentHalf = new[]
    {
        PaypalDetails, PaypalToken, SubmitForCompletion,
    };

    /// <summary>The full URL path for one operation.</summary>
    public static string Url(string operationName) => Base + operationName;

    /// <summary>True when <paramref name="name"/> is one of the six.</summary>
    public static bool IsKnown(string? name) =>
        !string.IsNullOrEmpty(name) && All.Contains(name, StringComparer.Ordinal);
}
