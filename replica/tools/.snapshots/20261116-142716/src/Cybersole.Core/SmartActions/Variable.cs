namespace Cybersole.SmartActions;

/// <summary>
/// <c>Cybersole.SmartActions.Variable</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Description</c></c> are bound by the original, each with a getter and a setter.
/// <b>Inferred</b>: their CLR types and any cross-reference — the descriptor table records names and accessor
/// kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class Variable
{
    /// <summary>Bound as <c>Description</c> — text; type inferred.</summary>
    public string Description { get; set; } = string.Empty;
}
