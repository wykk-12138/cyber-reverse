using System.Collections.Generic;

namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.Store</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>ColorSupport</c>, <c>Currency</c>, <c>Elements</c>, <c>Info</c>, <c>Name</c>, <c>Url</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class Store
{
    /// <summary>Bound as <c>ColorSupport</c> — flag; type inferred.</summary>
    public bool ColorSupport { get; set; }

    /// <summary>Bound as <c>Currency</c> — text; type inferred.</summary>
    public string Currency { get; set; } = string.Empty;

    /// <summary>Bound as <c>Elements</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Elements { get; set; } = new();

    /// <summary>Bound as <c>Info</c> (getter only in the original) — text; type inferred.</summary>
    public string Info { get; init; } = string.Empty;

    /// <summary>Bound as <c>Name</c> — text; type inferred.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Bound as <c>Url</c> — text; type inferred.</summary>
    public string Url { get; set; } = string.Empty;
}
