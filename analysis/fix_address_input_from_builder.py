"""R1378: the AddressInput builder is found, and its field list is not the one I guessed.

`0x140AD5B10` references recipientName and carries, in its own literal table, exactly an address object plus a PayPal
Express cart request:

    recipientName  firstName  lastName  line1  line2  city  postalCode  countryCode  phone  email
    billingAddress  checkoutType  EXPRESS  OTHER  payerId  nonce  details
    /cart/paypal  application/json  PayPalAccount  Store  "Submit info"

So AddressInput is built here, its fields are line1/line2 (not addressLine1/addressLine2) and city/postalCode, and the
request around it is a PayPal Express cart submission. R1372's model guessed the modern Shopify-shaped names because
those are the strings the image happens to keep; this is the construction, and it disagrees.

The second function, 0x140F4BA90, is another sender with the same address names and a FootLocker-shaped header set.

Usage: python analysis/fix_address_input_from_builder.py
"""
import io

MODEL = 'replica/src/Cybersole.Stores/Flows/AddressInput.cs'
CART = 'replica/src/Cybersole.Stores/Flows/PayPalExpressCart.cs'
TESTS = 'replica/tests/Cybersole.Tests/AddressInputTests.cs'
CART_TESTS = 'replica/tests/Cybersole.Tests/PayPalExpressCartTests.cs'

model = '''using Newtonsoft.Json.Linq;

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
'''

io.open(MODEL, 'w', encoding='utf-8', newline='').write(model)
print('AddressInput rewritten to the builder\'s fields')

cart = '''using System;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Http;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// The PayPal Express cart submission that carries an <see cref="AddressInput"/>.
///
/// <para>
/// <b>Observed</b> (R1378): <c>sub_140AD5B10</c> posts to <c>/cart/paypal</c> with <c>application/json</c>, and its
/// literals name <c>billingAddress</c>, <c>checkoutType</c> with the two values <c>EXPRESS</c> and <c>OTHER</c>,
/// <c>payerId</c>, <c>details</c>, <c>nonce</c>, <c>PayPalAccount</c>, <c>Store</c> and the label "Submit info".
/// </para>
///
/// <para>
/// <b>Not observed:</b> a host. The path is relative, so the origin is the caller's.
/// </para>
/// </summary>
public static class PayPalExpressCart
{
    /// <summary>The relative path the sender builds.</summary>
    public const string Path = "/cart/paypal";

    /// <summary>The Express checkout type.</summary>
    public const string CheckoutTypeExpress = "EXPRESS";

    /// <summary>The other checkout type the sender names.</summary>
    public const string CheckoutTypeOther = "OTHER";

    /// <summary>The step's label.</summary>
    public const string SubmitInfoMessage = "Submit info";

    /// <summary>The body field names the sender names.</summary>
    public static readonly string[] BodyFieldNames =
    {
        "billingAddress", "checkoutType", "payerId", "nonce", "details",
    };

    /// <summary>The url for one origin.</summary>
    public static string UrlFor(string origin) => origin.TrimEnd('/') + Path;

    /// <summary>
    /// The request body. The address is the builder's object; the checkout type is one of the two the sender names.
    /// </summary>
    public static JObject Body(
        AddressInput address, string checkoutType, string? payerId, string? nonce, JObject? details = null)
    {
        if (checkoutType != CheckoutTypeExpress && checkoutType != CheckoutTypeOther)
            throw new ArgumentOutOfRangeException(nameof(checkoutType),
                "checkout type is one of the two values the sender names");

        var body = new JObject
        {
            ["billingAddress"] = address?.ToJson() ?? new JObject(),
            ["checkoutType"] = checkoutType,
        };
        if (!string.IsNullOrEmpty(payerId)) body["payerId"] = payerId;
        if (!string.IsNullOrEmpty(nonce)) body["nonce"] = nonce;
        if (details is not null) body["details"] = details;
        return body;
    }

    /// <summary>Post the submission.</summary>
    public static async Task<(JObject? Data, string Error)> SendAsync(
        FlowContext c, string? origin, JObject body, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(origin)) return (null, "paypal-express: no origin");

        try
        {
            var reply = await GatewayHttp
                .PostAsync(c, UrlFor(origin!), body, "paypal-express", ct).ConfigureAwait(false);
            if (reply is null) return (null, "paypal-express: no reply");

            var data = reply["data"] as JObject ?? reply;
            return (data, string.Empty);
        }
        catch (Exception ex)
        {
            return (null, "paypal-express: " + ex.GetType().Name);
        }
    }
}
'''

io.open(CART, 'w', encoding='utf-8', newline='').write(cart)
print('wrote %s' % CART)

tests = '''using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1378: AddressInput's fields come from the function that builds one, not from the strings that happen to exist.
/// </summary>
public sealed class AddressInputTests
{
    [Fact]
    public void TheFieldsAreTheBuilders()
    {
        Assert.Equal(new[]
        {
            "recipientName", "firstName", "lastName", "line1", "line2", "city", "postalCode", "countryCode",
            "phone", "email",
        }, AddressInput.FieldNames);
    }

    /// <summary>The two names R1372 assumed — addressLine1/addressLine2 — are not what the builder fills.</summary>
    [Fact]
    public void TheAssumedNamesAreNotTheBuilders()
    {
        Assert.DoesNotContain("addressLine1", AddressInput.FieldNames);
        Assert.DoesNotContain("addressLine2", AddressInput.FieldNames);
        Assert.Contains("line1", AddressInput.FieldNames);
        Assert.Contains("line2", AddressInput.FieldNames);
    }

    [Fact]
    public void EmptyFieldsAreNotWritten()
    {
        var json = new AddressInput { RecipientName = "A", Line1 = "1 Main St", City = "" }.ToJson();

        Assert.Equal("A", json["recipientName"]!.ToObject<string>());
        Assert.Equal("1 Main St", json["line1"]!.ToObject<string>());
        Assert.Null(json["city"]);
        Assert.Equal(2, json.Count);
    }
}
'''

io.open(TESTS, 'w', encoding='utf-8', newline='').write(tests)
print('rewrote the AddressInput tests')

cart_tests = '''using System;
using Cybersole.Stores.Flows;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>R1378: the PayPal Express cart submission that carries an AddressInput.</summary>
public sealed class PayPalExpressCartTests
{
    [Fact]
    public void ThePathAndVocabularyAreTheObservedOnes()
    {
        Assert.Equal("/cart/paypal", PayPalExpressCart.Path);
        Assert.Equal("EXPRESS", PayPalExpressCart.CheckoutTypeExpress);
        Assert.Equal("OTHER", PayPalExpressCart.CheckoutTypeOther);
        Assert.Equal("Submit info", PayPalExpressCart.SubmitInfoMessage);
        Assert.Equal(new[] { "billingAddress", "checkoutType", "payerId", "nonce", "details" },
            PayPalExpressCart.BodyFieldNames);
        Assert.Equal("https://shop.test/cart/paypal", PayPalExpressCart.UrlFor("https://shop.test/"));
    }

    [Fact]
    public void TheBodyCarriesTheAddressObject()
    {
        var address = new AddressInput { RecipientName = "A", Line1 = "1 Main", City = "Town", CountryCode = "BE" };
        var body = PayPalExpressCart.Body(address, PayPalExpressCart.CheckoutTypeExpress, "P-1", "n-1");

        Assert.Equal("EXPRESS", body["checkoutType"]!.ToObject<string>());
        Assert.Equal("1 Main", body["billingAddress"]!["line1"]!.ToObject<string>());
        Assert.Equal("BE", body["billingAddress"]!["countryCode"]!.ToObject<string>());
        Assert.Equal("P-1", body["payerId"]!.ToObject<string>());
    }

    [Fact]
    public void OnlyTheTwoCheckoutTypesAreAccepted()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            PayPalExpressCart.Body(new AddressInput(), "GUEST", null, null));
    }
}
'''

io.open(CART_TESTS, 'w', encoding='utf-8', newline='').write(cart_tests)
print('wrote %s' % CART_TESTS)
