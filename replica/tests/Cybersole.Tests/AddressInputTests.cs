using Cybersole.Stores.Flows;
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
