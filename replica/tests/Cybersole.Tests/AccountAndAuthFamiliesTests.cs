using System.Text;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 104: three account/auth surfaces, and the one thing in this session that is <b>decoded</b>
/// rather than merely recorded.
///
/// <para>
/// Magento's login family has a <c>/account/login/referer/{base64}</c> variant. The image contains
/// two real payloads; decoding them yields <c>https://www.panini.it/…</c> and
/// <c>https://www.footlocker.ph/…</c>. That is how the encoding is <b>known</b> instead of assumed —
/// and it is checkable offline, so it belongs in a test.
/// </para>
///
/// <para>
/// Better Auth's route table and On Running's Magento GraphQL router are recorded as vocabulary.
/// </para>
/// </summary>
public sealed class AccountAndAuthFamiliesTests
{
    private readonly ITestOutputHelper _out;

    public AccountAndAuthFamiliesTests(ITestOutputHelper output) => _out = output;

    /// <summary>Eleven, eight and seven — twenty-six literals, all distinct.</summary>
    [Fact]
    public void TheThreeGroupsHaveTheirImagesCounts()
    {
        Assert.Equal(11, AccountAndAuthFamilies.BetterAuth.All.Count);
        Assert.Equal(8, AccountAndAuthFamilies.MagentoAccount.All.Count);
        Assert.Equal(7, AccountAndAuthFamilies.OnRunning.All.Count);

        Assert.Equal(26, AccountAndAuthFamilies.All.Count);
        Assert.Equal(26, AccountAndAuthFamilies.All.Distinct().Count());
    }

    /// <summary>
    /// The referer payloads decode to the hosts the image names elsewhere. This is the strongest
    /// form of evidence in the session: not "this string exists" but "this string means X".
    /// </summary>
    [Fact]
    public void TheRefererPayloadsDecodeToRealHosts()
    {
        var decoded = new List<string>();

        foreach (var payload in AccountAndAuthFamilies.MagentoAccount.RefererPayloads)
        {
            var cleaned = payload.Replace("%2C", string.Empty, StringComparison.Ordinal);
            // restore padding for the URL-safe form
            var padded = cleaned.PadRight(cleaned.Length + (4 - cleaned.Length % 4) % 4, '=');
            var bytes = Convert.FromBase64String(padded);
            var text = Encoding.UTF8.GetString(bytes);
            decoded.Add(text);
            _out.WriteLine($"{payload[..20]}… → {text}");
        }

        Assert.Contains("https://www.panini.it", decoded[0]);
        Assert.Contains("https://www.footlocker.ph", decoded[1]);
    }

    /// <summary>better-auth's sign-in walk, and the Shopify OAuth hop beside it.</summary>
    [Fact]
    public void TheBetterAuthSignInWalkIsRecorded()
    {
        Assert.Equal("/api/auth/sign-in/email", AccountAndAuthFamilies.BetterAuth.SignInEmail);
        Assert.Equal("/api/auth/callback/credentials",
            AccountAndAuthFamilies.BetterAuth.CallbackCredentials);
        Assert.Equal("/api/auth/session", AccountAndAuthFamilies.BetterAuth.Session);
        Assert.Equal("/api/auth/signin/shopify", AccountAndAuthFamilies.BetterAuth.SignInShopify);

        _out.WriteLine(string.Join(" → ", AccountAndAuthFamilies.BetterAuth.SignIn));
        Assert.Equal(5, AccountAndAuthFamilies.BetterAuth.SignIn.Count);
    }

    /// <summary>On Running is Magento GraphQL — the router parameter is the giveaway.</summary>
    [Fact]
    public void OnRunningUsesTheMagentoGraphQlRouter()
    {
        Assert.Contains("graphql_router=0xdjmg_aa6", AccountAndAuthFamilies.OnRunning.GraphQlRouter);
        Assert.Equal("www.on.com/ko-kr/graphql", AccountAndAuthFamilies.OnRunning.GraphQl);

        _out.WriteLine(string.Join(" → ", AccountAndAuthFamilies.OnRunning.Checkout));
        Assert.Equal(4, AccountAndAuthFamilies.OnRunning.Checkout.Count);
        Assert.Contains(AccountAndAuthFamilies.OnRunning.CheckoutPayments,
            AccountAndAuthFamilies.OnRunning.Checkout);
    }

    /// <summary>Exact match, and the trailing-slash variants are their own literals.</summary>
    [Fact]
    public void KnownIsExactAndSlashVariantsAreDistinct()
    {
        Assert.True(AccountAndAuthFamilies.IsKnown("/api/auth/csrf"));
        Assert.False(AccountAndAuthFamilies.IsKnown("/api/auth/nope"));
        Assert.False(AccountAndAuthFamilies.IsKnown(null));

        Assert.NotEqual(AccountAndAuthFamilies.MagentoAccount.Login,
            AccountAndAuthFamilies.MagentoAccount.LoginSlash);
        Assert.True(AccountAndAuthFamilies.IsKnown(AccountAndAuthFamilies.MagentoAccount.LoginSlash));
    }
}
