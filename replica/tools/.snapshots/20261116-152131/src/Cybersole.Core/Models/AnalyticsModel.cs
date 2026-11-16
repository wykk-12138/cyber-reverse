namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.Analytics</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Spent</c>, <c>Success</c></c> are bound by the original, with getters and setters.
/// <b>Inferred</b>: the member types (`decimal`, `bool`) — the descriptor table records names and accessor kinds, not CLR
/// types, so these are guesses from the member names.
/// <b>Unknown</b>: behaviour. Nothing here establishes what the original did with these values.
/// </remarks>
public sealed class Analytics
{
    /// <summary>Bound as <c>Spent</c> (getter and setter in the original) — money spent.</summary>
    public decimal Spent { get; set; } = 0m;

    /// <summary>Bound as <c>Success</c> (getter and setter in the original) — whether it succeeded.</summary>
    public bool Success { get; set; }
}
