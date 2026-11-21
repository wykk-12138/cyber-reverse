using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R789: Warhammer's add-to-cart speaks the image's GraphQL, not an invented REST call.
///
/// <para>
/// The mutation text in <c>WarhammerFlow.AddToCartMutation</c> is transcribed from
/// <c>analysis/warhammer_graphql.txt</c>, which R788 recovered from the pool at 0x1470cc484. Transcribing a 536-character
/// string by hand is exactly the kind of work that silently accumulates a wrong character, and a wrong character inside
/// a string literal still compiles. These tests therefore check the invariants that matter rather than trusting the
/// transcription.
/// </para>
///
/// <para>
/// What is observed: the operation name, the ten variables, which two are non-null, and the single selected field.
/// What is inferred: that the endpoint accepts this shape as a JSON body with operationName, query and variables --
/// the standard GraphQL-over-HTTP envelope, which the image's own request builder is consistent with but does not
/// spell out.
/// </para>
/// </summary>
public class WarhammerGraphQlTests
{
    private readonly ITestOutputHelper _out;

    public WarhammerGraphQlTests(ITestOutputHelper output) => _out = output;

    private static string Mutation => WarhammerFlow.AddToCartMutation;

    [Fact]
    public void TheOperationNameMatchesTheRecoveredText()
    {
        _out.WriteLine(Mutation);
        Assert.StartsWith("mutation AddToCart(", Mutation);
    }

    [Fact]
    // The two non-null arguments. If either loses its bang the request would be accepted by the client and rejected by
    // the server, which is harder to diagnose than a failing test.
    public void SkuAndFasciaAreTheOnlyNonNullArguments()
    {
        var declared = Mutation[..Mutation.IndexOf(')')];
        Assert.Contains("$sku: String!", declared);
        Assert.Contains("$fascia: String!", declared);
        Assert.Equal(2, declared.Count(ch => ch == '!'));
    }

    [Fact]
    public void TheOptionalRecaptchaTokenIsDeclared()
    {
        // This says the site's add-to-cart expects a solved reCAPTCHA when one is required.
        Assert.Contains("$recaptchaToken: String", Mutation);
    }

    [Fact]
    // The mutation selects exactly one field, which is what later steps authenticate with.
    public void TheSelectionIsTheCartJwt()
    {
        Assert.Contains("ctCartJWT", Mutation);
        Assert.Contains("__typename", Mutation);
        Assert.DoesNotContain("products", Mutation);
    }

    [Fact]
    // GraphQL ignores whitespace, and the constant flattens the recovered text's indentation deliberately. What must
    // survive is the structure: one operation, one call, ten arguments passed through.
    public void EveryDeclaredVariableIsAlsoPassedThrough()
    {
        var declared = new[] {
            "sku", "fascia", "linkedOfferId", "offerId", "quantity",
            "statusPoint", "recaptchaToken", "storeId", "algoliaQueryId", "objectId",
        };
        foreach (var name in declared)
        {
            Assert.Contains("$" + name + ":", Mutation);
            Assert.Contains(name + ": $" + name, Mutation);
        }
    }

    /// <summary>
    /// R1326: the onboarding document shipped for months ending with "[4040 chars total]" — a truncation
    /// marker pasted out of a display, which left the document stopping mid-way. The image's copy is 4040
    /// characters; this pins the repaired text and the absence of the marker in every generated document, so
    /// the same paste cannot ship again.
    /// </summary>
    [Fact]
    public void TheOnboardDocumentIsWholeAndCarriesNoTruncationMarker()
    {
        var document = WarhammerQueries.ApproveOnboardPaymentMutation;

        Assert.Equal(4040, document.Length);
        Assert.DoesNotContain("chars total", document);
        Assert.EndsWith("__typename\n}\n", document);
        Assert.Contains("approveGuestSignUpPayment", document);

        foreach (var field in typeof(WarhammerQueries).GetFields(
                     System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
        {
            var value = field.GetValue(null) as string;
            if (value is null) continue;
            Assert.DoesNotContain("chars total", value);
        }
    }
}
