namespace Cybersole.Attributes;

/// <summary>
/// <c>Cybersole.Attributes.Platform</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>InputType</c>, <c>MultiCart</c>, <c>Name</c>, <c>QuantityAutoAdjustSupport</c>, <c>QuantitySupport</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class Platform
{
    /// <summary>Bound as <c>InputType</c> — text; type inferred.</summary>
    public string InputType { get; set; } = string.Empty;

    /// <summary>Bound as <c>MultiCart</c> — flag; type inferred.</summary>
    public bool MultiCart { get; set; }

    /// <summary>Bound as <c>Name</c> — text; type inferred.</summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>Bound as <c>QuantityAutoAdjustSupport</c> — flag; type inferred.</summary>
    public bool QuantityAutoAdjustSupport { get; set; }

    /// <summary>Bound as <c>QuantitySupport</c> — flag; type inferred.</summary>
    public bool QuantitySupport { get; set; }
}
