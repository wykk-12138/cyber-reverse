namespace Cybersole.Ui.Views.Settings;

/// <summary>
/// <c>Cybersole.Ui.Views.Settings.KeyBindSection</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Key</c>, <c>Shortcuts</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class KeyBindSection
{
    /// <summary>Bound as <c>Key</c> — text; type inferred.</summary>
    public string Key { get; set; } = string.Empty;

    /// <summary>Bound as <c>Shortcuts</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Shortcuts { get; set; } = new();
}
