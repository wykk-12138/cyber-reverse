using System.Collections.Generic;

namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.ValueGroup</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Name</c>, <c>Preview</c>, <c>Values</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class ValueGroup
{
    /// <summary>Bound as <c>Name</c> — text; type inferred.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Bound as <c>Preview</c> (getter only in the original) — text; type inferred.</summary>
    public string Preview { get; init; } = string.Empty;

    /// <summary>Bound as <c>Values</c> — a collection; element type unknown; type inferred.</summary>
    public List<string> Values { get; set; } = new();
}
