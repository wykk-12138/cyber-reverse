using System.Collections.Generic;

namespace Cybersole.SmartActions;

/// <summary>
/// <c>Cybersole.SmartActions.Filter</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Behaviour</c>, <c>Inputs</c>, <c>Operator</c>, <c>Variable</c></c> are bound by the original, each with a getter and a setter.
/// <b>Inferred</b>: their CLR types and any cross-reference — the descriptor table records names and accessor
/// kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class Filter
{
    /// <summary>Bound as <c>Behaviour</c> — text; type inferred.</summary>
    public string Behaviour { get; set; } = string.Empty;

    /// <summary>Bound as <c>Inputs</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Inputs { get; set; } = new();

    /// <summary>Bound as <c>Operator</c> — text — likely the Operator's Name; type inferred.</summary>
    public string Operator { get; set; } = string.Empty;

    /// <summary>Bound as <c>Variable</c> — text — likely the Variable's Description; type inferred.</summary>
    public string Variable { get; set; } = string.Empty;
}
