namespace Cybersole.Models;

/// <summary>
/// A state or province, as the image models it: one member, a name.
///
/// <para>
/// Evidence: the descriptor run at 0x143211f9d lists
/// <c>Cybersole.Models.State,Cybersole.Core.Name!Getter</c> and <c>!Setter</c> and nothing else, while
/// <c>Cybersole.Models.Country</c> carries <c>Name</c>, <c>Code</c> and <c>States</c>, and
/// <c>Cybersole.Models.Address</c> carries <c>State</c> beside <c>Country</c> and <c>Barangay</c>.
/// So the abbreviation lives on the country, not on the state — this type is the name and only the name.
/// </para>
/// </summary>
public sealed record State(string Name);

/// <summary>A country with its states, carrying the code the checkout forms post.</summary>
public sealed record Country(string Name, string Code, System.Collections.Generic.IReadOnlyList<State> States);

/// <summary>
/// The shipping or billing address a checkout posts, in the image's field order.
///
/// <para>
/// Evidence: the same descriptor run lists FirstName, LastName, Address1, Address2, City, ZipCode, Country,
/// State and Barangay on <c>Cybersole.Models.Address</c>. The Philippine field is part of the model because the
/// image has it, not because a store happens to ask for it.
/// </para>
/// </summary>
public sealed record Address(
    string? FirstName,
    string? LastName,
    string? Address1,
    string? Address2,
    string? City,
    string? ZipCode,
    Country? Country,
    State? State,
    string? Barangay);
