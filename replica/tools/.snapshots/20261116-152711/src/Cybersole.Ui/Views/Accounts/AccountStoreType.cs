namespace Cybersole.Ui.Views.Accounts;

/// <summary>
/// <c>Cybersole.Ui.Views.Accounts.AccountStoreType</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Stores</c>, <c>Type</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class AccountStoreType
{
    /// <summary>Bound as <c>Stores</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Stores { get; set; } = new();

    /// <summary>Bound as <c>Type</c> — text; type inferred.</summary>
    public string Type { get; set; } = string.Empty;
}
