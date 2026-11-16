using System;
using System.Threading;
using System.Threading.Tasks;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// Sends a built session payload, and refuses to send it anywhere the image did not name (R154).
///
/// <para>
/// R153 made the payload buildable. This is the part that could go wrong in a way nobody would notice: a
/// telemetry sender with an unset or misspelled host that quietly posts a fingerprint to whatever it was
/// pointed at. Two guards, both testable without a network:
/// </para>
///
/// <list type="number">
/// <item><b>No sink, no send.</b> The default is unset, and unset means the caller gets a reason rather than
/// a silent success.</item>
/// <item><b>Only the recorded hosts.</b> <see cref="CybersoleHosts"/> holds the fifteen names the image
/// carries; <c>analytics.cybersole.io</c> and <c>telemetry.cybersole.io</c> are the two that make sense for
/// this payload, and anything else is refused by name — the same rule
/// <c>endpoint-provenance.py</c> enforces for storefront endpoints, applied to Cybersole's own.</item>
/// </list>
///
/// <para>
/// The post itself is injected so a test can observe exactly what would have been sent, and
/// <see cref="LastError"/> records a failure instead of throwing: telemetry must never be on the checkout
/// path's critical side.
/// </para>
/// </summary>
public sealed class SessionTelemetry : Cybersole.Http.ISessionSink
{
    /// <summary>The two hosts that receive this payload, out of the fifteen the image names.</summary>
    public static readonly string[] AllowedHosts =
    {
        "analytics.cybersole.io",
        "telemetry.cybersole.io",
    };

    private readonly Func<string, string, CancellationToken, Task<bool>> _post;

    public SessionTelemetry(string? sinkUrl = null,
        Func<string, string, CancellationToken, Task<bool>>? post = null)
    {
        SinkUrl = sinkUrl;
        _post = post ?? DefaultPostAsync;
    }

    /// <summary>Where the payload goes. Unset by default — an unconfigured sender sends nothing.</summary>
    public string? SinkUrl { get; set; }

    /// <summary>The reason the last attempt did not send, or null when it did.</summary>
    public string? LastError { get; private set; }

    /// <summary>
    /// Where the inputs come from when the analytics flush calls this sink (R155).
    ///
    /// <para>
    /// The flush runs on a timer and knows nothing about sessions, so the caller supplies a factory rather
    /// than a snapshot: the payload must describe the session as it is at send time, not as it was when the
    /// sink was attached.
    /// </para>
    /// </summary>
    public Func<SessionPayloadBuilder.Inputs>? InputsFactory { get; set; }

    /// <summary>The flush's entry point: build from the factory and send.</summary>
    async Task<bool> Cybersole.Http.ISessionSink.SendAsync(CancellationToken ct)
    {
        if (InputsFactory is null)
        {
            LastError = "no inputs factory: nothing to describe";
            return false;
        }

        return await SendAsync(InputsFactory(), ct).ConfigureAwait(false);
    }

    /// <summary>True when a sink is set and its host is one of the allowed two.</summary>
    public bool IsConfigured => HostOf(SinkUrl) is { } host
        && Array.Exists(AllowedHosts, h => string.Equals(h, host, StringComparison.OrdinalIgnoreCase));

    /// <summary>The host of a URL, or null when it cannot be read.</summary>
    public static string? HostOf(string? url) =>
        Uri.TryCreate(url, UriKind.Absolute, out var uri) ? uri.Host : null;

    /// <summary>
    /// Build and post. Returns true only when the payload was handed to the transport, and records a reason
    /// for every other outcome.
    /// </summary>
    public async Task<bool> SendAsync(SessionPayloadBuilder.Inputs inputs, CancellationToken ct = default)
    {
        LastError = null;

        if (string.IsNullOrEmpty(SinkUrl))
        {
            LastError = "no sink configured: telemetry stays in memory";
            return false;
        }

        var host = HostOf(SinkUrl);
        if (host is null || !IsConfigured)
        {
            LastError = $"sink host is not one of the recorded hosts ({string.Join(", ", AllowedHosts)})";
            return false;
        }

        // the payload is built even when the send fails, so a caller can log what it would have sent
        var payload = SessionPayloadBuilder.Build(inputs).ToString(Newtonsoft.Json.Formatting.None);

        try
        {
            if (!await _post(SinkUrl!, payload, ct).ConfigureAwait(false))
                LastError = "transport refused the payload";
            return LastError is null;
        }
        catch (OperationCanceledException)
        {
            LastError = "cancelled";
            return false;
        }
        catch (Exception ex)
        {
            LastError = "transport failed: " + ex.Message;
            return false;
        }
    }

    /// <summary>The default transport: one POST of JSON. Never throws to the caller.</summary>
    private static async Task<bool> DefaultPostAsync(string url, string payload, CancellationToken ct)
    {
        using var http = new System.Net.Http.HttpClient { Timeout = TimeSpan.FromSeconds(15) };
        using var content = new System.Net.Http.StringContent(
            payload, System.Text.Encoding.UTF8, "application/json");
        using var response = await http.PostAsync(url, content, ct).ConfigureAwait(false);
        return response.IsSuccessStatusCode;
    }
}
