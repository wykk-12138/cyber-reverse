using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The address object the cart documents take as <c>AddressInput</c>.
///
/// <para>
/// <b>Observed</b> (R1378): <c>sub_140AD5B10</c> builds one, and its literal table names the fields it fills —
/// <c>recipientName</c>, <c>firstName</c>, <c>lastName</c>, <c>line1</c>, <c>line2</c>, <c>city</c>,
/// <c>postalCode</c>, <c>countryCode</c>, <c>phone</c> and <c>email</c> — beside the request it belongs to
/// (<c>/cart/paypal</c>, <c>checkoutType</c>, <c>payerId</c>, <c>nonce</c>, <c>billingAddress</c>,
/// "Submit info").
/// </para>
///
/// <para>
/// <b>Corrected:</b> R1372 read <c>addressLine1</c>, <c>addressLine2</c> and <c>locality</c> out of the string table
/// and assumed they were this object's fields. They are in the image, but the builder does not use them: it uses
/// <c>line1</c>, <c>line2</c> and <c>city</c>. The string table says what exists; the builder says what is used.
/// </para>
/// </summary>
public sealed class AddressInput
{
    /// <summary>The field names the builder fills, in its order.</summary>
    public static readonly string[] FieldNames =
    {
        "recipientName", "firstName", "lastName", "line1", "line2", "city", "postalCode", "countryCode",
        "phone", "email",
    };

    public string? RecipientName { get; init; }
    public string? FirstName { get; init; }
    public string? LastName { get; init; }
    public string? Line1 { get; init; }
    public string? Line2 { get; init; }
    public string? City { get; init; }
    public string? PostalCode { get; init; }
    public string? CountryCode { get; init; }
    public string? Phone { get; init; }
    public string? Email { get; init; }

    /// <summary>
    /// The object a document's address argument takes. Only fields with a value are written, because the documents'
    /// arguments are strict about what they accept.
    /// </summary>
    public JObject ToJson()
    {
        var json = new JObject();
        if (!string.IsNullOrEmpty(RecipientName)) json["recipientName"] = RecipientName;
        if (!string.IsNullOrEmpty(FirstName)) json["firstName"] = FirstName;
        if (!string.IsNullOrEmpty(LastName)) json["lastName"] = LastName;
        if (!string.IsNullOrEmpty(Line1)) json["line1"] = Line1;
        if (!string.IsNullOrEmpty(Line2)) json["line2"] = Line2;
        if (!string.IsNullOrEmpty(City)) json["city"] = City;
        if (!string.IsNullOrEmpty(PostalCode)) json["postalCode"] = PostalCode;
        if (!string.IsNullOrEmpty(CountryCode)) json["countryCode"] = CountryCode;
        if (!string.IsNullOrEmpty(Phone)) json["phone"] = Phone;
        if (!string.IsNullOrEmpty(Email)) json["email"] = Email;
        return json;
    }
}
