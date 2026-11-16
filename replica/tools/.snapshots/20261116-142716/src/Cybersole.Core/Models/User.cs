namespace Cybersole.Models;

/// <summary>
/// <c>Cybersole.Models.User</c> — recovered from the original's binding table.
/// </summary>
/// <remarks>
/// <b>Observed</b>: the members <c><c>Discord</c>, <c>Email</c>, <c>FirstName</c>, <c>Image</c>, <c>IsStaff</c>, <c>LastName</c></c> are bound by the original.
/// <b>Inferred</b>: their CLR types. The descriptor table records names and accessor kinds, not types; the guesses
/// and their reasons are on each member.
/// <b>Unknown</b>: behaviour, and any element type not shown.
/// </remarks>
public sealed class User
{
    /// <summary>Bound as <c>Discord</c> — text; type inferred.</summary>
    public string Discord { get; set; } = string.Empty;

    /// <summary>Bound as <c>Email</c> — text; type inferred.</summary>
    public string Email { get; set; } = string.Empty;

    /// <summary>Bound as <c>FirstName</c> — text; type inferred.</summary>
    public string FirstName { get; set; } = string.Empty;

    /// <summary>Bound as <c>Image</c> — text; type inferred.</summary>
    public string Image { get; set; } = string.Empty;

    /// <summary>Bound as <c>IsStaff</c> (getter only in the original) — flag; type inferred.</summary>
    public bool IsStaff { get; init; }

    /// <summary>Bound as <c>LastName</c> — text; type inferred.</summary>
    public string LastName { get; set; } = string.Empty;
}
