using System.Text.RegularExpressions;
using Cybersole.Http;
using Cybersole.Stores.Flows;
using Cybersole.Stores.Payments;
using Newtonsoft.Json.Linq;

namespace Cybersole.Stores.Payments;

/// <summary>
/// The shield step's Paynamics arm, which is the only shield the image names.
///
/// <para>
/// R916. Two hosts were recovered in R905 — <c>nodecde1.paynamics.net</c> for device profiling and
/// <c>shield.paynamics.net</c> for the OTP path — and until now nothing called the second. The image's method is
/// <c>RunShield</c>, ordinal eighteen, with locals <c>data</c>, <c>data2</c> and <c>shieldQuery</c>, sitting after
/// <c>OpenSecurePage</c> at fifteen and <c>Navigate</c> at seventeen.
/// </para>
///
/// <para>
/// <b>The shape this implements, and what it does not know.</b> A shield step after a secure page and around a
/// navigation, whose answer is processed, implies: profile the device, build a query carrying that profile, post it,
/// and record the answer for the caller. That order is inference from the ordinals and local names. What no literal
/// records is which fields the query carries — <c>shieldQuery</c> names a variable and not its contents — so the body
/// sent here carries the profile token and the amount, and the method reports an unreachable host rather than
/// inventing a success.
/// </para>
/// </summary>
public static class PaynamicsShield
{
    /// <summary>
    /// Runs the step against the session's Paynamics device token, leaving the answer in
    /// <c>paynamics.shieldResult</c> and the raw body in <c>paynamics.shieldBody</c>.
    ///
    /// <para>
    /// Takes the session rather than a whole <see cref="FlowContext"/> because the session is all it reads; a context
    /// would require a live NetClient in every test and would suggest this step uses the product, card or proxy that
    /// the context carries and it does not.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> RunAsync(FlowSession session, CancellationToken ct,
        Func<string, string, string, CancellationToken, Task<NetResponse?>> post)
    {
        var (host, otpPath) = PaynamicsGateway.RecoveredShieldSurface;

        // the device token is what R905 recovered the profiling host for; without it there is nothing to shield
        if (!session.Vars.TryGetValue("paynamics.deviceToken", out var token) || string.IsNullOrEmpty(token))
            return StepOutcome.Fail("RunShield has no paynamics.deviceToken; the profile step did not run", retryable: true);

        // shieldQuery, in the image's own local name: the token plus what is being paid
        var query = new JObject
        {
            ["deviceToken"] = token,
            ["amount"] = session.Vars.TryGetValue("amount", out var amount) ? amount : null,
            ["orderId"] = session.Vars.TryGetValue("orderId", out var order) ? order : null,
        };

        var res = await post(host + otpPath, query.ToString(Newtonsoft.Json.Formatting.None),
            "paynamics-shield-otp", ct).ConfigureAwait(false);

        if (res is null) return StepOutcome.Fail("paynamics shield host unreachable", retryable: true);
        if (!res.IsSuccess) return StepOutcome.Fail($"paynamics shield HTTP {res.StatusCode}", retryable: true);

        session.Vars["paynamics.shieldBody"] = res.Body;

        // the answer is processed rather than trusted: the image hands it to ProcessResult at ordinal fourteen, and
        // the one field whose meaning is legible is a token the later steps would carry
        var m = Regex.Match(res.Body, "\"(?:shieldToken|token)\"\\s*:\\s*\"([^\"]+)\"");
        session.Vars["paynamics.shieldResult"] = m.Success ? m.Groups[1].Value : res.Body;
        return StepOutcome.Success();
    }
}