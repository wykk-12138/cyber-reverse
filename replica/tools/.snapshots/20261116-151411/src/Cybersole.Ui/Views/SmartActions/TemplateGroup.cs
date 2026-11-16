namespace Cybersole.Ui.Views.SmartActions;

/// <summary>
/// <c>Cybersole.Ui.Views.SmartActions.TemplateGroup</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Key</c>, <c>Templates</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class TemplateGroup
{
    /// <summary>Bound as <c>Key</c> — text; type inferred.</summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>Bound as <c>Templates</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Templates { get; set; } = new();
}
