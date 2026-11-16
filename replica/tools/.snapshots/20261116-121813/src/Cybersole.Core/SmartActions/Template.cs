using System.Collections.Generic;

namespace Cybersole.SmartActions;

/// <summary>
/// <c>Cybersole.SmartActions.Template</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Actions</c>, <c>Description</c>, <c>Filters</c>, <c>Title</c>, <c>Trigger</c></c> are bound by the original, each with a getter and a setter.
/// <b>Inferred</b>: their CLR types and any cross-reference — the descriptor table records names and accessor
/// kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class Template
{
    /// <summary>Bound as <c>Actions</c> — a collection of Action; inferred from the name; type inferred.</summary>
    public List<Action> Actions { get; set; } = new();

    /// <summary>Bound as <c>Description</c> — text; type inferred.</summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>Bound as <c>Filters</c> — a collection of Filter; inferred from the name; type inferred.</summary>
    public List<Filter> Filters { get; set; } = new();

    /// <summary>Bound as <c>Title</c> — text; type inferred.</summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>Bound as <c>Trigger</c> — text; type inferred.</summary>
    public string Trigger { get; set; } = string.Empty;
}
