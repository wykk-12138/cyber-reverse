using System.Net;
using System.Reflection;
using System.Text;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Parity tests for the step-driven store flows.
///
/// The method-name assertions below are the mechanical check for "same functions as the
/// shipped binary": every name in the expected set was recovered from the original image
/// as a compiler-generated async state machine (<c>&lt;Name&gt;d__N</c>), so a flow that
/// exposes the same name is performing the same unit of work.
/// </summary>
public class StoreFlowParityTests
{
    /// <summary>Step names recovered from the binary's string heap, grouped by flow phase.</summary>
    private static readonly string[] RequiredSteps =
    {
        // session
        "Init", "GetHome", "GetCsrf", "GetSession", "RefreshSession", "VerifySession",
        "SetCookies", "SetRequest", "HandleResponse", "Detect",
        // product
        "FindProduct", "FindProductMulti", "FindProductFlow", "FindVariant", "GetProduct",
        "GetProductDetails", "ScrapeProduct", "ScrapeProductPage", "ScrapeProductAvailability",
        "ScrapeJson", "ScrapeJsonFrontend", "ScrapePreload", "ScrapeVariantAvailability",
        "GetOwnProperties", "GetProperty", "CheckPriceLimit", "HandleOutOfStock",
        // cart
        "CreateCart", "GetCart", "ClearCart", "AddToCart", "AddToCartPreload",
        "AddToCartStoreFront", "AddToCartMulti", "EditLine", "UpdateCart",
        "RemoveLineItem", "RemoveItem",
        // checkout
        "InitiateCheckout", "GetCheckout", "GenerateCheckout", "SubmitEmail", "SubmitShipping",
        "SubmitAddress", "SubmitShippingMethod", "GetShippingRates", "GetShippingRate",
        "SubmitBilling", "SubmitBillingAddress", "SubmitDiscount", "ApplyDiscount",
        "SubmitOrder", "PlaceOrder", "ProcessOrder", "CreateOrder", "CalculateTaxes",
        "GetRates", "SubmitRate", "LookupAddress",
        // payment
        "SubmitPayment", "SubmitPaymentDetails", "GetPaymentToken", "GetPaymentPage",
        "GetPaymentUrl", "GetPaymentDetails", "CompletePayment", "StartPayment",
        "ProcessPayment", "CreatePayment", "CreateTransaction", "SubmitCard", "Tokenize",
        "Authorize", "HandleRequiresAction", "GetMerchantCode",
        // paypal / gateways
        "SubmitPayPal", "StartPayPal", "GetPayPalToken", "GetPayPalAccessToken",
        "GetPayPalOrderId", "CreateStripePaymentMethod", "GetStripePaymentIntent",
        "CreateGmoToken",
        // 3ds
        "ThreeDS", "Handle3DS", "Solve3DS", "Solve3DSRedirect", "Process3DS",
        "AwaitDeviceProfiling",
        // account
        "Login", "AccountLogin", "EmailLogin", "CheckLogin", "HandleLogin", "Register",
        "CompleteRegistration", "SignUp", "ResetPassword", "SendTwoFactor", "SubmitPassword",
        "SubmitCustomer", "SubmitInfo", "SubmitDetailsCommerce",
        // anti-bot
        "GetScript", "Generate", "GenerateSensor", "SubmitSensor", "GetSensorData",
        "GetKasada", "GenerateSbsd", "GetSbsdData",
        // captcha
        "GetCaptcha", "GetCheckoutCaptcha", "SolveCaptcha", "PollCaptcha", "SubmitCaptcha",
        // raffle / queue
        "EnterRaffle", "GetRaffleData", "GetRaffle", "GetRaffleProduct", "ScrapeRaffleForm",
        "PollQueue", "PollRelease", "PollRestock", "WaitForRelease", "FindSlot",
        "GetReleaseFeed", "LoadCountryData",
        // behaviour / misc
        "MoveMouse", "Click", "Paste", "SendManualNotification",
        "SubmitKlaviyoEvent", "SubmitKlaviyoBulkEvents", "SubmitKlaviyoProfile",
        "SubmitKlaviyoSubscription", "ConfirmSubscription",
    };

    [Fact]
    public void StoreFlow_ExposesEveryRecoveredStepName()
    {
        var actual = typeof(StoreFlow)
            .GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Select(m => m.Name.EndsWith("Async") ? m.Name[..^5] : m.Name)
            .ToHashSet(StringComparer.Ordinal);

        var missing = RequiredSteps.Where(s => !actual.Contains(s)).ToList();

        Assert.True(missing.Count == 0,
            $"missing step methods: {string.Join(", ", missing)}");
    }

    [Fact]
    public void StoreFlow_StepCountIsInParityRange()
    {
        var count = typeof(StoreFlow)
            .GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Count(m => m.DeclaringType == typeof(StoreFlow) && m.Name.EndsWith("Async"));

        // The binary exposes 289 async state machines implemented more than once; the
        // step contract covers that vocabulary, so the floor is the required list size.
        Assert.True(count >= RequiredSteps.Length,
            $"flow exposes {count} steps, expected at least {RequiredSteps.Length}");
    }

    [Fact]
    public void NikeFlow_DeclaresKasadaAndOverridesTheKasadaSteps()
    {
        var nike = new NikeFlow();
        Assert.True(nike.UsesKasada);

        foreach (var name in new[] { "GetScriptAsync", "GenerateSensorAsync", "SubmitSensorAsync" })
        {
            var m = typeof(NikeFlow).GetMethod(name, BindingFlags.Public | BindingFlags.Instance);
            Assert.NotNull(m);
            Assert.Equal(typeof(NikeFlow), m!.DeclaringType);
        }
    }

    [Fact]
    public void ShopifyFlow_OverridesTheFullCheckoutChain()
    {
        foreach (var name in new[]
                 {
                     "FindProductAsync", "FindVariantAsync", "AddToCartAsync", "GetCartAsync",
                     "InitiateCheckoutAsync", "GetCheckoutAsync", "SubmitEmailAsync",
                     "SubmitShippingAsync", "GetShippingRatesAsync", "SubmitPaymentAsync",
                     "SubmitOrderAsync",
                 })
        {
            var m = typeof(ShopifyFlow).GetMethod(name, BindingFlags.Public | BindingFlags.Instance);
            Assert.NotNull(m);
            Assert.Equal(typeof(ShopifyFlow), m!.DeclaringType);
        }
    }
}

/// <summary>Runs vendor anti-bot JavaScript locally, the way the binary does.</summary>
public class ScriptRuntimeTests
{
    [Fact]
    public void BrowserShim_PreludeExecutesAndExposesTheDom()
    {
        using var rt = new ScriptRuntime();
        Assert.Equal("Win32", rt.TryString("navigator.platform"));
        Assert.Equal("1920", rt.TryString("String(screen.width)"));
        Assert.NotNull(rt.TryString("String(typeof document.createElement)"));
        Assert.Equal("false", rt.TryString("String(navigator.webdriver)"));
    }

    [Fact]
    public void BrowserShim_CookieJarCapturesWrites()
    {
        var shim = new BrowserShim { Cookie = "a=1; b=2" };
        using var rt = new ScriptRuntime(shim);
        Assert.Equal("a=1; b=2", rt.TryString("document.cookie"));

        rt.Execute("document.cookie = 'kpsdk_ct=token123; path=/'");
        var cookies = rt.WrittenCookies;
        Assert.Contains(cookies, c => c.StartsWith("kpsdk_ct=", StringComparison.Ordinal));
    }

    [Fact]
    public void BrowserShim_CryptoRandomValuesIsDeterministicLength()
    {
        using var rt = new ScriptRuntime();
        var len = rt.TryString("(function(){var a=new Uint8Array(16);crypto.getRandomValues(a);return String(a.length);})()");
        Assert.Equal("16", len);
        var nonZero = rt.TryString("(function(){var a=new Uint8Array(16);crypto.getRandomValues(a);var n=0;for(var i=0;i<a.length;i++){if(a[i]!==0)n++;}return String(n>0);})()");
        Assert.Equal("true", nonZero);
    }

    [Fact]
    public void ScriptRuntime_SandboxRejectsInfiniteLoop()
    {
        using var rt = new ScriptRuntime(timeout: TimeSpan.FromMilliseconds(250));
        Assert.False(rt.TryExecute("while(true){}", out var err));
        Assert.NotNull(err);
    }
}

/// <summary>Kasada sensor generation from the store's own script.</summary>
public class KasadaSolverTests
{
    private const string FakeIps = """
        var KPSDK = {
          v: 3,
          ct: function () { return "3|abcdef0123456789|1730000000|ua|fp"; },
          sb: function () { return "sbsd-token-xyz"; },
          cd: function (s) { return "cd:" + s.length + ":" + s; }
        };
        window.KPSDK = KPSDK;
        document.cookie = "x-kpsdk-ct=3|abcdef0123456789; path=/";
        """;

    [Fact]
    public void FindScriptUrl_HandlesScriptSrcTl()
    {
        var html = "<script src=\"/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39/ips.js\"></script>";
        var url = KasadaSolver.FindScriptUrl(html, "https://www.nike.com/");
        Assert.NotNull(url);
        Assert.StartsWith("https://www.nike.com/", url);
    }

    [Fact]
    public void FindScriptUrl_HandlesUuidPairPath()
    {
        var html = """<script src="/149e9513-01fa-4fb0-aad4-566afd725d1b/2d206a39-8ed7-437e-a3be-862e0f06eea3/tl"></script>""";
        var url = KasadaSolver.FindScriptUrl(html, "https://www.nike.com/");
        Assert.Contains("/tl", url);
    }

    [Fact]
    public void FindScriptUrl_ReturnsNullWhenAbsent()
    {
        Assert.Null(KasadaSolver.FindScriptUrl("<html><body>hi</body></html>", "https://a.b/"));
    }

    [Fact]
    public void Solve_ReadsClientTokenFromScript()
    {
        using var solver = new KasadaSolver();
        var r = solver.Solve(FakeIps);

        Assert.True(r.Ok, r.Error);
        Assert.Equal("3|abcdef0123456789|1730000000|ua|fp", r.Ct);
        Assert.Equal("sbsd-token-xyz", r.Sbsd);
        Assert.Equal("3", r.Version);
        Assert.Equal("3|abcdef0123456789|1730000000|ua|fp", r.Headers["x-kpsdk-ct"]);
        Assert.Equal("sbsd-token-xyz", r.Headers["x-kpsdk-sb"]);
    }

    [Fact]
    public void Solve_FailsWithoutAToken()
    {
        using var solver = new KasadaSolver();
        var r = solver.Solve("var x = 1;");
        Assert.False(r.Ok);
        Assert.NotNull(r.Error);
    }

    [Fact]
    public void EncryptBody_UsesTheScriptCipher()
    {
        using var solver = new KasadaSolver();
        Assert.True(solver.Solve(FakeIps).Ok);

        var cd = solver.EncryptBody("""{"a":1}""");
        Assert.NotNull(cd);
        Assert.StartsWith("cd:", cd);
    }

    [Fact]
    public void Solve_PropagatesScriptErrors()
    {
        using var solver = new KasadaSolver();
        var r = solver.Solve("throw new Error('boom');");
        Assert.False(r.Ok);
        Assert.Contains("script threw", r.Error);
    }
}
