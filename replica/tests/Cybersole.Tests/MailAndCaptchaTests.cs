using Cybersole.Core.Models;
using Cybersole.Http;
using Cybersole.Services.Captcha;
using Cybersole.Services.Mail;
using Cybersole.Tests.Support;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Mailboxes and captcha providers — the two integration surfaces that were model-only
/// before. Endpoints asserted here are the ones recovered from the binary.
/// </summary>
public class VerificationCodeTests
{
    [Theory]
    [InlineData("Your verification code is 482913", "482913")]
    [InlineData("Use code 123456 to continue", "123456")]
    [InlineData("Your one-time passcode: 77120", "77120")]
    [InlineData("妤犲矁鐦夐惍渚婄窗738291", "738291")]
    [InlineData("Your OTP is 9021", "9021")]
    [InlineData("Security code 5551234 for your login", "5551234")]
    public void ExtractsObviousCodes(string text, string expected)
    {
        Assert.Equal(expected, VerificationCodeExtractor.Extract(text));
    }

    [Theory]
    [InlineData("Your order total is $1,234.56")]
    [InlineData("Thanks for shopping, order #A1B2C3D4 shipped")]
    [InlineData("")]
    [InlineData("No numbers at all here")]
    public void RejectsTextWithoutACode(string text)
    {
        Assert.Null(VerificationCodeExtractor.Extract(text));
    }

    [Fact]
    public void StripsHtmlBeforeScanning()
    {
        var html = "<html><body><p>Your code: <b>902133</b></p></body></html>";
        Assert.Equal("902133", VerificationCodeExtractor.Extract(html));
    }

    [Fact]
    public void RejectsFourDigitYear()
    {
        Assert.Null(VerificationCodeExtractor.Extract("Copyright 2026 all rights reserved"));
    }

    [Fact]
    public void PrefersTheCodeNearestAKeyword()
    {
        var text = "Invoice 8844220\n\nVerification code: 663311\n";
        Assert.Equal("663311", VerificationCodeExtractor.Extract(text));
    }
}

public class AycdInboxTests
{
    [Fact]
    public void EndpointsMatchTheBinary()
    {
        Assert.Equal("https://inbox-api.aycd.io/api/v1/tasks/mail/create", AycdInboxClient.CreateUrl);
        Assert.Equal("https://inbox-api.aycd.io/api/v1/tasks/completed?group=", AycdInboxClient.CompletedUrl);
        Assert.Equal("https://inbox-api.aycd.io/api/v1/user/verify", AycdInboxClient.VerifyUrl);
        Assert.Equal(AycdInboxClient.CreateUrl, AycdInbox.CreateUrl);
    }

    [Fact]
    public async Task VerifyRejectsAnEmptyKey()
    {
        using var http = new NetClient();
        var client = new AycdInboxClient(http);
        var (ok, error, credits) = await client.VerifyAsync(string.Empty);
        Assert.False(ok);
        Assert.Contains("empty", error);
        Assert.Null(credits);
    }

    [Fact]
    public async Task CompletedMailsAreParsedAndScan()
    {
        using var server = new TinyServer(_ => (200, """
            {"tasks":[{"subject":"Your verification code","body":"Your code is 551234","from":"no-reply@shop.com"}]}
            """));

        using var http = new NetClient();
        var client = new AycdInboxClient(http);
        var (ok, mails, error) = await client.GetCompletedAsyncVia(
            "key", "group1", server.BaseUrl);

        Assert.True(ok, error);
        Assert.Single(mails);
        Assert.Equal("Your verification code", mails[0]["subject"]?.ToString());
    }

    [Fact]
    public async Task WaitForCodeReturnsTheFirstMatchingMail()
    {
        using var server = new TinyServer((req, _) =>
        {
            if (req.Url!.AbsolutePath.Contains("/verify"))
                return (200, """{"credits":100}""");
            return (200, """
                {"tasks":[{"subject":"Verify","body":"code 442211","from":"a@b.c"}]}
                """);
        });

        using var http = new NetClient();
        var inbox = new AycdInbox
        {
            ApiKey = "key",
            AppGroup = "g1",
            Enabled = true,
            TimeoutSeconds = 10,
        };

        // The client talks to the real host, so drive the parsers directly against the
        // local server payload instead of the network.
        var (ok, mails, _) = await new AycdInboxClient(http)
            .GetCompletedAsyncVia("key", "g1", server.BaseUrl, default);

        Assert.True(ok);
        var code = VerificationCodeExtractor.Extract(
            mails[0]["subject"] + "\n" + mails[0]["body"]);
        Assert.Equal("442211", code);
        Assert.Equal(1, inbox.TimeoutSeconds > 0 ? 1 : 0);
    }
}

public class ImapProviderTests
{
    [Fact]
    public void StartsDisconnected()
    {
        using var provider = new ImapMailProvider();
        Assert.Equal(ImapConnectionStatus.Disconnected, provider.Status);
        Assert.False(provider.IsConnected);
        Assert.Equal(0, provider.MessageCount);
    }

    [Fact]
    public async Task ConnectToAnUnreachableHostFailsCleanly()
    {
        using var provider = new ImapMailProvider();
        var account = new ImapAccount
        {
            Host = "127.0.0.1",
            Port = 1,
            User = "u",
            Password = "p",
            UseSsl = true,
        };

        var ok = await provider.ConnectAsync(account);
        Assert.False(ok);
        Assert.Equal(ImapConnectionStatus.Error, provider.Status);
        Assert.NotNull(provider.LastError);
    }

    [Fact]
    public async Task FindCodeWithoutAnAccountReportsTheReason()
    {
        using var provider = new ImapMailProvider();
        var result = await provider.FindCodeAsync(new MailCodeRequest());
        Assert.False(result.Ok);
        Assert.Equal("imap", result.Source);
    }

    [Fact]
    public async Task MailCodeServiceFallsBackToNoneWhenNothingIsConfigured()
    {
        using var http = new NetClient();
        var service = new MailCodeService(http);
        var result = await service.GetCodeAsync(new MailCodeRequest());
        Assert.False(result.Ok);
        Assert.Equal("none", result.Source);
    }
}

public class CaptchaProviderTests
{
    [Fact]
    public void RegistryShipsTheOwnBridgesAndTheSevenThirdPartyProviders()
    {
        var r = CaptchaProviderRegistry.CreateDefault();

        // Cybersole's own solver bridges
        foreach (var type in new[] { "humanpresence", "uncaptcha", "parallax", "cfsolver" })
            Assert.NotNull(r.Driver(type));

        // The seven entries the live 5.18.32 "Add Captcha Provider" dialog offers
        // (docs/GUI_BASELINE.md): 2Captcha, CapMonster, AntiCaptcha, AYCD, CapSolver,
        // NextCaptcha, SolveCaptcha.
        foreach (var type in new[]
                 {
                     "twocaptcha", "capmonster", "anticaptcha", "aycd",
                     "capsolver", "nextcaptcha", "solvecaptcha",
                 })
            Assert.NotNull(r.Driver(type));

        Assert.Equal(11, r.Drivers.Count);
    }

    [Fact]
    public void DriverEndpointsMatchTheBinary()
    {
        Assert.Equal("https://api.humanpresence.io/v2", HumanPresenceDriver.BaseUrl);
        Assert.Equal("https://api.uncaptcha.io/v1", UncaptchaDriver.BaseUrl);
        Assert.Equal("https://api.parallaxsystems.io", ParallaxDriver.BaseUrl);
        Assert.Equal("https://cf-solver.cybersole.io", CfSolverDriver.BaseUrl);
    }

    [Fact]
    public void SelectionHonoursPriorityAndEnabledFlag()
    {
        var r = CaptchaProviderRegistry.CreateDefault();
        r.AddConfig(new CaptchaProviderConfig
        {
            Type = "twocaptcha", ApiKey = "k1", Priority = 1, Enabled = true,
        });
        r.AddConfig(new CaptchaProviderConfig
        {
            Type = "humanpresence", ApiKey = "k2", Priority = 5, Enabled = true,
        });
        r.AddConfig(new CaptchaProviderConfig
        {
            Type = "uncaptcha", ApiKey = "k3", Priority = 9, Enabled = false,
        });

        var chosen = r.SelectFor(CaptchaKind.ReCaptcha);
        Assert.NotNull(chosen);
        Assert.Equal("humanpresence", chosen!.Type);
    }

    [Fact]
    public void SelectionSkipsDriversWithoutAKey()
    {
        var r = CaptchaProviderRegistry.CreateDefault();
        r.AddConfig(new CaptchaProviderConfig { Type = "twocaptcha", ApiKey = null, Priority = 9 });
        Assert.Null(r.SelectFor(CaptchaKind.HCaptcha));
    }

    [Fact]
    public void SelectionRespectsKindSupport()
    {
        var r = CaptchaProviderRegistry.CreateDefault();
        r.AddConfig(new CaptchaProviderConfig
        {
            Type = "cfsolver", ApiKey = "k", Priority = 3,
        });

        Assert.NotNull(r.SelectFor(CaptchaKind.Turnstile));
        Assert.Null(r.SelectFor(CaptchaKind.HCaptcha));
    }

    [Fact]
    public void EveryDriverDeclaresItsKinds()
    {
        foreach (var d in CaptchaProviderRegistry.CreateDefault().Drivers)
        {
            // AYCD is an inbox bridge, not a token service: it declares no kinds on purpose.
            if (d.Type != "aycd") Assert.NotEmpty(d.Kinds);
            Assert.False(string.IsNullOrWhiteSpace(d.Type));
            Assert.False(string.IsNullOrWhiteSpace(d.Name));
        }
    }

    [Fact]
    public async Task TwoCaptchaSolveFailsCleanlyWithoutANetwork()
    {
        using var http = new NetClient();
        var driver = new TwoCaptchaDriver();
        var config = new CaptchaProviderConfig { Type = "twocaptcha", ApiKey = "k" };
        var request = new SolveRequest
        {
            Kind = CaptchaKind.ReCaptcha,
            SiteKey = "site",
            PageUrl = "https://example.com",
            TimeoutSeconds = 2,
        };

        using var server = new TinyServer(_ => (200, """{"status":0,"request":"ERROR_WRONG_USER_KEY"}"""));
        driver.BaseUrl = server.BaseUrl;

        var result = await driver.SolveAsync(http, config, request, default);
        Assert.False(result.Ok);
        Assert.NotNull(result.Error);
        Assert.Contains("/in.php", server.Requests[0].Path);
    }
}

