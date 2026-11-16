namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.NotificationSound</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>SoundLocation</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class NotificationSound
{
    /// <summary>Bound as <c>SoundLocation</c> (getter only in the original) — getter only; a path; type inferred.</summary>
    public string SoundLocation { get; init; } = string.Empty;
}
