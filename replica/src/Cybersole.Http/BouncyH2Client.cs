using System.Buffers.Binary;
using System.Text;
using Cybersole.Core.Models;
using Cybersole.Http.Compression;

namespace Cybersole.Http;

/// <summary>
/// HTTP/2 client running on the BouncyCastle TLS channel.
/// Uses the controlled ClientHello (ALPN offers h2 first) and speaks real h2 frames,
/// so it works against h2-only edges such as Cloudflare.
/// </summary>
public sealed class BouncyH2Client : IDisposable
{
    private readonly HttpAnalytics? _analytics;

    public BouncyH2Client(HttpAnalytics? analytics = null) => _analytics = analytics;

    public Task<NetResponse> GetAsync(string url, TlsProfile? profile = null,
        Proxy? proxy = null, TimeSpan? timeout = null, string? tag = null, CancellationToken ct = default)
        => SendAsync("GET", url, profile, proxy, null, null, timeout, tag, ct);

    public async Task<NetResponse> SendAsync(string method, string url, TlsProfile? profile = null,
        Proxy? proxy = null, IDictionary<string, string>? headers = null, string? body = null,
        TimeSpan? timeout = null, string? tag = null, CancellationToken ct = default)
    {
        profile ??= TlsProfile.Chrome;
        var uri = new Uri(url);
        if (uri.Scheme != "https")
            throw new NetException("BouncyH2Client only supports https://");
        var port = uri.Port > 0 ? uri.Port : 443;

        var sw = System.Diagnostics.Stopwatch.StartNew();
        var (protocol, probe) = await BouncyTls.ConnectAsync(uri.Host, port, profile, proxy, ct)
            .ConfigureAwait(false);
        if (protocol is null)
            throw new NetException($"TLS handshake failed: {probe.Error}");

        try
        {
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
            cts.CancelAfter(timeout ?? TimeSpan.FromSeconds(30));
            var stream = protocol.Stream;

            // ---- connection preface + settings ----
            await stream.WriteAsync(Encoding.ASCII.GetBytes(Http2.Preface), cts.Token).ConfigureAwait(false);
            await stream.WriteAsync(Http2.SettingsFrame(), cts.Token).ConfigureAwait(false);

            var path = string.IsNullOrEmpty(uri.PathAndQuery) ? "/" : uri.PathAndQuery;
            var bodyBytes = string.IsNullOrEmpty(body) ? Array.Empty<byte>() : Encoding.UTF8.GetBytes(body);
            IEnumerable<KeyValuePair<string, string>>? extra = headers;
            if (headers is null || !headers.Keys.Any(k => string.Equals(k, "accept-encoding", StringComparison.OrdinalIgnoreCase)))
            {
                var list = headers is null
                    ? new List<KeyValuePair<string, string>>(1)
                    : new List<KeyValuePair<string, string>>(headers);
                list.Add(new KeyValuePair<string, string>("accept-encoding", ContentEncodingCodec.DefaultAcceptEncoding));
                extra = list;
            }

            var block = Http2.EncodeHeaders(uri.Host, path, profile.UserAgent,
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", profile.AcceptLanguage,
                method, extra);

            var headersFlags = (byte)(Http2.FlagEndHeaders | (bodyBytes.Length == 0 ? Http2.FlagEndStream : 0));
            await stream.WriteAsync(Http2.Frame(Http2.Headers, headersFlags, 1, block), cts.Token)
                .ConfigureAwait(false);

            if (bodyBytes.Length > 0)
            {
                await stream.WriteAsync(
                    Http2.Frame(Http2.Data, Http2.FlagEndStream, 1, bodyBytes), cts.Token)
                    .ConfigureAwait(false);
            }

            await stream.FlushAsync(cts.Token).ConfigureAwait(false);

            // ---- read loop ----
            var headerBlock = new MemoryStream();
            var responseBody = new MemoryStream();
            var status = 0;
            var endStream = false;

            while (!endStream)
            {
                var (type, flags, streamId, payload) = await Http2.ReadFrameAsync(stream, cts.Token)
                    .ConfigureAwait(false);

                switch (type)
                {
                    case Http2.Settings:
                        if ((flags & Http2.FlagAck) == 0)
                            await stream.WriteAsync(Http2.Frame(Http2.Settings, Http2.FlagAck, 0, Array.Empty<byte>()),
                                cts.Token).ConfigureAwait(false);
                        break;

                    case Http2.Ping:
                        if ((flags & Http2.FlagAck) == 0)
                            await stream.WriteAsync(Http2.Frame(Http2.Ping, Http2.FlagAck, 0, payload),
                                cts.Token).ConfigureAwait(false);
                        break;

                    case Http2.Headers:
                        headerBlock.Write(payload);
                        if ((flags & Http2.FlagEndHeaders) != 0 && status == 0)
                            status = Http2.DecodeStatus(headerBlock.ToArray());
                        if ((flags & Http2.FlagEndStream) != 0) endStream = true;
                        break;

                    case Http2.Continuation:
                        headerBlock.Write(payload);
                        if ((flags & Http2.FlagEndHeaders) != 0 && status == 0)
                            status = Http2.DecodeStatus(headerBlock.ToArray());
                        break;

                    case Http2.Data:
                        responseBody.Write(payload);
                        if ((flags & Http2.FlagEndStream) != 0) endStream = true;
                        break;

                    case Http2.RstStream:
                        var code = payload.Length >= 4 ? BinaryPrimitives.ReadInt32BigEndian(payload) : 0;
                        throw new NetException($"h2 stream reset (code 0x{code:X})");

                    case Http2.GoAway:
                        endStream = true;
                        break;

                    default:
                        break;
                }
            }

            sw.Stop();
            var responseHeaders = Http2.DecodeHeaders(headerBlock.ToArray());
            var data = responseBody.ToArray();

            _analytics?.Record(new HttpRequestEvent
            {
                Url = uri.ToString(),
                Method = method,
                Status = status,
                ElapsedMs = (int)sw.Elapsed.TotalMilliseconds,
                Bytes = data.LongLength,
                Protocol = "h2",
                Profile = profile.Name,
                Proxy = proxy?.Uri,
                Tag = tag,
                At = DateTime.UtcNow,
            });

            return new NetResponse
            {
                StatusCode = status,
                Body = ContentEncodingCodec.DecompressToString(data, responseHeaders),
                Url = uri,
                Headers = responseHeaders,
                Elapsed = sw.Elapsed,
                Bytes = data.LongLength,
                Protocol = "h2",
            };
        }
        finally
        {
            try { protocol.Close(); } catch { /* closing a dead channel */ }
        }
    }

    public void Dispose() { }
}
