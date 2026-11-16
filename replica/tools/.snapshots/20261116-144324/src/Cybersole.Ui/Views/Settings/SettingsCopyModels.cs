namespace Cybersole.Ui.Views.Settings;

/// <summary>
/// <c>Cybersole.Ui.Views.Settings.ErrorEntry</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// **Observed**: the members <c><c>Key</c>, <c>Value</c></c> are bound by the original (getters).
/// **Inferred**: that they are <c>string</c> — the descriptor table records member names and accessor kinds, not
/// CLR types; text is a guess from the names.
/// **Unknown**: behaviour. Nothing here establishes what the original did with these values.
/// </remarks>
public sealed class ErrorEntry : object
{
    /// <summary>Bound as <c>Key</c> (getter and setter in the original).</summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>Bound as <c>Value</c> (getter and setter in the original).</summary>
    public string Value { get; set; } = string.Empty;
}


/// <summary>
/// <c>Cybersole.Ui.Views.Settings.LocalizedOption</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// **Observed**: the members <c><c>Text</c>, <c>Value</c></c> are bound by the original (getters (one is getter-only)).
/// **Inferred**: that they are <c>string</c> — the descriptor table records member names and accessor kinds, not
/// CLR types; text is a guess from the names.
/// **Unknown**: behaviour. Nothing here establishes what the original did with these values.
/// </remarks>
public sealed class LocalizedOption : object
{
    /// <summary>Bound as <c>Text</c> (getter only in the descriptor table).</summary>
    public string Text { get; init; } = string.Empty;

    /// <summary>Bound as <c>Value</c> (getter and setter in the original).</summary>
    public string Value { get; set; } = string.Empty;
}
