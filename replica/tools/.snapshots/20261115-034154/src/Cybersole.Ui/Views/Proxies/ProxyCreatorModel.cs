using System;
using System.Collections.Generic;
using System.IO;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views.Proxies;

/// <summary>
/// The logic behind the proxy creator modal, kept out of the window so it can be tested without a UI (R204).
///
/// <para>
/// The original's modal is <c>Cybersole.Ui.Views.Proxies.Modals.ProxyCreatorView</c>, and the image names one of its
/// behaviours outright:
/// </para>
///
/// <code>
/// 0x06e5071c  ProxyCreator.DragDrop
/// </code>
///
/// <para>
/// So the creator takes <b>dropped text or files</b>, not just typed fields. This replica had no creator at all — the
/// proxies page only had a bulk "Add Proxies" importer — which meant "create one proxy, carefully" had no path.
/// </para>
///
/// <para>
/// The parse itself is not re-implemented here: <see cref="ImportParser.ParseProxies"/> already accepts
/// <c>host:port</c>, <c>host:port:user:pass</c> and <c>scheme://…</c>, and the creator must agree with the importer rather
/// than drift from it.
/// </para>
/// </summary>
public sealed class ProxyCreatorModel
{
    /// <summary>What one drop produced.</summary>
    public sealed record Result(IReadOnlyList<Proxy> Accepted, int Rejected)
    {
        /// <summary>How many lines the drop carried.</summary>
        public int Total => Accepted.Count + Rejected;
    }

    /// <summary>Every proxy created so far, in drop order.</summary>
    public List<Proxy> Created { get; } = new();

    /// <summary>Reads a dropped file as text; returns null when it cannot be read.</summary>
    public static string? ReadDroppedFile(string path)
    {
        try
        {
            if (!File.Exists(path)) return null;
            var info = new FileInfo(path);
            if (info.Length > 4 * 1024 * 1024) return null;   // a proxy list is not a disk image
            return File.ReadAllText(path);
        }
        catch (IOException) { return null; }
        catch (UnauthorizedAccessException) { return null; }
    }

    /// <summary>
    /// Parses dropped or typed text and keeps the proxies. Returns the count accepted and rejected, so the modal can
    /// say "12 added, 1 line not understood" instead of silently dropping the line.
    /// </summary>
    public Result AddFromText(string? text)
    {
        var parsed = ImportParser.ParseProxies(text);
        var accepted = new List<Proxy>();
        var lines = 0;

        if (!string.IsNullOrWhiteSpace(text))
        {
            foreach (var raw in text.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
            {
                if (raw.StartsWith('#') || raw.StartsWith("//")) continue;
                lines++;
            }
        }

        foreach (var proxy in parsed)
        {
            if (string.IsNullOrWhiteSpace(proxy.Host) || proxy.Port is <= 0 or > 65535) continue;
            Created.Add(proxy);
            accepted.Add(proxy);
        }

        return new Result(accepted, Math.Max(0, lines - accepted.Count));
    }

    /// <summary>
    /// The typed-single-proxy path: host, port and an optional credential pair. Returns null when the values cannot
    /// make a proxy (an empty host, a port outside 1..65535), so the modal can keep the field open rather than add a
    /// row that will never connect.
    /// </summary>
    public Proxy? AddOne(string? host, string? port, string? username = null, string? password = null,
        string scheme = "http")
    {
        host = host?.Trim();
        if (string.IsNullOrWhiteSpace(host)) return null;
        if (!int.TryParse(port?.Trim(), out var portNumber)) return null;
        if (portNumber is <= 0 or > 65535) return null;

        var proxy = new Proxy
        {
            Host = host,
            Port = portNumber,
            Username = string.IsNullOrWhiteSpace(username) ? null : username!.Trim(),
            Password = string.IsNullOrWhiteSpace(password) ? null : password!.Trim(),
            Scheme = string.IsNullOrWhiteSpace(scheme) ? "http" : scheme.Trim().ToLowerInvariant(),
        };

        Created.Add(proxy);
        return proxy;
    }
}
