using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Services.Auth;
using Xunit;

namespace Cybersole.Tests;

public class SettingsTests
{
    [Fact]
    public void GlobalSettings_RoundTrips_Through_Json()
    {
        var settings = new GlobalSettings
        {
            Bearer = "token-abc",
            License = "6af28adf9813baada60406dd",
            MonitorDelay = 1500,
            RetryDelay = 2000,
            Timeout = 12,
            Currency = Currency.EUR,
            Language = "English",
            MonitorConcurrency = new ConcurrencySettings { Mode = ConcurrencyMode.Maximum, Maximum = 5, Ratio = 0.25 },
        };
        settings.NotificationOptions.Checkout.Sound = false;
        settings.Webhooks.Add(new Webhook { Url = "https://discord.com/api/webhooks/1/2" });

        var json = Json.Serialize(settings);
        var back = Json.Deserialize<GlobalSettings>(json);

        Assert.NotNull(back);
        Assert.Equal("token-abc", back!.Bearer);
        Assert.Equal("6af28adf9813baada60406dd", back.License);
        Assert.Equal(1500, back.MonitorDelay);
        Assert.Equal(Currency.EUR, back.Currency);
        Assert.Equal(5, back.MonitorConcurrency.Maximum);
        Assert.False(back.NotificationOptions.Checkout.Sound);
        Assert.Single(back.Webhooks);
        // camelCase on disk
        Assert.Contains("\"monitorDelay\"", json);
        Assert.Contains("\"bearer\"", json);
    }

    [Fact]
    public void TaskGroup_Matches_OnDisk_Shape()
    {
        var group = new TaskGroup { Name = "Group 1", CaptchaSource = CaptchaSource.Empty, Pinned = false };
        var json = Json.Serialize(group);

        Assert.Contains("\"name\": \"Group 1\"", json);
        Assert.Contains("\"captchaSource\"", json);
        Assert.Contains("\"linkedDelays\": false", json.Replace("\n", string.Empty).Replace("  ", " "));
    }
}

public class ProxyTests
{
    [Theory]
    [InlineData("1.2.3.4:8080", "1.2.3.4", 8080, null)]
    [InlineData("1.2.3.4:8080:user:pass", "1.2.3.4", 8080, "user")]
    [InlineData("http://1.2.3.4:3128", "1.2.3.4", 3128, null)]
    [InlineData("socks5://user:pass@1.2.3.4:1080", "1.2.3.4", 1080, "user")]
    public void Proxy_Parse_Handles_All_Formats(string input, string host, int port, string? user)
    {
        var proxy = Proxy.Parse(input);
        Assert.Equal(host, proxy.Host);
        Assert.Equal(port, proxy.Port);
        Assert.Equal(user, proxy.Username);
    }

    [Fact]
    public void Proxy_Uri_Includes_Credentials()
    {
        var proxy = Proxy.Parse("1.2.3.4:8080:u:p");
        Assert.Equal("http://u:p@1.2.3.4:8080", proxy.Uri);
    }
}

public class JwtTests
{
    [Fact]
    public void Decode_Reads_Cybersole_Claims()
    {
        // payload: {"AspNet.Identity.SecurityStamp":"X","...name":"a@b.c","role":"Bot","exp":1825816245,"iss":"https://cybersole.io/"}
        const string token =
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +
            "eyJBc3BOZXQuSWRlbnRpdHkuU2VjdXJpdHlTdGFtcCI6IlgiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiYUBiLmMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJCb3QiLCJleHAiOjE4MjU4MTYyNDUsImlzcyI6Imh0dHBzOi8vY3liZXJzb2xlLmlvLyJ9." +
            "sig";

        var claims = Jwt.Decode(token);

        Assert.NotNull(claims);
        Assert.Equal("a@b.c", claims!.Email);
        Assert.Equal("Bot", claims.Role);
        Assert.Equal("https://cybersole.io/", claims.Issuer);
        Assert.False(claims.IsExpired);
    }

    [Fact]
    public void Decode_Rejects_Garbage()
    {
        Assert.Null(Jwt.Decode("not-a-token"));
        Assert.Null(Jwt.Decode(null));
    }
}

public class TlsProfileTests
{
    [Fact]
    public void Profiles_Are_Complete()
    {
        Assert.Equal(3, TlsProfile.All.Count);
        foreach (var p in TlsProfile.All)
        {
            Assert.False(string.IsNullOrWhiteSpace(p.Ja3));
            Assert.Contains("h2", p.Alpn);
            Assert.Contains("Chrome", TlsProfile.Chrome.UserAgent);
        }
        Assert.Equal("firefox", TlsProfile.ByName("Firefox").Name);
        Assert.Equal("chrome", TlsProfile.ByName("nope").Name);
    }
}

public class StoreModuleTests
{
    [Fact]
    public void Catalog_Registers_All_Modules()
    {
        var registry = new Cybersole.Http.Stores.StoreRegistry();
        Cybersole.Stores.Modules.StoreModuleCatalog.RegisterAll(registry);

        // 66 since R1309 added Saucony — a store the image has and the catalogue did not list.
        Assert.Equal(66, registry.Modules.Count);
        Assert.Contains(registry.Modules, m => m.Id == "shopify");
        Assert.Contains(registry.Modules, m => m.Id == "nike");
        Assert.Contains(registry.Modules, m => m.Id == "demandware");
        Assert.Contains(registry.Modules, m => m.Id == "funko");
        Assert.Contains(registry.Modules, m => m.Id == "footsites");
        Assert.Contains(registry.Modules, m => m.Id == "supreme");
        Assert.Contains(registry.Modules, m => m.Id == "kith");
        Assert.Contains(registry.Modules, m => m.Id == "endclothing");
        Assert.Contains(registry.Modules, m => m.Id == "johnlewis");
        Assert.Contains(registry.Modules, m => m.Id == "100thieves");
        Assert.Contains(registry.Modules, m => m.Id == "10corsocomo");
        Assert.Contains(registry.Modules, m => m.Id == "titan22");
        Assert.Contains(registry.Modules, m => m.Id == "popmart");
        Assert.Contains(registry.Modules, m => m.Id == "yeezysupply");
        Assert.Contains(registry.Modules, m => m.Id == "offspring");
        Assert.Contains(registry.Modules, m => m.Id == "raffle");
        Assert.Contains(registry.Modules, m => m.Id == "casio");
        Assert.Contains(registry.Modules, m => m.Id == "warhammer");
        Assert.Contains(registry.Modules, m => m.Id == "jbhifi");
        Assert.Contains(registry.Modules, m => m.Id == "superswipe");
        Assert.Contains(registry.Modules, m => m.Id == "pocketgames");
        Assert.Contains(registry.Modules, m => m.Id == "sns");
        Assert.Contains(registry.Modules, m => m.Id == "size");
        Assert.Contains(registry.Modules, m => m.Id == "jdsports");
        Assert.Contains(registry.Modules, m => m.Id == "fanatics");
        Assert.Contains(registry.Modules, m => m.Id == "riotgames");
        Assert.Contains(registry.Modules, m => m.Id == "hypecommerce");
        Assert.Contains(registry.Modules, m => m.Id == "footpatrol");
        Assert.Contains(registry.Modules, m => m.Id == "notre");
        Assert.Contains(registry.Modules, m => m.Id == "bodega");
        Assert.Contains(registry.Modules, m => m.Id == "concepts");
        Assert.Contains(registry.Modules, m => m.Id == "packershoes");
        Assert.Contains(registry.Modules, m => m.Id == "socialstatus");
        Assert.Contains(registry.Modules, m => m.Id == "undefeated");
    }

    [Fact]
    public void Generic_Shopify_Claims_Only_Its_Own_Domains()
    {
        var module = new Cybersole.Stores.Modules.ShopifyModule();
        Assert.True(module.CanHandle(new Uri("https://brand.myshopify.com/products/tee")));

        // regression: this used to match any "/products/" path, which swallowed every brand alias
        Assert.False(module.CanHandle(new Uri("https://shop.example.com/products/tee")));
        Assert.False(module.CanHandle(new Uri("https://example.com/about")));
    }

    [Fact]
    public void Brand_Alias_Wins_Over_The_Generic_Shopify_Module()
    {
        var registry = new Cybersole.Http.Stores.StoreRegistry();
        Cybersole.Stores.Modules.StoreModuleCatalog.RegisterAll(registry);

        var resolved = registry.Resolve(new Uri("https://cncpts.com/products/tee"));
        Assert.NotNull(resolved);
        Assert.Equal("concepts", resolved!.Id);
    }

    [Fact]
    public void Nike_Resolves_Style_Color()
    {
        var module = new Cybersole.Stores.Modules.NikeModule();
        Assert.True(module.CanHandle(new Uri("https://www.nike.com/t/air-max-1/DD1873-100")));
    }
}





