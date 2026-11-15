namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.CreateInputModel</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>AutoQuantity</c>, <c>Color</c>, <c>Currency</c>, <c>Input</c>, <c>MaxPrice</c>, <c>MinPrice</c>, <c>Quantity</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class CreateInputModel
{
    /// <summary>Bound as <c>AutoQuantity</c> — flag; type inferred.</summary>
    public bool AutoQuantity { get; set; }

    /// <summary>Bound as <c>Color</c> — text; type inferred.</summary>
    public string Color { get; set; } = string.Empty;

    /// <summary>Bound as <c>Currency</c> — text; type inferred.</summary>
    public string Currency { get; set; } = string.Empty;

    /// <summary>Bound as <c>Input</c> — text; type inferred.</summary>
    public string Input { get; set; } = string.Empty;

    /// <summary>Bound as <c>MaxPrice</c> (getter only in the original) — a price; type inferred.</summary>
    public decimal MaxPrice { get; init; }

    /// <summary>Bound as <c>MinPrice</c> — a price; type inferred.</summary>
    public decimal MinPrice { get; set; }

    /// <summary>Bound as <c>Quantity</c> — a count; type inferred.</summary>
    public int Quantity { get; set; }
}
