using Cybersole.Stores.Flows;
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

    /// <summary>
    /// R1372: the four names are in the image's string table; a claim that three of them are referenced was withdrawn
    /// after the referenced function's literal list contained none of them. This test records the distinction so the
    /// next reader does not inherit the over-claim.
    /// </summary>
    [Fact]
    public void TheNamesSurviveButTheReferenceClaimDoesNot()
    {
        Assert.Equal(4, AddressInput.ModernFieldNames.Length);
        Assert.Contains("recipientName", AddressInput.ModernFieldNames);
        Assert.Contains("addressLine1", AddressInput.ModernFieldNames);
        Assert.Contains("addressLine2", AddressInput.ModernFieldNames);
        Assert.Contains("locality", AddressInput.ModernFieldNames);

        // The CreditCard sender's twenty literals, decoded in this round: no address field among them.
        Assert.DoesNotContain("addressLine1", new[]
        {
            " ", "/finalize", "CreditCard", "Submit order", "api/checkout/v1/orders/", "application/json",
            "cardCvv", "cardExpiryMonth", "cardExpiryYear", "cardName", "cardNumber", "paymentMethodId",
            "paymentMethodType", "savePaymentMethodAsToken",
        });
    }
}
