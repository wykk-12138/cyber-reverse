namespace Cybersole.Stores.Flows;

/// <summary>
/// The account routes the image carries, including the one that stands where the replica assumed another.
///
/// <para>
/// <b>Observed</b> (R1257, full string dump): <c>/account/login</c>, <c>/account-passwordreset</c>,
/// <c>/account/authorize?redirect_uri=</c>, <c>/account/searchorder?orderNumber=</c>, the regex-shaped
/// <c>/account/login/multipass/[^\s"'&lt;&gt;\\]+</c>, the Demandware customer pages <c>/customer/account/</c>,
/// <c>/customer/account/index/</c> and <c>/customer/account/login</c>, the camel-cased pair
/// <c>/Account/User/Login</c> and <c>/Account/User/Register</c>, and the query fragment
/// <c>&amp;returnUrl=/account/login?returnUrl=</c>.
/// </para>
///
/// <para>
/// <b>Not observed</b>: <c>/account/recover</c> and <c>/account/verify</c>, the two the replica had used. The reset
/// route the image does carry is <c>/account-passwordreset</c> — a different shape, not a different word for the
/// same thing: one is a nested path under <c>account/</c> and the other is a hyphenated top-level segment. The
/// method names <c>ResetPassword</c> and <c>VerifyEmailLogin</c> exist in the image, so the behaviour is there; only
/// the route strings differ from what the replica assumed.
/// </para>
///
/// <para>
/// <b>Unknown</b>: which storefront uses which of these, and what <c>/account/verify</c> maps onto — the image has no
/// route with that word, so either the verification step posts somewhere else or it never leaves the client.
/// </para>
/// </summary>
public static class AccountRoutes
{
    public const string Login = "/account/login";

    /// <summary>The image's password-reset route: hyphenated, not nested.</summary>
    public const string PasswordReset = "/account-passwordreset";

    public const string Authorize = "/account/authorize?redirect_uri=";

    public const string SearchOrder = "/account/searchorder?orderNumber=";

    /// <summary>Multi-pass login, stored in the image as a regex rather than a literal path.</summary>
    public const string LoginMultipassPattern = "/account/login/multipass/[^\\s\"'<>\\\\]+";

    /// <summary>Demandware's customer pages, three of which the image carries.</summary>
    public const string CustomerAccount = "/customer/account/";

    public const string CustomerAccountIndex = "/customer/account/index/";

    public const string CustomerAccountLogin = "/customer/account/login";

    /// <summary>The camel-cased pair a different storefront family uses.</summary>
    public const string CamelUserLogin = "/Account/User/Login";

    public const string CamelUserRegister = "/Account/User/Register";

    /// <summary>The return-URL fragment the image carries inside a larger query.</summary>
    public const string ReturnUrlFragment = "&returnUrl=/account/login?returnUrl=";
}
