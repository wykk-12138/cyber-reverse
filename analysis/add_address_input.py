"""R1372: AddressInput's field names, from the strings the image keeps and the code that references them.

The type name never appears as a string, which is why this sat in the open list as "shape unknown". But a sender has to
write the field names into the object, and four of them are in the image's own string table with real code references:

    recipientName   0x147149A94   referenced at 0x140AD5FAD
    addressLine1    0x146F6EC6C   referenced at 0x140A42650
    addressLine2    0x146F6EC9C   referenced at 0x140AAEA55
    locality        0x146FC9852   (no code reference found)

The first three are what a modern address type is made of, and the sibling names this project already handles
(postcode, city, countryId, firstname, lastname, phone) come from the Magento and session documents. What this round
does is pin the four that the image itself spells this way, and record which one lacks a reference rather than pretend
all four are equally attested.

IDA was down when this was written, so the sender at 0x140AAEA55 has not been read yet; that is the next round's job
and the reason the model below says "observed as strings and references" rather than "observed in a construction".
"""
import io

OUT = 'replica/src/Cybersole.Stores/Flows/AddressInput.cs'
TESTS = 'replica/tests/Cybersole.Tests/AddressInputTests.cs'

source = '''using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The address object a GraphQL document asks for as <c>AddressInput</c>.
///
/// <para>
/// <b>Observed</b> (R1372): the image keeps <c>recipientName</c>, <c>addressLine1</c>, <c>addressLine2</c> and
/// <c>locality</c> as strings, and code references the first three (0x140AD5FAD, 0x140A42650, 0x140AAEA55). The
/// type name itself is not a string anywhere, which is why the documents' <c>AddressInput!</c> annotation could not
/// be resolved from the name alone.
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
'''

io.open(OUT, 'w', encoding='utf-8', newline='').write(source)
print('wrote %s' % OUT)

tests = '''using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1372: AddressInput's field names. The type name is not a string in the image; these four are, and three of them
/// have code references, which is what makes the list evidence rather than a guess.
/// </summary>
public sealed class AddressInputTests
{
    [Fact]
    public void TheNamesTheImageSpellsAreTheObservedOnes()
    {
        Assert.Equal(new[] { "recipientName", "addressLine1", "addressLine2", "locality" },
            AddressInput.ModernFieldNames);
    }

    /// <summary>An empty string and a missing field are different to a strict document argument.</summary>
    [Fact]
    public void EmptyFieldsAreNotWritten()
    {
        var json = new AddressInput
        {
            RecipientName = "A",
            AddressLine1 = "1 Main St",
            Locality = "",
            PostalCode = null,
        }.ToJson();

        Assert.Equal("A", json["recipientName"]!.ToObject<string>());
        Assert.Equal("1 Main St", json["addressLine1"]!.ToObject<string>());
        Assert.Null(json["locality"]);
        Assert.Null(json["postalCode"]);
        Assert.Equal(2, json.Count);
    }

    [Fact]
    public void EveryEmittedNameIsInTheModel()
    {
        var json = new AddressInput
        {
            RecipientName = "A", AddressLine1 = "b", AddressLine2 = "c", Locality = "d",
            PostalCode = "e", CountryCode = "f", PhoneNumber = "g", Email = "h",
        }.ToJson();

        Assert.Equal(AddressInput.EmittedFieldNames.Count, json.Count);
        foreach (var name in AddressInput.EmittedFieldNames) Assert.NotNull(json[name]);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('wrote %s' % TESTS)
