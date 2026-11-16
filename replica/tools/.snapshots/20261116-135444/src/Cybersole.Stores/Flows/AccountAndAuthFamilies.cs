using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Account and auth surfaces from the 5.18.32 image, dumped in R104 — three groups, thirty-seven
/// literals.
///
/// <para>
/// <b>Better Auth</b> (11): the shape is unmistakable — <c>sign-in/email</c>,
/// <c>callback/credentials</c>, <c>device/token</c>, <c>csrf</c>, <c>session</c>. That is the
/// better-auth library's route table, plus <c>signin/shopify</c> for a Shopify OAuth hop.
/// </para>
///
/// <para>
/// <b>Magento account</b> (11): the login family is Magento 2's — <c>/account/login</c>,
/// <c>/account/loginPost/</c>, and a <c>/account/login/referer/{base64}</c> variant that carries the
/// return URL base64-encoded. The image has two real base64 payloads in it
/// (<c>aHR0cHM6Ly93d3cucGFuaW5pLml0…</c> = <c>https://www.panini.it</c>), which is how the encoding
/// is known rather than guessed.
/// </para>
///
/// <para>
/// <b>On Running</b> (9): the Korean storefront is <b>Magento GraphQL</b> — the storefront router
/// parameter <c>?graphql_router=0xdjmg_aa6</c> and <c>/ko-kr/graphql</c> are the PWA Studio shape.
/// </para>
/// </summary>
public static class AccountAndAuthFamilies
{
    /// <summary>better-auth's route table as the image spells it.</summary>
    public static class BetterAuth
    {
        public const string Callback = "/api/auth/callback/";
        public const string CallbackCredentials = "/api/auth/callback/credentials";
        public const string Csrf = "/api/auth/csrf";
        public const string Device = "/api/auth/device";
        public const string DeviceToken = "/api/auth/device/token";
        public const string Login = "/api/auth/login";
        public const string LoginReturnTo = "/api/auth/login?returnTo=%2Faccount";
        public const string Session = "/api/auth/session";
        public const string SignInEmail = "/api/auth/sign-in/email";
        public const string SignInShopify = "/api/auth/signin/shopify";
        public const string Token = "/api/auth/token";

        /// <summary>Sign-in walk: csrf, credentials, then the session and its token.</summary>
        public static readonly IReadOnlyList<string> SignIn = new[]
        {
            Csrf, SignInEmail, CallbackCredentials, Session, Token,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            Callback, CallbackCredentials, Csrf, Device, DeviceToken, Login, LoginReturnTo, Session,
            SignInEmail, SignInShopify, Token,
        };
    }

    /// <summary>Magento 2's account and login routes.</summary>
    public static class MagentoAccount
    {
        public const string Login = "/account/login";
        public const string LoginSlash = "/account/login/";
        public const string LoginPost = "/account/loginPost/";
        public const string MultiPass = "/account/login/multipass/";
        public const string LoginNext = "/account/login?next=%2F";
        public const string LoginReturnUrl = "/account/login?returnUrl=";
        public const string LoginReferer = "/account/login/referer/";
        public const string LoginPostReferer = "/account/loginPost/referer/";

        /// <summary>
        /// The two base64 payloads the image actually contains. They decode to
        /// <c>https://www.panini.it/…</c> and <c>https://www.footlocker.ph/…</c> — the return URL of a
        /// login, base64-encoded into the path. This is what proves the encoding.
        /// </summary>
        public static readonly IReadOnlyList<string> RefererPayloads = new[]
        {
            "aHR0cHM6Ly93d3cucGFuaW5pLml0L3NocF9pdGFfaXQvY3VzdG9tZXIvYWNjb3VudC9pbmRleC8",
            "aHR0cHM6Ly93d3cuZm9vdGxvY2tlci5waC8%2C",
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            Login, LoginSlash, LoginPost, MultiPass, LoginNext, LoginReturnUrl, LoginReferer,
            LoginPostReferer,
        };
    }

    /// <summary>On Running's Korean storefront — Magento GraphQL.</summary>
    public static class OnRunning
    {
        public const string Host = "www.on.com";
        public const string GraphQlRouter = "www.on.com/?graphql_router=0xdjmg_aa6";
        public const string GraphQl = "www.on.com/ko-kr/graphql";
        public const string Login = "www.on.com/ko-kr/login";
        public const string CheckoutShipping = "www.on.com/ko-kr/checkout/shipping";
        public const string CheckoutPayment = "www.on.com/ko-kr/checkout/payment";
        public const string CheckoutPayments = "www.on.com/ko-kr/api/checkout/payment/payments/";
        public const string CheckoutRegistration = "www.on.com/ko-kr/checkout/registration";

        public static readonly IReadOnlyList<string> Checkout = new[]
        {
            CheckoutShipping, CheckoutPayment, CheckoutPayments, CheckoutRegistration,
        };

        public static readonly IReadOnlyList<string> All = new[]
        {
            GraphQlRouter, GraphQl, Login, CheckoutShipping, CheckoutPayment, CheckoutPayments,
            CheckoutRegistration,
        };
    }

    /// <summary>Every literal in the three groups.</summary>
    public static readonly IReadOnlyList<string> All = BetterAuth.All
        .Concat(MagentoAccount.All)
        .Concat(OnRunning.All)
        .ToList();

    /// <summary>True when the literal is one of them, exactly.</summary>
    public static bool IsKnown(string? path) =>
        !string.IsNullOrEmpty(path) && All.Contains(path, System.StringComparer.Ordinal);
}
