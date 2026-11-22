using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The address object a GraphQL document asks for as <c>AddressInput</c>.
///
/// <para>
/// <b>Observed</b> (R1372): the image keeps <c>recipientName</c> (0x147149A94), <c>addressLine1</c> (0x146F6EC6C),
/// <c>addressLine2</c> (0x146F6EC9C) and <c>locality</c> (0x146FC9852) as strings. The type name itself is not a
/// string anywhere, which is why the documents' <c>AddressInput!</c> annotation could not be resolved from the name.
///
/// <para>
/// <b>Refuted in the same round:</b> the first reading claimed code references for three of them on the strength of
/// disp32 byte-pattern hits. Decoding the referenced function's own literal list showed twenty literals and not one
/// address field, so a disp32 hit is a pattern until the function's literal set contains the name. What remains is
/// the four strings, not a construction.
/// </para>
///
/// <para>
/// <b>Observed elsewhere:</b> the sibling field names this project already sends come from their own documents —
/// <c>postcode</c>/<c>city</c>/<c>countryId</c>/<c>firstname</c>/<c>lastname</c> in Magento and the session family,
/// <c>postalCode</c>/<c>phoneNumber</c> in others.
/// </para>
///
/// <para>
/// <b>Not observed:</b> a single function that constructs all of them together, and that is why this is a model with
/// an explicit field list rather than a claim about one sender's object literal.
/// </para>
/// </summary>
public sealed class AddressInput
{
    /// <summary>The names the image spells this way.</summary>
    public static readonly string[] ModernFieldNames =
    {
        "recipientName", "addressLine1", "addressLine2", "locality",
    };

    /// <summary>The names the Magento and session documents use.</summary>
    public static readonly string[] DocumentFieldNames =
    {
        "firstname", "lastname", "street", "city", "postcode", "country_id", "telephone", "email",
    };

    public string? RecipientName { get; init; }
    public string? AddressLine1 { get; init; }
    public string? AddressLine2 { get; init; }
    public string? Locality { get; init; }
    public string? PostalCode { get; init; }
    public string? CountryCode { get; init; }
    public string? PhoneNumber { get; init; }
    public string? Email { get; init; }

    /// <summary>
    /// The object a document's <c>$address</c> variable takes. Only fields with a value are written: an empty string
    /// and an absent field are different things to a validator, and the documents' arguments are strict.
    /// </summary>
    public JObject ToJson()
    {
        var json = new JObject();
        if (!string.IsNullOrEmpty(RecipientName)) json["recipientName"] = RecipientName;
        if (!string.IsNullOrEmpty(AddressLine1)) json["addressLine1"] = AddressLine1;
        if (!string.IsNullOrEmpty(AddressLine2)) json["addressLine2"] = AddressLine2;
        if (!string.IsNullOrEmpty(Locality)) json["locality"] = Locality;
        if (!string.IsNullOrEmpty(PostalCode)) json["postalCode"] = PostalCode;
        if (!string.IsNullOrEmpty(CountryCode)) json["countryCode"] = CountryCode;
        if (!string.IsNullOrEmpty(PhoneNumber)) json["phoneNumber"] = PhoneNumber;
        if (!string.IsNullOrEmpty(Email)) json["email"] = Email;
        return json;
    }

    /// <summary>The field names this model can emit, for callers that need to check a document's argument.</summary>
    public static IReadOnlyList<string> EmittedFieldNames => new[]
    {
        "recipientName", "addressLine1", "addressLine2", "locality",
        "postalCode", "countryCode", "phoneNumber", "email",
    };
}
