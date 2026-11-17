using System.Net;
using System.Reflection;
using System.Text;
using Cybersole.Http;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Parity tests for the recovered step-action vocabulary and the payment gateway set.
///
/// The action ids and the gateway hosts below are the exact strings the shipped binary
/// carries, so a green run means the replica executes the same named units of work.
/// </summary>
public class StepActionTests
{
    private static readonly StepActionRegistry Registry = StepActionRegistry.CreateDefault();

    /// <summary>Every action id recovered from the binary's string heap.</summary>
    private static readonly string[] RecoveredActionIds =
    {
        "Account-Login",
        "Account-LoginVerify2FA",
        "Account-SubmitRegistration",
        "Account-VerifyTwoFactorEmailCode",
        "Account-CheckLogin",
        "Adyen-Authorize3DS2",
        "Adyen-PaymentFromComponent",
        "Adyen-PaymentsDetails",
        "COShipping-Form",
        "CSRF-Generate",
        "Product-Variant",
        "Sites-asics",
    };

    [Fact]
    public void EveryRecoveredActionIsRegistered()
    {
        var missing = RecoveredActionIds.Where(id => Registry.Resolve(id) is null).ToList();
        Assert.True(missing.Count == 0, $"missing actions: {string.Join(", ", missing)}");
    }

    [Fact]
    public void ActionIdsAreUniqueAndCategorised()
    {
        Assert.Equal(Registry.All.Count, Registry.All.Select(a => a.Id).Distinct().Count());
        foreach (var a in Registry.All)
        {
            Assert.False(string.IsNullOrWhiteSpace(a.Category));
            Assert.NotEmpty(a.Steps);
        }
    }

    [Fact]
    public void EveryActionStepExistsOnTheFlowContract()
    {
        var contract = typeof(StoreFlow)
            .GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Where(m => m.Name.EndsWith("Async"))
            .Select(m => m.Name[..^5])
            .ToHashSet(StringComparer.Ordinal);

        var missing = new List<string>();
        foreach (var action in Registry.All)
        {
            foreach (var step in action.Steps)
            {
                if (!contract.Contains(step)) missing.Add($"{action.Id}->{step}");
            }
        }

        Assert.True(missing.Count == 0, $"steps not on StoreFlow: {string.Join(", ", missing)}");
    }

    [Fact]
    public void RunnerKnowsEveryActionStep()
    {
        foreach (var step in Registry.All.SelectMany(a => a.Steps).Distinct())
        {
            Assert.True(StepActionRunner.Knows(step), $"runner cannot invoke '{step}'");
        }
    }

    [Fact]
    public void RunnerRejectsUnknownStep()
    {
        var action = new StepAction
        {
            Id = "bogus",
            Category = "Test",
            Name = "Bogus",
            Steps = new[] { "NoSuchStep" },
        };

        Assert.False(StepActionRunner.Knows("NoSuchStep"));
        Assert.NotEmpty(action.Steps);
    }

    [Fact]
    public async Task RunnerExecutesAnActionAndRecordsEveryStep()
    {
        // R964: the page now carries a token. Before this, GetCsrf returned success without looking at the response, so a
        // body of "{}" was enough for this test to pass -- and that pass pinned the false success rather than the recording
        // it means to check. A page with no token is now a failure, which is the point of the change, so the fixture
        // supplies a real one and the test keeps checking what its name says: that every step runs and is recorded.
        using var server = new TinyServer(_ =>
            (200, "<form><input type=\"hidden\" name=\"csrf_token\" value=\"testtoken123456\"></form>"));
        using var http = new NetClient();
        var ctx = new FlowContext { Http = http, Url = server.BaseUrl + "/", TimeoutSeconds = 5 };
        var flow = new NoopFlow();

        var result = await StepActionRunner.RunAsync(flow, ctx, Registry.Resolve("CSRF-Generate")!, default);

        Assert.True(result.Ok, result.Error);
        Assert.Equal(3, result.Records.Count);
        Assert.All(result.Records, r => Assert.True(r.Ok));
        Assert.Equal(3, ctx.Steps.Count);
    }

    [Fact]
    public async Task RunnerStopsAtTheFailingStep()
    {
        using var http = new NetClient();
        var ctx = new FlowContext { Http = http, Url = "http://127.0.0.1:1/", TimeoutSeconds = 2 };
        var flow = new FailingFlow();

        var result = await StepActionRunner.RunAsync(flow, ctx, Registry.Resolve("Product-Variant")!, default);

        Assert.False(result.Ok);
        Assert.Equal("FindProduct", result.FailedStep);
        Assert.Single(result.Records);
    }

    private class NoopFlow : StoreFlow
    {
        public override string Id => "noop";
        public override string Name => "Noop";
        public override IReadOnlyList<string> Domains => new[] { "127.0.0.1" };
    }

    private sealed class FailingFlow : NoopFlow
    {
        public override Task<StepOutcome> FindProductAsync(FlowContext c, CancellationToken ct) =>
            Task.FromResult(StepOutcome.Fail("no product"));
    }

    /// <summary>Single-shot HTTP listener for flow tests.</summary>
    private sealed class TinyServer : IDisposable
    {
        private readonly HttpListener _listener = new();
        public string BaseUrl { get; }

        public TinyServer(Func<HttpListenerRequest, (int Status, string Body)> handler)
        {
            var port = FreePort();
            BaseUrl = $"http://127.0.0.1:{port}";
            _listener.Prefixes.Add(BaseUrl + "/");
            _listener.Start();
            _ = Task.Run(async () =>
            {
                while (_listener.IsListening)
                {
                    HttpListenerContext ctx;
                    try { ctx = await _listener.GetContextAsync().ConfigureAwait(false); }
                    catch { return; }

                    var (status, body) = handler(ctx.Request);
                    var bytes = Encoding.UTF8.GetBytes(body);
                    ctx.Response.StatusCode = status;
                    ctx.Response.ContentType = "application/json";
                    await ctx.Response.OutputStream.WriteAsync(bytes).ConfigureAwait(false);
                    ctx.Response.Close();
                }
            });
        }

        private static int FreePort()
        {
            var l = new System.Net.Sockets.TcpListener(IPAddress.Loopback, 0);
            l.Start();
            var port = ((IPEndPoint)l.LocalEndpoint).Port;
            l.Stop();
            return port;
        }

        public void Dispose()
        {
            try { _listener.Stop(); } catch { }
            _listener.Close();
        }
    }
}

/// <summary>Payment gateway coverage against the hosts recovered from the binary.</summary>
public class PaymentGatewayTests
{
    private static readonly PaymentGatewayRegistry Registry = PaymentGatewayRegistry.CreateDefault();

    [Fact]
    public void AllNineGatewaysAreRegistered()
    {
        foreach (var id in new[]
                 {
                     "adyen", "square", "stripe", "unzer", "commercehub",
                     "omise", "paynamics", "sibs", "paypal",
                 })
        {
            Assert.NotNull(Registry.Resolve(id));
        }
    }

    [Fact]
    public void GatewayIdsAreUnique()
    {
        Assert.Equal(Registry.All.Count, Registry.All.Select(g => g.Id).Distinct().Count());
    }

    [Fact]
    public void SquareCarriesTheRecoveredApplicationId()
    {
        Assert.Equal("sq0idp-IHOCkIE2YwtxidR3fPWIEg", SquareGateway.DefaultApplicationId);
    }

    [Fact]
    public void CommerceHubCarriesTheRecoveredHost()
    {
        Assert.Equal("https://commercehub-secure-data-capture.fiservapps.com",
            CommerceHubGateway.DefaultHost);
    }

    [Fact]
    public void AdyenShopperHostAndVersionArePinned()
    {
        Assert.Equal("v68", AdyenGateway.ApiVersion);
        var t = typeof(AdyenGateway);
        foreach (var name in new[]
                 {
                     "LookUpAsync", "GetJwt", "AuthenticateAsync",
                     "ResolveContingencyAsync", "Authorize3DS2Async",
                     "PaymentFromComponentAsync", "CompleteActionAsync",
                 })
        {
            Assert.NotNull(t.GetMethod(name, BindingFlags.Public | BindingFlags.Instance));
        }
    }

    [Fact]
    public void AdyenDecodesAThreeDsJwt()
    {
        // {"acsTransID":"abc","messageVersion":"2.1.0"} base64url
        var payload = "eyJhY3NUcmFuc0lEIjoiYWJjIiwibWVzc2FnZVZlcnNpb24iOiIyLjEuMCJ9";
        var header = "eyJhbGciOiJub25lIn0";
        var jwt = header + "." + payload + ".";

        var decoded = AdyenGateway.DecodeJwt(jwt);
        Assert.NotNull(decoded);
        Assert.Equal("abc", decoded!["acsTransID"]?.ToString());
        Assert.Equal("2.1.0", decoded["messageVersion"]?.ToString());
    }

    [Fact]
    public void AdyenRejectsANonJwt()
    {
        Assert.Null(AdyenGateway.DecodeJwt("not-a-jwt"));
        Assert.Null(AdyenGateway.DecodeJwt(""));
    }

    [Fact]
    public void EveryGatewayDeclaresATokenizeAndAuthorizePath()
    {
        var t = typeof(IPaymentGateway);
        foreach (var g in Registry.All)
        {
            Assert.NotNull(g.GetType().GetMethod("TokenizeAsync", new[] { typeof(FlowContext), typeof(CancellationToken) }));
            Assert.NotNull(g.GetType().GetMethod("AuthorizeAsync", new[] { typeof(FlowContext), typeof(CancellationToken) }));
            Assert.NotNull(g.GetType().GetMethod("CompleteActionAsync",
                new[] { typeof(FlowContext), typeof(string), typeof(CancellationToken) }));
            Assert.NotNull(t);
        }
    }

    [Fact]
    public void GatewaysRejectAMissingCard()
    {
        using var http = new NetClient();
        var ctx = new FlowContext { Http = http, Url = "https://example.com/", TimeoutSeconds = 2 };

        foreach (var id in new[] { "adyen", "square", "stripe", "unzer", "commercehub", "omise", "sibs" })
        {
            var result = Registry.Resolve(id)!.TokenizeAsync(ctx, default).GetAwaiter().GetResult();
            Assert.False(result.Ok);
            Assert.Contains("no card", result.Error);
        }
    }
}
