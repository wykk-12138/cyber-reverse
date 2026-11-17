using System.Collections.Generic;
using System.Threading.Tasks;
using Cybersole.Core.Models;
using Cybersole.Http.Stores;
using Cybersole.Stores.Flows;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1006: the shortage disposition comes from the response body, because the artifact has no status-code table.
///
/// <para>
/// Searching the image for 409 finds forty hexadecimal hashes and nothing else, and Conflict finds only .NET enum
/// names (R1005). What it does carry is <c>Out of stock (reservation failed), retrying</c> and <c>Out of stock (decoy)</c>
/// beside a <c>get_DecoyActive</c> property. So a failed reservation is worth another attempt, a decoy is bait and must
/// not be, and the plain wordings mean the shelf really is empty.
/// </para>
///
/// <para>
/// These drive the real checkout path against a server rather than poking the classifier, which is private and should
/// stay private. What they pin is the two markers pointing in opposite directions: a test that only checked
/// "reservation failed retries" would stay green if decoy retried too.
/// </para>
/// </summary>
public sealed class ShortageMessageTests
{
    private static FlowContext Ctx(Cybersole.Services.AppServices services, string baseUrl) => new()
    {
        Http = services.Http,
        Url = baseUrl + "/products/x",
        Product = new Product
        {
            Name = "x",
            Url = baseUrl + "/products/x",
            Sizes = new List<string> { "10" },
        },
        ProfileData = new Profile
        {
            Email = "a@b.c", FirstName = "A", LastName = "B", Address1 = "1 St",
            City = "C", State = "S", Zip = "1", Country = "US",
        },
        Card = new Card { Number = "4111111111111111", Month = "12", Year = "30", Cvv = "123" },
        TimeoutSeconds = 5,
    };

    /// <summary>Everything succeeds except the cart, which answers 409 with whatever body the case is about.</summary>
    private static async Task<CheckoutOutcome> CheckoutWithCartBody(string cartBody)
    {
        using var services = TestServices.Create();
        using var store = new TinyServer((req, _) =>
        {
            var path = req.Url!.AbsolutePath;

            if (path == "/") return (200, "<html></html>");
            if (path.EndsWith(".js", System.StringComparison.Ordinal) && path.StartsWith("/products/"))
                return (200, """
                    {"title":"x","variants":[{"id":1,"title":"10","public_title":"10","price":"10.00","available":true}]}
                    """);
            if (path == "/cart/add.js") return (409, cartBody);
            return (404, "{}");
        });

        return await StoreFlowRunner.RunCheckoutAsync(new ShopifyFlow(), Ctx(services, store.BaseUrl), default);
    }

    /// <summary>A 409 whose body says the reservation failed is the one case the artifact says to retry.</summary>
    [Fact]
    public async Task AFailedReservationIsWorthAnotherAttempt()
    {
        var outcome = await CheckoutWithCartBody(
            """{"description":"Out of stock (reservation failed), retrying"}""");

        Assert.False(outcome.Success);
        Assert.NotEqual(CheckoutResult.Declined, outcome.Result);
    }

    /// <summary>A decoy is bait; retrying it is how a session starts looking like a bot.</summary>
    [Fact]
    public async Task ADecoyIsNeverRetried()
    {
        var outcome = await CheckoutWithCartBody("""{"description":"Out of stock (decoy)"}""");

        Assert.False(outcome.Success);
        Assert.Equal(CheckoutResult.Declined, outcome.Result);
    }

    /// <summary>A plain 409 with an ordinary sold-out message stays a decline, which is the conservative reading.</summary>
    [Fact]
    public async Task AnUnmarkedShortageStaysADecline()
    {
        var outcome = await CheckoutWithCartBody("""{"description":"Item is Out of Stock"}""");

        Assert.False(outcome.Success);
        Assert.Equal(CheckoutResult.Declined, outcome.Result);
    }

    /// <summary>
    /// When both markers appear the refusal wins: a wrong retry costs an account, a wrongly abandoned attempt costs
    /// only that attempt.
    /// </summary>
    [Fact]
    public async Task TheRefusalWinsWhenBothMarkersAppear()
    {
        var outcome = await CheckoutWithCartBody(
            """{"description":"Out of stock (reservation failed) -- decoy"}""");

        Assert.False(outcome.Success);
        Assert.Equal(CheckoutResult.Declined, outcome.Result);
    }
}
