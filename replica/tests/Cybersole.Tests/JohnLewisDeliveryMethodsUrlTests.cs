using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1132: the delivery-methods endpoint is derived at run time, not written as a literal.
///
/// <c>sub_140A3FB10</c> joins <c>…/bff/v4/orderforms/deliveries/</c> (0x14705db98) with the suffix
/// <c>/methods</c> (0x146ab5dd0) through <c>sub_141CF62D0</c> and hands the result to the GET call.
/// A census that looks for whole literals cannot see the joined value, so the constant here exists to
/// make the endpoint visible to the codebase.
/// </summary>
public sealed class JohnLewisDeliveryMethodsUrlTests
{
    [Fact]
    public void TheDerivedUrlIsTheBaseSlashPlusTheMethods()
    {
        Assert.Equal("https://checkout.johnlewis.com/bff/v4/orderforms/deliveries/methods",
            RetailApiFamilies.JohnLewisBff.DeliveryMethodsV4);
    }

    [Fact]
    public void TheBaseCarriesTheTrailingSlashThatMakesTheJoinCorrect()
    {
        // without the slash the join would produce ".../deliveriesmethods"
        Assert.EndsWith("/deliveries/", RetailApiFamilies.JohnLewisBff.DeliveriesSlashV4);
        Assert.StartsWith(RetailApiFamilies.JohnLewisBff.DeliveriesSlashV4,
            RetailApiFamilies.JohnLewisBff.DeliveryMethodsV4);
    }
}
