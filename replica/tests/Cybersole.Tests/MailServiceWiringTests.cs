using System.Net;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Services;
using Cybersole.Services.Captcha;
using Cybersole.Services.Mail;
using Cybersole.Tests.Support;
using Cybersole.Ui.Views.Settings;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Wave 2A behavioral &amp; wiring tests covering <see cref="AycdInboxClient"/> wire contracts,
/// <see cref="ImapMailProvider"/> / <see cref="MailMessageMatcher"/> filtering &amp; extraction,
/// concurrent <see cref="MailCodeService"/> race orchestration, <see cref="AppServices"/> /
/// <see cref="TaskEngine"/> / <see cref="CheckoutContext.WaitForMailCodeAsync"/> wiring, and
/// <see cref="ImapView"/> live verification.
/// </summary>
public sealed class MailServiceWiringTests
{
    [Fact]
    public async Task AycdVerifyAndCreateUseTokenAuthAndCamelCaseWireJson()
    {
        string? seenAuth = null;
        string? createBody = null;
        using var server = new TinyServer((req, body) =>
        {
            seenAuth = req.Headers["Authorization"];
            var path = req.Url?.AbsolutePath ?? "";
            if (path == "/api/v1/user/verify")
                return (200, """{"credits":42}""");
            if (path == "/api/v1/tasks/mail/create")
            {
                createBody = body;
                return (200, """{"id":"task_99","status":"pending","results":{}}""");
            }
            if (path == "/api/v1/tasks/completed")
                return (200, """{"tasks":[{"id":"task_99","status":"completed","results":{"code":"492018"}}]}""");
            return (404, "{}");
        });

        using var http = new NetClient();
        var client = new AycdInboxClient(http);

        var (ok, err, credits) = await client.VerifyAsync("aycd_secret", server.BaseUrl);
        Assert.True(ok, err);
        Assert.Equal(42, credits);
        Assert.Equal("Token aycd_secret", seenAuth);

        var inbox = new AycdInbox { ApiKey = "aycd_secret", TemplateId = "tpl-1", TimeoutSeconds = 9999, Enabled = true };
        var mailReq = new MailCodeRequest
        {
            Aycd = inbox,
            Recipient = "buyer+01@example.com",
            SenderContains = "shopify.com",
            SubjectContains = "Verify",
            Elements = new[] { new MailElement { Name = "code", Target = MailFilterTarget.Body, Type = MailElementType.Numeric, Regex = @"\b\d{6}\b" } },
            PollInterval = TimeSpan.FromMilliseconds(20),
            Timeout = TimeSpan.FromSeconds(5),
            AycdBaseOriginOverride = server.BaseUrl,
        };

        var result = await client.WaitForCodeAsync(mailReq);
        Assert.True(result.Ok, result.Error);
        Assert.Equal("492018", result.Code);
        Assert.Equal("aycd", result.Source);
        Assert.NotNull(createBody);

        var sent = JObject.Parse(createBody!);
        Assert.Equal("tpl-1", sent["templateId"]?.ToString());
        Assert.Equal("buyer+01@example.com", sent["email"]?.ToString());
        Assert.Equal(3600, sent["timeout"]?.Value<int>()); // clamped [1, 3600]
        Assert.Equal(2, (sent["mailFilters"] as JArray)?.Count);
        Assert.Equal("code", sent["mailElements"]?[0]?["name"]?.ToString());
    }

    [Fact]
    public void MailMessageMatcherAppliesSinceFiltersRecipientFallbackAndElements()
    {
        var cutoff = new DateTimeOffset(2026, 11, 20, 12, 0, 0, TimeSpan.Zero);
        var msgs = new[]
        {
            new MailMessageSnapshot("Your code is 111111", new[] { "noreply@shopifyemail.com" },
                new[] { "a@shop.test" }, "Store+998877 code 111111", null, cutoff.AddMinutes(-5)),
            new MailMessageSnapshot("Verify 738291", new[] { "noreply@shopifyemail.com" },
                new[] { "a@shop.test" }, "Use code 738291 for Store+998877", "<a href=\"https://shop.test/confirm?k=9\">Go</a>", cutoff.AddMinutes(1)),
        };

        var req = new MailCodeRequest
        {
            Since = cutoff,
            Recipient = "a@shop.test",
            Filters = new[]
            {
                new MailFilter { Target = MailFilterTarget.From, Comparator = MailFilterComparator.Includes, OrValues = new[] { "shopifyemail", "shopify.com" } },
                new MailFilter { Target = MailFilterTarget.Subject, Comparator = MailFilterComparator.Matches, Value = @".*\d{6}.*" },
                new MailFilter { Target = MailFilterTarget.Body, Comparator = MailFilterComparator.Excludes, Value = "unsubscribe-me-now" },
            },
            Elements = new[]
            {
                new MailElement { Name = "code", Target = MailFilterTarget.Body, Type = MailElementType.Numeric, Formatter = "Use code ", Regex = @"(\d{6})" },
                new MailElement { Name = "shop", Target = MailFilterTarget.Body, Type = MailElementType.Numeric, Regex = @"Store\+(\d{6,})", Optional = true },
                new MailElement { Name = "confirm", Target = MailFilterTarget.Body, Type = MailElementType.Link, Selector = "a", Optional = true },
            },
        };

        var res = MailMessageMatcher.EvaluateMessages(msgs, req, "imap");
        Assert.NotNull(res);
        Assert.True(res!.Ok);
        Assert.Equal("738291", res.Code);
        Assert.Equal("998877", res.Values["shop"]);
        Assert.Equal("https://shop.test/confirm?k=9", res.Values["confirm"]);

        // Recipient unique fallback when strict filter misses
        var fallbackReq = new MailCodeRequest
        {
            Since = cutoff,
            Recipient = "a@shop.test",
            SubjectContains = "nonexistent-subject",
            AllowMultiple = false,
        };
        var fallbackRes = MailMessageMatcher.EvaluateMessages(msgs, fallbackReq, "imap");
        Assert.NotNull(fallbackRes);
        Assert.Equal("738291", fallbackRes!.Code);
    }

    [Fact]
    public void ImapProviderCtorGuardsNullAndFlagsOutlookHosts()
    {
        Assert.Throws<ArgumentNullException>(() => new ImapMailProvider(null!, "user"));
        Assert.Throws<ArgumentNullException>(() => new ImapMailProvider("imap.gmail.com", null!));
        Assert.True(ImapMailProvider.IsOutlookOAuthHost("outlook.office365.com"));
        Assert.True(ImapMailProvider.IsOutlookOAuthHost("imap-mail.outlook.com"));
        Assert.False(ImapMailProvider.IsOutlookOAuthHost("imap.gmail.com"));
    }

    [Fact]
    public async Task MailCodeServiceRacesProvidersConcurrentlyAndTaskEngineWiresCheckoutContext()
    {
        var tempRoot = Path.Combine(Path.GetTempPath(), "cyb-mail-test-" + Guid.NewGuid().ToString("N"));
        try
        {
            using var server = new TinyServer((req, _) =>
            {
                var path = req.Url?.AbsolutePath ?? "";
                if (path == "/api/v1/user/verify")
                    return (200, """{"credits":7}""");
                if (path == "/api/v1/tasks/mail/create")
                    return (200, """{"id":"grp_1","status":"pending","results":{}}""");
                if (path == "/api/v1/tasks/completed")
                    return (200, """{"tasks":[{"id":"grp_1","status":"completed","results":{"code":"654321"}}]}""");
                return (404, "{}");
            });

            using var services = AppServices.Create(
                (reg, _) => reg.Register(new CapturingOtpModule(server.BaseUrl)),
                tempRoot);

            services.Config.Accounts.Imap.Add(new ImapAccount
            {
                Host = "127.0.0.1",
                Port = 1, // unreachable fast failure -> must not block winning AYCD branch
                User = "u@test",
                Password = "p",
                UseSsl = false,
            });
            services.Config.Accounts.AycdInbox = new AycdInbox
            {
                ApiKey = "aycd_key",
                AppGroup = "grp_1",
                Enabled = true,
                TimeoutSeconds = 5,
            };
            services.Config.Save();

            // 1. Live concurrent race via MailCodeService
            var raceResult = await services.Mail.GetCodeAsync(new MailCodeRequest
            {
                ImapAccounts = services.Config.Accounts.Imap,
                Aycd = services.Config.Accounts.AycdInbox,
                PollInterval = TimeSpan.FromMilliseconds(20),
                Timeout = TimeSpan.FromSeconds(5),
                AycdBaseOriginOverride = server.BaseUrl,
            });
            Assert.True(raceResult.Ok, raceResult.Error);
            Assert.Equal("654321", raceResult.Code);
            Assert.Equal("aycd", raceResult.Source);

            // 2. Settings ImapView live AYCD verification against loopback server
            var imapView = new ImapView(services);
            var verifyMsg = await imapView.VerifyAycdAsync(server.BaseUrl);
            Assert.Contains("7 credits", verifyMsg);

            // 3. TaskEngine -> CheckoutContext.WaitForMailCodeAsync resolves OTP live via MailCodeService
            var profile = new Profile { Id = "p1", Name = "P1", Email = "buyer@example.com" };
            services.Config.BillingGroups.Add(new BillingGroup { Id = "bg1", Name = "BG", Profiles = new() { profile } });
            var task = new BotTask
            {
                Id = "t1",
                Name = "OtpTask",
                Store = "otp-probe",
                ProfileId = "p1",
                MonitorDelay = 5,
                RetryDelay = 5,
                Product = new Product { Url = "https://shop.test/item", Name = "Shoe" },
            };

            var done = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            services.Tasks.CheckoutCompleted += (_, e) => done.TrySetResult(e.Success);
            services.Tasks.Start(task);
            var ok = await done.Task.WaitAsync(TimeSpan.FromSeconds(10));
            Assert.True(ok);
            Assert.Equal("654321", CapturingOtpModule.ResolvedCode);
        }
        finally
        {
            if (Directory.Exists(tempRoot))
                Directory.Delete(tempRoot, recursive: true);
        }
    }

    private sealed class CapturingOtpModule : IStoreModule
    {
        private readonly string _aycdOrigin;
        public static string? ResolvedCode { get; private set; }
        public CapturingOtpModule(string aycdOrigin) => _aycdOrigin = aycdOrigin;
        public string Id => "otp-probe";
        public string Name => "OTP Probe";
        public IReadOnlyList<string> Domains => new[] { "shop.test" };
        public bool CanHandle(Uri url) => true;
        public CaptchaChallenge? CreateChallenge(string pageUrl, string? siteKey = null, string kind = "turnstile") => null;

        public Task<MonitorResult> MonitorAsync(MonitorContext context, CancellationToken ct) =>
            Task.FromResult(new MonitorResult { Status = MonitorStatus.Available, VariantId = "v1" });

        public async Task<CheckoutOutcome> CheckoutAsync(CheckoutContext context, CancellationToken ct)
        {
            if (context.WaitForMailCodeAsync is null)
                return new CheckoutOutcome { Success = false, Error = "missing WaitForMailCodeAsync" };
            var ans = await context.WaitForMailCodeAsync(new MailCodeInquiry
            {
                Recipient = context.ProfileData.Email,
                Timeout = TimeSpan.FromSeconds(5),
                BaseOriginOverride = _aycdOrigin,
            }, ct).ConfigureAwait(false);
            ResolvedCode = ans.Code;
            return new CheckoutOutcome { Success = ans.Ok && ans.Code == "654321", OrderNumber = ans.Code };
        }
    }
}
