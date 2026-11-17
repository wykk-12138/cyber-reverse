using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Flows;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The bridge between the DataDome sensor and a running flow: detect the wall, run the sensor, and put the
/// cookie where the next request will pick it up. R996, and the third of these — Cloudflare took R140, Kasada R141.
///
/// <para>
/// This is the same gap the other two had, and the wording from R140 still fits: <b>detection and storage both
/// existed; the call between them did not</b>. Here the call is a sensor submission, and the image names every
/// piece of it:
/// </para>
///
/// <code>
/// https://datadome.cybersole.io/sensor          the relay that answers with a cookie
/// https://api-sdk.datadome.co/sdk/              DataDome's own SDK, which the image also names
/// DataDomeKey  DataDomeChallenge  DatadomeSliderTask
/// Getting DataDome  Initialising DataDome  Solving DataDome  Submitting DataDome    the four stages
/// </code>
///
/// <para>
/// The four stage lines are why this helper reports a stage rather than a bare boolean: the image narrates what it
/// is doing, so a run that stalls says where. The cookie is <c>datadome</c>, which is what
/// <see cref="AntiBotProtocol.CookiesFor"/> already recorded.
/// </para>
///
/// <para>
/// What this does <b>not</b> claim: the relay wants credentials this workspace does not have, exactly as
/// <c>cf-solver.cybersole.io</c> did. So the sensor is injected, and an unconfigured one returns the refusal
/// sentence as a status rather than as an error — the flow continues and the next request retries without a
/// cookie, which is the behaviour the Cloudflare helper settled on for the same reason.
/// </para>
/// </summary>
public static class DataDomeClearance
{
    /// <summary>The cookie the protocol table records for DataDome.</summary>
    public const string ClearanceCookie = "datadome";

    /// <summary>The relay the image names for sensor submission.</summary>
    public const string SensorUrl = "https://" + AntiBotVendors.DataDomeSensor;

    /// <summary>DataDome's own SDK host, named separately in the image.</summary>
    public const string SdkUrl = "https://" + AntiBotVendors.DataDomeSdk;

    /// <summary>The session keys this helper reads and writes.</summary>
    public const string VendorVar = "antibot";
    public const string StageVar = "datadome.stage";
    public const string SolverStatusVar = "datadome.solverStatus";
    public const string ClearanceVar = "datadome.clearance";

    /// <summary>The four stages the image narrates, in its order.</summary>
    public static readonly IReadOnlyList<string> Stages = new[]
    {
        "Getting DataDome", "Initialising DataDome", "Solving DataDome", "Submitting DataDome",
    };

    /// <summary>True when the detected vendor is DataDome.</summary>
    public static bool IsDataDome(FlowSession session) =>
        session.Vars.TryGetValue(VendorVar, out var vendor)
        && string.Equals(vendor, "datadome", StringComparison.OrdinalIgnoreCase);

    /// <summary>
    /// Run the sensor when the wall is DataDome's, then store the cookie both as a session var and in the jar.
    ///
    /// <para>
    /// A wall that is not DataDome's is not this helper's business: it returns success and stores nothing, so a
    /// Cloudflare or Kasada store is untouched. That guard is why the three helpers can sit side by side in one
    /// dispatcher without any of them claiming another's work.
    /// </para>
    /// </summary>
    public static async Task<StepOutcome> ApplyAsync(FlowContext c, IDataDomeSensor sensor,
        string pageUrl, CancellationToken ct = default)
    {
        if (!IsDataDome(c.Session)) return StepOutcome.Success();

        foreach (var stage in Stages)
        {
            c.Session.Vars[StageVar] = stage;
            c.Emit($"DataDome (I): {stage}", "antibot");
        }

        var (token, status) = await sensor.SolveAsync(SensorUrl, pageUrl, ct).ConfigureAwait(false);

        c.Session.Vars[SolverStatusVar] = status;

        if (string.IsNullOrEmpty(token))
        {
            c.Emit($"{status}", "antibot");
            return StepOutcome.Success();
        }

        c.Session.Vars[ClearanceVar] = token;
        c.Session.Cookies[ClearanceCookie] = token;
        c.Emit($"DataDome clearance acquired ({status})", "antibot");

        return StepOutcome.Success();
    }

    /// <summary>The clearance this session holds, or null.</summary>
    public static string? Clearance(FlowSession session) =>
        session.Vars.TryGetValue(ClearanceVar, out var value) && value.Length > 0 ? value : null;

    /// <summary>The last stage the session reached, or null.</summary>
    public static string? Stage(FlowSession session) =>
        session.Vars.TryGetValue(StageVar, out var value) ? value : null;

    /// <summary>The sensor's status as the session recorded it, or null.</summary>
    public static string? SolverStatus(FlowSession session) =>
        session.Vars.TryGetValue(SolverStatusVar, out var value) ? value : null;

    /// <summary>Every key this helper writes.</summary>
    public static readonly IReadOnlyList<string> Keys = new[]
    {
        StageVar, SolverStatusVar, ClearanceVar,
    };
}

/// <summary>
/// One road: submit the page to the relay and take back a cookie. There is no service-then-in-bot ladder here
/// because the image names one relay and one SDK, not two roads — inventing a second would be a strategy the
/// image does not have.
/// </summary>
public interface IDataDomeSensor
{
    /// <summary>Returns the cookie and a status describing what happened; a null cookie is a refusal, not a fault.</summary>
    Task<(string? Token, string Status)> SolveAsync(string sensorUrl, string pageUrl, CancellationToken ct);
}

/// <summary>
/// The injected sensor. With no call configured it reports that plainly, which is the same honesty
/// <c>ServiceCloudflareSolver</c> settled on: an unconfigured road is a fact about this workspace.
/// </summary>
public sealed class InjectedDataDomeSensor : IDataDomeSensor
{
    private readonly Func<string, string, CancellationToken, Task<string?>>? _call;

    public InjectedDataDomeSensor(Func<string, string, CancellationToken, Task<string?>>? call = null) => _call = call;

    public async Task<(string? Token, string Status)> SolveAsync(string sensorUrl, string pageUrl,
        CancellationToken ct)
    {
        if (_call is null)
            return (null, "DataDome relay not configured: the image names datadome.cybersole.io/sensor but this "
                + "workspace has no credentials for it");

        var token = await _call(sensorUrl, pageUrl, ct).ConfigureAwait(false);
        return string.IsNullOrEmpty(token)
            ? (null, "DataDome relay answered without a cookie")
            : (token, "solved");
    }

    /// <summary>The default: a sensor with no call configured.</summary>
    public static InjectedDataDomeSensor Default(
        Func<string, string, CancellationToken, Task<string?>>? call = null) => new(call);
}
