using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// How the image actually gets a Kasada token: not one way, but four, with an interface behind them —
/// read in R136 and correcting an assumption this session had been working under.
///
/// <para>
/// The replica has a local browser solver and nothing else. The image's own status strings show a
/// wider machine:
/// </para>
///
/// <code>
/// IKasadaSolver                       — an interface, so the solver is pluggable
/// Getting Kasada (                    — the API path, numbering its attempts
/// Getting Kasada (1) / (2)            — first and second attempt
/// Getting Kasada (MFC)                — a mobile-fallback attempt
/// Failed getting Kasada               — the API path failed
/// Failed getting Kasada (Rotating)    — it failed and the proxy is being rotated
/// Failed solving Kasada               — the local path failed
/// Failed solving Kasada (TL)          — the local path failed on a TL step
/// Failed Kasada (Retry limit reached) — the whole strategy gave up
/// Kasada API down (Contact staff)     — the API is unreachable, which is an operator problem
/// Kasada-Fallback / Kasada-Mobile-Fallback   — the two fallback modes, named
/// </code>
///
/// <para>
/// Two consequences the replica was missing. First, <b>"getting" and "solving" are different verbs</b>:
/// getting means asking a service, solving means running the page. Second, a token can come from a
/// fallback, and the fallbacks have names, which means the caller can tell which one it got.
/// </para>
///
/// <para>
/// The provider names in the same pool — <c>Nike-Kasada-Version</c>, <c>Footsites-Kasada-Version</c>,
/// <c>Scheels-Kasada-Version</c>, <c>Converse-Kasada-Version</c>, <c>Crocs-Kasada-Version</c> and the
/// EU/JP variants — say the version header is per store, not global, which is why the header surface
/// is a table rather than a constant.
/// </para>
/// </summary>
public static class KasadaStrategy
{
    /// <summary>The four ways a token can arrive.</summary>
    public enum Mode
    {
        /// <summary>Ask the remote Kasada service — "Getting Kasada".</summary>
        Api,
        /// <summary>Run the page in a browser — "solving Kasada".</summary>
        Local,
        /// <summary>A fallback token, "Kasada-Fallback".</summary>
        Fallback,
        /// <summary>A mobile fallback token, "Kasada-Mobile-Fallback".</summary>
        MobileFallback,
    }

    /// <summary>The interface the image declares, which is why the modes are interchangeable.</summary>
    public const string SolverInterface = "IKasadaSolver";

    /// <summary>Status strings, verbatim. These are what the UI shows, so they are the contract.</summary>
    public static readonly IReadOnlyDictionary<string, string> Statuses =
        new Dictionary<string, string>(System.StringComparer.Ordinal)
        {
            ["Getting Kasada ("] = "api attempt, numbered",
            ["Getting Kasada (1)"] = "api attempt 1",
            ["Getting Kasada (2)"] = "api attempt 2",
            ["Getting Kasada (MFC)"] = "api attempt on the mobile-fallback path",
            ["Failed getting Kasada"] = "api path failed",
            ["Failed getting Kasada (Rotating)"] = "api path failed, proxy rotating",
            ["Failed solving Kasada"] = "local path failed",
            ["Failed solving Kasada (TL)"] = "local path failed on a TL step",
            ["Failed Kasada (Retry limit reached)"] = "the strategy gave up",
            ["Kasada API down (Contact staff)"] = "the service is unreachable — an operator problem",
            ["Kasada-Fallback"] = "a fallback token was used",
            ["Kasada-Mobile-Fallback"] = "a mobile fallback token was used",
        };

    /// <summary>The two fallback mode names, as the image spells them.</summary>
    public const string Fallback = "Kasada-Fallback";

    /// <inheritdoc cref="Fallback"/>
    public const string MobileFallback = "Kasada-Mobile-Fallback";

    /// <summary>The per-store version headers, which is why this is a table and not a constant.</summary>
    public static readonly IReadOnlyList<string> VersionHeaders = new[]
    {
        "Nike-Kasada-Version", "Footsites-Kasada-Version", "Scheels-Kasada-Version",
        "Converse-Kasada-Version", "Crocs-Kasada-Version", "Crocs-EU-Kasada-Version",
        "Crocs-JP-Kasada-Version",
    };

    /// <summary>The header names a solved request carries.</summary>
    public static readonly IReadOnlyList<string> ProtocolHeaders = new[]
    {
        "x-kpsdk-ct", "x-kpsdk-cd", "x-kpsdk-dt", "x-kpsdk-dv",
        "x-kpsdk-fc", "x-kpsdk-h", "x-kpsdk-im", "x-kpsdk-st",
    };

    /// <summary>Which verb a mode uses — the distinction the image's strings make.</summary>
    public static string Verb(Mode mode) => mode switch
    {
        Mode.Api => "getting",
        Mode.Local => "solving",
        _ => "falling back to",
    };

    /// <summary>True when a mode produces a token a caller can use for a real request.</summary>
    public static bool IsUsable(Mode mode) => mode is Mode.Api or Mode.Local or Mode.Fallback
        or Mode.MobileFallback;

    /// <summary>The mode a failure message belongs to, or null when the string is not one of ours.</summary>
    public static Mode? ModeFor(string? status)
    {
        if (string.IsNullOrEmpty(status)) return null;

        if (status.Contains("Getting Kasada", System.StringComparison.Ordinal)
            || status.Contains("Kasada API down", System.StringComparison.Ordinal))
            return status.Contains("(MFC)", System.StringComparison.Ordinal) ? Mode.MobileFallback : Mode.Api;

        if (status.Contains("Failed getting Kasada", System.StringComparison.Ordinal))
            return Mode.Api;

        if (status.Contains("Failed solving Kasada", System.StringComparison.Ordinal))
            return Mode.Local;

        if (status == MobileFallback) return Mode.MobileFallback;
        if (status == Fallback) return Mode.Fallback;

        return null;
    }

    /// <summary>Every status string, for a UI that must render them verbatim.</summary>
    public static IReadOnlyList<string> StatusList => Statuses.Keys.ToList();
}
