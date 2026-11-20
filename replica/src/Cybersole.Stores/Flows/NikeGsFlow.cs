using System.Text.RegularExpressions;

namespace Cybersole.Stores.Flows;

/// <summary>
/// Nike GS — the running build lists this as its own <c>Type</c> next to "Nike", so it gets its
/// own module id rather than being folded into the main Nike flow.
///
/// GS ("grade school") is the youth sizing line: same storefront, same Kasada gate, but the
/// size vocabulary is numeric kids' sizes (3.5Y–7Y) rather than men's. Everything else is
/// inherited.
/// </summary>
public sealed class NikeGsFlow : NikeFlow
{
    public override string Id => "nike-gs";
    public override string Name => "Nike GS";

    /// <summary>
    /// GS shares the main Nike storefront, so it cannot claim nike.com (the main flow already
    /// does, and duplicate claims make domain routing ambiguous). Nike's kids line has its own
    /// subdomain, which is both real and unique — picking GS by id is still the normal way in.
    /// </summary>
    public override IReadOnlyList<string> Domains => new[] { "kids.nike.com" };

    /// <summary>True when a size looks like a grade-school size rather than an adult one.</summary>
    public static bool IsGradeSchoolSize(string size)
    {
        var m = Regex.Match(size.Trim(), @"^(\d+(?:\.\d+)?)\s*[Yy]?$");
        if (!m.Success) return false;

        if (!double.TryParse(m.Groups[1].Value,
                System.Globalization.NumberStyles.Any,
                System.Globalization.CultureInfo.InvariantCulture, out var value))
            return false;

        // kids' sizes top out around 7; anything above that is adult
        return value is > 0 and <= 7;
    }

    public override Task<StepOutcome> FindVariantAsync(FlowContext c, CancellationToken ct)
    {
        var outcome = base.FindVariantAsync(c, ct);
        c.Session.Vars["sizeLine"] = "gs";
        return outcome;
    }

    public override async Task<StepOutcome> Process3DSAsync(FlowContext c, CancellationToken ct)
    {
        var url = c.Session.Vars.GetValueOrDefault("nike.threeDSecureRedirectUrl")
                  ?? c.Session.ThreeDsUrl
                  ?? c.Session.Vars.GetValueOrDefault("threeDsUrl");
        if (!string.IsNullOrEmpty(url) &&
            (url!.Contains("authentication-devices.checkout.com", StringComparison.OrdinalIgnoreCase) ||
             string.Equals(c.Session.Vars.GetValueOrDefault("checkoutcom.mode"), "esw", StringComparison.OrdinalIgnoreCase) ||
             string.Equals(c.Session.Vars.GetValueOrDefault("checkoutcom.mode"), "nike-gs", StringComparison.OrdinalIgnoreCase)))
        {
            var payload = c.Session.Vars.GetValueOrDefault("threeDsPayload") ?? string.Empty;
            var resolved = await new Cybersole.Stores.Payments.CheckoutComGateway()
                .ResolveEswThreeDsAsync(c, url!, payload, ct).ConfigureAwait(false);
            return resolved.Ok
                ? StepOutcome.Success()
                : StepOutcome.Fail(resolved.Error ?? "nike-gs: checkout.com 3DS failed", retryable: true);
        }

        return await base.Process3DSAsync(c, ct).ConfigureAwait(false);
    }
}
