using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1379: the browser-side PayPal path. The header names, the app name and the body's three variables are the image's;
/// the two session values are the caller's.
/// </summary>
public sealed class PayPalBrowserSurfaceTests
{
    [Fact]
    public void TheSurfaceConstantsAreTheObservedOnes()
    {
        Assert.Equal("https://www.paypal.com", PayPalBrowserSurface.Origin);
        Assert.Equal("checkoutuinodeweb_hermione", PayPalBrowserSurface.AppName);
        Assert.Equal("PayWithQuery", PayPalBrowserSurface.OperationName);
        Assert.Equal("expeirences", PayPalBrowserSurface.ExperiencesFieldName);
        Assert.Equal("IFRAME", PayPalBrowserSurface.FundingMethodIframe);
        Assert.Equal("en-GB", PayPalBrowserSurface.AcceptLanguage);
        Assert.Equal(16, PayPalBrowserSurface.HeaderNames.Length);
    }

    [Fact]
    public void TheHeadersCarryTheAppNameAndTheSessionsValues()
    {
        var headers = PayPalBrowserSurface.Headers("euat-1", "meta-1", null, null, null, null, null, null, null);

        Assert.Equal("checkoutuinodeweb_hermione", headers["x-app-name"]!.ToObject<string>());
        Assert.Equal("euat-1", headers["x-paypal-internal-euat"]!.ToObject<string>());
        Assert.Equal("meta-1", headers["paypal-client-metadata-id"]!.ToObject<string>());
        Assert.Equal("https://www.paypal.com", headers["origin"]!.ToObject<string>());
        Assert.Equal("same-origin", headers["sec-fetch-site"]!.ToObject<string>());
        Assert.Null(headers["cookie"]);
    }

    /// <summary>Without the session values the path cannot be used, and it says which one is missing.</summary>
    [Fact]
    public void TheSessionValuesAreRequired()
    {
        Assert.False(PayPalBrowserSurface.CanSend(null, "meta").Usable);
        Assert.False(PayPalBrowserSurface.CanSend("euat", null).Usable);
        Assert.True(PayPalBrowserSurface.CanSend("euat", "meta").Usable);
    }

    [Fact]
    public void TheBodyKeepsTheImagesSpelling()
    {
        var body = PayPalBrowserSurface.Body("query PayWithQuery { }", "tok", true);

        Assert.Equal("PayWithQuery", body["operationName"]!.ToObject<string>());
        Assert.True(body["variables"]!["withSplitTender"]!.ToObject<bool>());
        Assert.NotNull(body["variables"]!["expeirences"]);
        Assert.Null(body["variables"]!["experiences"]);
    }
}
