using System.Collections.Generic;

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

    // R566: six more members the descriptor table records and I missed when this class was first written.
    // All six carry getter+setter there, so they are properties; three of them are verb-shaped
    // (Plus/Minus/TogglePriceCheck) and are most likely bound to commands, which a property cannot express —
    // behaviour for those is Unknown.
    /// <summary>Bound as <c>Minus</c> (getter and setter in the original) — verb-shaped; behaviour Unknown.</summary>
    public string? Minus { get; set; }

    /// <summary>Bound as <c>Plus</c> (getter and setter in the original) — verb-shaped; behaviour Unknown.</summary>
    public string? Plus { get; set; }

    /// <summary>Bound as <c>PriceCheckVisible</c> (getter only in the original) — a flag; type inferred.</summary>
    public bool PriceCheckVisible { get; init; }

    /// <summary>Bound as <c>Sizes</c> (getter and setter in the original) — a collection; element type unknown.</summary>
    public List<string> Sizes { get; set; } = new();

    /// <summary>Bound as <c>Symbol</c> (getter only in the original) — text; type inferred.</summary>
    public string Symbol { get; init; } = string.Empty;

    /// <summary>Bound as <c>TogglePriceCheck</c> (getter and setter in the original) — verb-shaped; behaviour Unknown.</summary>
    public string? TogglePriceCheck { get; set; }
}
