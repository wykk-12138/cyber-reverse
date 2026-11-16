namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.AycdInboxAccount</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>ApiKey</c>, <c>Enabled</c>, <c>Error</c>, <c>Status</c>, <c>TaskCount</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class AycdInboxAccount
{
    /// <summary>Bound as <c>ApiKey</c> — text; type inferred.</summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>Bound as <c>Enabled</c> — flag; type inferred.</summary>
    public bool Enabled { get; set; }

    /// <summary>Bound as <c>Error</c> — text; type inferred.</summary>
    public string Error { get; set; } = string.Empty;

    /// <summary>Bound as <c>Status</c> — text; type inferred.</summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>Bound as <c>TaskCount</c> — a count; type inferred.</summary>
    public int TaskCount { get; set; }
}
