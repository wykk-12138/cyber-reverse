using Cybersole.Core.Models;
using Cybersole.Http.Stores;
using Xunit;

namespace Cybersole.Tests;

public class CheckoutFormBuilderTests
{
    private static Profile FullProfile() => new()
    {
        Name = "P1",
        Email = "profile@example.com",
        FirstName = "Ada",
        LastName = "Lovelace",
        Phone = "5551234",
        Address1 = "1 Analytical Way",
        Address2 = "Apt 3",
        City = "London",
        State = "LDN",
        Zip = "EC1A",
        Country = "GB",
        CardNumber = "4111 1111 1111 1111",
        CardExpiry = "1/28",
        CardCvv = "123",
        CardName = "A Lovelace",
    };

    [Fact]
    public void Account_Email_Wins_Over_Profile_Email()
    {
        var form = CheckoutFormBuilder.Build(FullProfile(), new Account { Email = "acc@store.com" });
        Assert.Equal("acc@store.com", form["email"]);
    }

    [Fact]
    public void Falls_Back_To_Profile_Email_Without_Account()
    {
        var form = CheckoutFormBuilder.Build(FullProfile(), null);
        Assert.Equal("profile@example.com", form["email"]);
    }

    [Fact]
    public void Maps_Address_And_Size()
    {
        var form = CheckoutFormBuilder.Build(FullProfile(), null, "10.5");
        Assert.Equal("Ada", form["firstName"]);
        Assert.Equal("Lovelace", form["lastName"]);
        Assert.Equal("1 Analytical Way", form["address1"]);
        Assert.Equal("EC1A", form["zip"]);
        Assert.Equal("GB", form["country"]);
        Assert.Equal("10.5", form["size"]);
    }

    [Fact]
    public void Strips_Card_Formatting()
    {
        var form = CheckoutFormBuilder.Build(FullProfile(), null);
        Assert.Equal("4111111111111111", form["cardNumber"]);
    }

    [Fact]
    public void Normalises_Expiry_Variants()
    {
        Assert.Equal("01/28", CheckoutFormBuilder.NormaliseExpiry("1/28"));
        Assert.Equal("01/28", CheckoutFormBuilder.NormaliseExpiry("01/2028"));
        Assert.Equal("01/28", CheckoutFormBuilder.NormaliseExpiry("0128"));
        Assert.Equal("12/30", CheckoutFormBuilder.NormaliseExpiry("12 / 2030"));
        Assert.Equal(string.Empty, CheckoutFormBuilder.NormaliseExpiry(null));
    }

    [Fact]
    public void Card_Fields_Omitted_When_No_Card()
    {
        var profile = FullProfile();
        profile.CardNumber = string.Empty;
        var form = CheckoutFormBuilder.Build(profile, null);
        Assert.False(form.ContainsKey("cardNumber"));
        Assert.False(form.ContainsKey("cardCvv"));
    }

    [Fact]
    public void Password_Copied_From_Account()
    {
        var form = CheckoutFormBuilder.Build(FullProfile(), new Account { Email = "a@b.c", Password = "s3cret" });
        Assert.Equal("s3cret", form["password"]);
    }

    [Fact]
    public void Empty_Inputs_Produce_Empty_Form()
    {
        var form = CheckoutFormBuilder.Build(null, null);
        Assert.Empty(form);
    }
}
