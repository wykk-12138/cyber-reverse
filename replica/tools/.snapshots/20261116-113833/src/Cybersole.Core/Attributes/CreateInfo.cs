namespace Cybersole.Attributes;

/// <summary>
/// <c>Cybersole.Attributes.CreateInfo</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Name</c>, <c>Properties</c></c> are bound by the original, with getters and setters.
/// <b>Inferred</b>: the member types (`string`, `string`) — the descriptor table records names and accessor kinds, not CLR
/// types, so these are guesses from the member names.
/// <b>Unknown</b>: behaviour. Nothing here establishes what the original did with these values.
/// </remarks>
public sealed class CreateInfo
{
    /// <summary>Bound as <c>Name</c> (getter and setter in the original) — the attribute's name.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Bound as <c>Properties</c> (getter and setter in the original) — its payload.</summary>
    public string Properties { get; set; } = string.Empty;
}
