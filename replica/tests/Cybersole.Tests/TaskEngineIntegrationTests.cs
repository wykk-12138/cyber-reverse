using System.Net;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Services;
using Cybersole.Services.Captcha;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// End-to-end orchestration test: a real HTTP store (local HttpListener) + the real
/// TaskEngine + a module that follows the IStoreModule contract. Verifies that
/// monitor → availability → checkout → event → stats all connect.
/// </summary>
public class TaskEngineIntegrationTests
{
    private sealed class MockModule : IStoreModule
    {
        public string Id => "mockstore";
        public string Name => "Mock Store";
        public IReadOnlyList<string> Domains => new[] { "127.0.0.1" };
        public bool CanHandle(Uri url) => url.Host is "127.0.0.1" or "localhost";

        public CaptchaChallenge? CreateChallenge(string pageUrl, string? siteKey = null,
            string kind = "turnstile") => null;

        public async Task<MonitorResult> MonitorAsync(MonitorContext ctx, CancellationToken ct)
        {
            var res = await ctx.Http.GetAsync(ctx.Url, new RequestOptions
            {
                Timeout = TimeSpan.FromSeconds(10),
                Tag = "mock-monitor",
            }, ct).ConfigureAwait(false);

            var json = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
            return new MonitorResult
            {
                Status = json["available"]?.ToObject<bool>() == true
                    ? MonitorStatus.Available
                    : MonitorStatus.SoldOut,
                ProductName = json["name"]?.ToString(),
                Price = json["price"]?.ToString(),
                VariantId = json["variant"]?.ToString(),
            };
        }

        public async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext ctx, CancellationToken ct)
        {
            var res = await ctx.Http.PostJsonAsync(
                ctx.Url.Replace("/product", "/cart/add"),
                Newtonsoft.Json.JsonConvert.SerializeObject(new { id = ctx.VariantId, quantity = 1 }),
                new RequestOptions { Timeout = TimeSpan.FromSeconds(10), Tag = "mock-cart" },
                ct).ConfigureAwait(false);

            var json = Newtonsoft.Json.Linq.JObject.Parse(res.Body);
            var order = json["orderNumber"]?.ToString();
            return new CheckoutOutcome
            {
                Success = order is not null,
                OrderNumber = order,
                Result = order is not null ? CheckoutResult.Success : CheckoutResult.Declined,
                SubmittedFields = CheckoutFormBuilder.Build(ctx.ProfileData, ctx.Account, ctx.Size),
            };
        }
    }

    private static (HttpListener Listener, int Port) StartStoreServer(bool inStock = true)
    {
        for (var port = 18200; port < 18300; port++)
        {
            var listener = new HttpListener();
            listener.Prefixes.Add($"http://127.0.0.1:{port}/");
            try
            {
                listener.Start();
                _ = Task.Run(async () =>
                {
                    while (listener.IsListening)
                    {
                        HttpListenerContext ctx;
                        try { ctx = await listener.GetContextAsync(); }
                        catch { break; }

                        var path = ctx.Request.Url?.AbsolutePath ?? "/";
                        var body = path.Contains("cart")
                            ? "{\"orderNumber\":\"TEST-123\"}"
                            : $"{{\"available\":{(inStock ? "true" : "false")}," +
                              "\"name\":\"Test Shoe\",\"price\":\"199.99\",\"variant\":\"V1\"}";

                        var bytes = Encoding.UTF8.GetBytes(body);
                        ctx.Response.ContentType = "application/json";
                        ctx.Response.ContentLength64 = bytes.Length;
                        await ctx.Response.OutputStream.WriteAsync(bytes);
                        ctx.Response.Close();
                    }
                });
                return (listener, port);
            }
            catch
            {
                listener.Close();
            }
        }

        throw new InvalidOperationException("no free port for the mock store");
    }

    [Fact]
    public async Task Task_Flow_Monitor_Then_Checkout_Raises_Event()
    {
        var (listener, port) = StartStoreServer();
        try
        {
            var settings = new GlobalSettings { MonitorDelay = 10, RetryDelay = 10, Timeout = 10 };
            var bus = new EventBus();
            var http = new NetClient();
            var registry = new StoreRegistry();
            registry.Register(new MockModule());

            var config = new ConfigurationStore();
            var engine = new TaskEngine(http, bus, registry, settings, config,
                new CaptchaSolverService(http, bus), new ClockService(bus));

            var checkout = new TaskCompletionSource<CheckoutEvent>(TaskCreationOptions.RunContinuationsAsynchronously);
            bus.Checkout += (_, e) => checkout.TrySetResult(e);
            engine.CheckoutCompleted += (_, e) => checkout.TrySetResult(e);

            var trace = new List<string>();
            engine.StateChanged += (_, rt) =>
            {
                lock (trace) trace.Add($"{rt.State} err={rt.LastError} checkouts={rt.Checkouts}");
            };

            // the engine refuses to check out without a billing profile
            var profile = new Cybersole.Core.Models.Profile { Name = "Integration Profile" };
            config.BillingGroups.Add(new Cybersole.Core.Models.BillingGroup
            {
                Name = "Integration",
                Profiles = new List<Cybersole.Core.Models.Profile> { profile },
            });

            var task = new BotTask
            {
                Name = "integration",
                Store = "mockstore",
                ProfileId = profile.Id,
                Product = new Product
                {
                    Url = $"http://127.0.0.1:{port}/product",
                    Name = "Test Shoe",
                    Sizes = new List<string> { "10" },
                },
            };

            engine.Start(task);

            CheckoutEvent evt;
            try
            {
                evt = await checkout.Task.WaitAsync(TimeSpan.FromSeconds(15));
            }
            catch (TimeoutException)
            {
                string log;
                lock (trace) log = string.Join(" -> ", trace);
                Assert.Fail($"no checkout event. state trace: {log}");
                return;
            }

            Assert.True(evt.Success);
            Assert.Equal("TEST-123", evt.OrderNumber);
            Assert.Equal("mockstore", evt.Store);
            Assert.Equal("199.99", evt.Price);

            // The Tasks page reads TaskEngine.Runtime to show live state. If the engine never
            // populated it, every row would keep saying Idle no matter what the workers were
            // doing — which is exactly what round 103 observed in the running UI.
            var runtime = engine.Runtime.SingleOrDefault(r => r.Task.Id == task.Id);
            Assert.NotNull(runtime);
            Assert.NotEqual(Cybersole.Core.Models.TaskState.Idle, runtime.State);

            // Attempts counts idle polls that came back out of stock, NOT checkout attempts. The
            // mock answers in-stock on the first poll, so it must still be zero — asserting the
            // real semantic instead of the one the name suggests (round 103 got this wrong).
            Assert.Equal(0, runtime.Attempts);

            engine.Stop(task);
        }
        finally
        {
            listener.Stop();
            listener.Close();
        }
    }

    /// <summary>
    /// An out-of-stock store keeps the worker polling, and each of those polls is what
    /// <c>Attempts</c> counts. This is the other half of the semantic pinned above: the in-stock
    /// path leaves it at zero, the sold-out path drives it up.
    /// </summary>
    [Fact]
    public async Task SoldOutPollsAdvanceTheAttemptsCounter()
    {
        var (listener, port) = StartStoreServer(inStock: false);
        try
        {
            var http = new NetClient { Transport = TransportMode.SChannel };
            var bus = new EventBus();
            var settings = new GlobalSettings { MonitorDelay = 50, RetryDelay = 50, Timeout = 5 };

            var registry = new StoreRegistry();
            registry.Register(new MockModule());

            var config = new ConfigurationStore();
            var engine = new TaskEngine(http, bus, registry, settings, config,
                new CaptchaSolverService(http, bus), new ClockService(bus));

            var profile = new Cybersole.Core.Models.Profile { Name = "Poll Profile" };
            config.BillingGroups.Add(new Cybersole.Core.Models.BillingGroup
            {
                Name = "Polling",
                Profiles = new List<Cybersole.Core.Models.Profile> { profile },
            });

            var task = new BotTask
            {
                Name = "soldout",
                Store = "mockstore",
                ProfileId = profile.Id,
                MonitorDelay = 40,
                Product = new Product
                {
                    Url = $"http://127.0.0.1:{port}/product",
                    Name = "Test Shoe",
                    Sizes = new List<string> { "10" },
                },
            };

            engine.Start(task);

            // the engine backs off on MonitorDelay, so ~6 polls fit in a second
            await Task.Delay(900);

            var runtime = engine.Runtime.SingleOrDefault(r => r.Task.Id == task.Id);
            Assert.NotNull(runtime);
            Assert.True(runtime.Attempts >= 3,
                $"expected several sold-out polls, got {runtime.Attempts}");
            Assert.Equal(Cybersole.Core.Models.TaskState.Monitoring, runtime.State);

            engine.Stop(task);
        }
        finally
        {
            listener.Stop();
            listener.Close();
        }
    }

    /// <summary>
    /// Two tasks with the same product URL keep separate runtime slots.
    ///
    /// A clone is a deep copy with a new id (round 99), and StartAll iterates every task in the
    /// group. If the engine keyed on anything but the id — the name, the URL — the two would
    /// fight over one slot and the second would never run. Round 105 saw runtime=2 and both rows
    /// Monitoring in the live window; this pins it.
    /// </summary>
    [Fact]
    public async Task TwoClonesRunInSeparateRuntimeSlots()
    {
        var (listener, port) = StartStoreServer(inStock: false);
        try
        {
            var http = new NetClient { Transport = TransportMode.SChannel };
            var bus = new EventBus();
            var settings = new GlobalSettings { MonitorDelay = 60, RetryDelay = 60, Timeout = 5 };

            var registry = new StoreRegistry();
            registry.Register(new MockModule());

            var config = new ConfigurationStore();
            var engine = new TaskEngine(http, bus, registry, settings, config,
                new CaptchaSolverService(http, bus), new ClockService(bus));

            var profile = new Cybersole.Core.Models.Profile { Name = "Clone Profile" };
            config.BillingGroups.Add(new Cybersole.Core.Models.BillingGroup
            {
                Name = "Clones",
                Profiles = new List<Cybersole.Core.Models.Profile> { profile },
            });

            BotTask Make(string name) => new()
            {
                Name = name,
                Store = "mockstore",
                ProfileId = profile.Id,
                MonitorDelay = 60,
                Product = new Product
                {
                    Url = $"http://127.0.0.1:{port}/product",
                    Name = "Test Shoe",
                    Sizes = new List<string> { "10" },
                },
            };

            var first = Make("original");
            var second = Make("original copy");

            engine.StartAll(new[] { first, second });
            await Task.Delay(500);

            var runtime = engine.Runtime;
            Assert.Equal(2, runtime.Count);
            Assert.Equal(2, runtime.Count(r => r.State == Cybersole.Core.Models.TaskState.Monitoring));

            // different ids, same URL — that is the whole point
            Assert.NotEqual(first.Id, second.Id);
            Assert.Equal(first.Product.Url, second.Product.Url);

            engine.StopAll();
        }
        finally
        {
            listener.Stop();
            listener.Close();
        }
    }
}
