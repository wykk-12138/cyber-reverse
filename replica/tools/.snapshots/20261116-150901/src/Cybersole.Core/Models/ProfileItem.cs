namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.ProfileItem</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Description</c>, <c>Name</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types — the descriptor table records names and accessor kinds only.
/// <b>Unknown</b>: behaviour.
/// </remarks>
public sealed class ProfileItem
{
    /// <summary>Bound as <c>Description</c> (getter only in the original) — getter only; text; type inferred.</summary>
    public string Description { get; init; } = string.Empty;

    /// <summary>Bound as <c>Name</c> (getter only in the original) — getter only; text; type inferred.</summary>
    public string Name { get; init; } = string.Empty;
}
