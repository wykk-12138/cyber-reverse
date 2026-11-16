namespace Cybersole.Ui.Views.Accounts;

/// <summary>
/// <c>Cybersole.Ui.Views.Accounts.AccountStoreEntry</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>IsSelected</c>, <c>Name</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class AccountStoreEntry
{
    /// <summary>Bound as <c>IsSelected</c> — flag; type inferred.</summary>
    public bool IsSelected { get; set; }

    /// <summary>Bound as <c>Name</c> — text; type inferred.</summary>
    public string Name { get; set; } = string.Empty;
}
