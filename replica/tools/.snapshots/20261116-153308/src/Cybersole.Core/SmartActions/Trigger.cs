using System.Collections.Generic;

namespace Cybersole.SmartActions;

/// <summary>
/// <c>Cybersole.SmartActions.Trigger</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Description</c>, <c>Image</c>, <c>Name</c>, <c>Variables</c></c> are bound by the original, each with a getter and a setter.
/// <b>Inferred</b>: their CLR types and any cross-reference — the descriptor table records names and accessor
/// kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class Trigger
{
    /// <summary>Bound as <c>Description</c> — text; type inferred.</summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>Bound as <c>Image</c> — a path or url; type inferred.</summary>
    public string Image { get; set; } = string.Empty;

    /// <summary>Bound as <c>Name</c> — text; type inferred.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Bound as <c>Variables</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Variables { get; set; } = new();
}
