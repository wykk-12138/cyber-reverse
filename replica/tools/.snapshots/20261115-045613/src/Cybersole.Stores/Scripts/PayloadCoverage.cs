using System.Collections.Generic;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The engine-level members the image's payload reads, audited against what the replica already
/// installs — three columns, and the third one matters as much as the others (R156).
///
/// <para>
/// The payload sample of R152 lists, in order: userAgentData brands, the connection quartet, plugins with
/// per-plugin filename and description, two canvas hashes, a <c>canvas_spoofing</c> counter, a
/// <c>js-errors</c> array, then per-font probes. Of those, some the replica already answered, some it did not,
/// and some <b>cannot</b> be installed by anyone because the detector computes them itself.
/// </para>
///
/// <code>
/// member                                  replica before R156       now
/// navigator.userAgentData.brands          Emulation override        kept
/// navigator.userAgentData.mobile/platform Emulation override        kept
/// navigator.connection.{effectiveType…}   absent                    installed
/// navigator.plugins (5 entries)           3 entries                 five
/// navigator.automationEnabled             absent                    installed (false)
/// screen.darkMode.enabled                 absent                    installed (false)
/// canvas-print-*-hashes                   —                         read-only: the page draws, we do not answer
/// canvas_spoofing                         —                         the image's own counter, not a DOM member
/// js-errors                               —                         the image's own capture
/// font-* probes                           —                         read-only measurements
/// </code>
///
/// <para>
/// The distinction in the bottom four rows is the point: a canvas hash is not a property to override, it is
/// the result of running a canvas. Nothing in a stealth script can install it, and pretending otherwise is how
/// a replica ends up with a spoofing layer that lies about what it can do.
/// </para>
/// </summary>
public static class PayloadCoverage
{
    /// <summary>What the replica already answered before this round.</summary>
    public static readonly IReadOnlyList<string> AlreadyAnswered = new[]
    {
        "navigator.userAgentData.brands",
        "navigator.userAgentData.mobile",
        "navigator.userAgentData.platform",
        "navigator.userAgent",
        "navigator.platform",
        "navigator.language",
        "navigator.hardwareConcurrency",
        "navigator.deviceMemory",
        "webdriver_detect",
    };

    /// <summary>What this round installs.</summary>
    public static readonly IReadOnlyList<string> Installed = new[]
    {
        "navigator.connection.effectiveType",
        "navigator.connection.rtt",
        "navigator.connection.saveData",
        "navigator.connection.downlink",
        "navigator.plugins",
        "navigator.automationEnabled",
        "screen.darkMode.enabled",
    };

    /// <summary>
    /// What nobody can install: the detector computes these from the page.
    ///
    /// <para>
    /// <c>canvas_spoofing</c> and <c>js-errors</c> are the image's own bookkeeping, sitting in the same
    /// namespace as the readings they describe.
    /// </para>
    /// </summary>
    public static readonly IReadOnlyList<string> CannotBeInstalled = new[]
    {
        "canvas-print-100-999",
        "canvas-print-detailed-100-999",
        "canvas_spoofing",
        "js-errors",
        "font-*",
    };

    /// <summary>The connection values the sample carries, recorded so the install is not a guess.</summary>
    public static readonly IReadOnlyDictionary<string, object> ConnectionSample =
        new Dictionary<string, object>(System.StringComparer.Ordinal)
        {
            ["effectiveType"] = "4g",
            ["rtt"] = 50,
            ["saveData"] = false,
            ["downlink"] = 10,
        };

    /// <summary>The five plugin names the sample reports.</summary>
    public static IReadOnlyList<string> Plugins => SessionPayload.PluginNames;

    /// <summary>True when a member is one of the four that cannot be installed.</summary>
    public static bool IsReadOnly(string? member) =>
        !string.IsNullOrEmpty(member)
        && (member.Contains("canvas", System.StringComparison.OrdinalIgnoreCase)
            || member.StartsWith("font-", System.StringComparison.Ordinal)
            || member == "js-errors");

    /// <summary>The rule this audit exists to keep.</summary>
    public const string Rule =
        "a canvas hash is the result of running a canvas, not a property to override; a stealth layer that " +
        "claims it can install one is lying about its own reach";
}
