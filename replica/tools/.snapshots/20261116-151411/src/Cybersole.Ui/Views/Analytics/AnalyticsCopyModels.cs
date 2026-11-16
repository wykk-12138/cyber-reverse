namespace Cybersole.Ui.Views.Analytics.Modals;

/// <summary>
/// <c>Cybersole.Ui.Views.Analytics.Modals.CheckoutProperty</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// **Observed**: the members <c><c>Key</c>, <c>Value</c></c> are bound by the original (getters).
/// **Inferred**: that they are <c>string</c> — the descriptor table records member names and accessor kinds, not
/// CLR types; text is a guess from the names.
/// **Unknown**: behaviour. Nothing here establishes what the original did with these values.
/// </remarks>
public sealed class CheckoutProperty : object
{
    /// <summary>Bound as <c>Key</c> (getter and setter in the original).</summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>Bound as <c>Value</c> (getter and setter in the original).</summary>
    public string Value { get; set; } = string.Empty;
}
