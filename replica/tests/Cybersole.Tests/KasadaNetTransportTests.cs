using System.Net;
using System.Net.Sockets;
using System.Text;
using Cybersole.Http;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// WHY THIS EXISTS: KasadaSolver.NetTransport is the adapter that turns the sensor's interrogation into a
/// real request on the replica's own HTTP stack. Its whole job is faithful translation -- the payload's
/// method, headers and body must arrive unchanged, and the response headers must come back intact,
/// because the clearance token only exists in one of them.
/// <para>
/// The server here is a hand-written TcpListener rather than HttpListener: it needs no URL ACL on Windows
/// and it lets the test observe the exact bytes that were sent.
/// </para>
/// </summary>
public sealed class KasadaNetTransportTests
{
    /// <summary>Accepts one request, records what arrived, replies with the given status and headers.</summary>
    private sealed class OneShotServer : IDisposable
    {
        private readonly TcpListener _listener;
        private readonly Task _serve;
        public string RawRequest { get; private set; } = "";
        public int Port => ((IPEndPoint)_listener.LocalEndpoint).Port;

        public OneShotServer(int status, params (string Name, string Value)[] headers)
        {
            _listener = new TcpListener(IPAddress.Loopback, 0);
            _listener.Start();
            _serve = Task.Run(async () =>
            {
                using var client = await _listener.AcceptTcpClientAsync().ConfigureAwait(false);
                using var stream = client.GetStream();

                var buffer = new byte[8192];
                var read = await stream.ReadAsync(buffer).ConfigureAwait(false);
                RawRequest = Encoding.UTF8.GetString(buffer, 0, read);

                // Drain the rest of the body so the client can finish writing before we answer.
                var headerEnd = RawRequest.IndexOf("\r\n\r\n", StringComparison.Ordinal);
                if (headerEnd >= 0)
                {
                    var declared = 0;
                    foreach (var line in RawRequest[..headerEnd].Split("\r\n"))
                        if (line.StartsWith("Content-Length:", StringComparison.OrdinalIgnoreCase))
                            declared = int.Parse(line["Content-Length:".Length..].Trim());
                    var have = RawRequest.Length - (headerEnd + 4);
                    while (have < declared)
                    {
                        read = await stream.ReadAsync(buffer).ConfigureAwait(false);
                        if (read <= 0) break;
                        have += read;
                        RawRequest += Encoding.UTF8.GetString(buffer, 0, read);
                    }
                }

                var sb = new StringBuilder();
                sb.Append("HTTP/1.1 ").Append(status).Append(" OK\r\n");
                sb.Append("Content-Length: 0\r\n");
                sb.Append("Connection: close\r\n");
                foreach (var (name, value) in headers)
                    sb.Append(name).Append(": ").Append(value).Append("\r\n");
                sb.Append("\r\n");
                await stream.WriteAsync(Encoding.ASCII.GetBytes(sb.ToString())).ConfigureAwait(false);
            });
        }

        public void Dispose()
        {
            try { _serve.Wait(TimeSpan.FromSeconds(5)); } catch (AggregateException) { }
            _listener.Stop();
        }
    }

    [Fact]
    public void TheTransportSendsThePayloadsMethodHeadersAndBodyAndReturnsTheResponseHeaders()
    {
        using var server = new OneShotServer(200, ("x-kpsdk-ct", "CT-OFF-THE-WIRE"));
        using var http = new NetClient();
        var transport = KasadaSolver.NetTransport(http);

        var json = transport(
            $"http://127.0.0.1:{server.Port}/r",
            "POST",
            """{"Content-Type":"text/plain","x-kpsdk-v":"j-1.2.988"}""",
            "encoded-interrogation-body");

        Assert.NotNull(json);
        using var doc = System.Text.Json.JsonDocument.Parse(json!);
        Assert.Equal(200, doc.RootElement.GetProperty("status").GetInt32());
        Assert.Equal("CT-OFF-THE-WIRE", doc.RootElement.GetProperty("headers").GetProperty("x-kpsdk-ct").GetString());

        // What arrived on the wire must be the payload's own request, not a rewritten one.
        Assert.StartsWith("POST /r ", server.RawRequest, StringComparison.Ordinal);
        Assert.Contains("encoded-interrogation-body", server.RawRequest, StringComparison.Ordinal);
        Assert.Contains("j-1.2.988", server.RawRequest, StringComparison.Ordinal);
    }

    [Fact]
    public void TheTransportSurfacesUnreachableEndpointsWithoutThrowing()
    {
        // Port 1 on loopback: nothing listens, so the send fails fast and locally.
        using var http = new NetClient();
        var transport = KasadaSolver.NetTransport(http);

        var json = transport("http://127.0.0.1:1/r", "POST", "{}", "body");

        // Either the client answered with a status or the runtime wrapped the failure, but in both cases
        // the solver must get parseable JSON rather than an exception escaping into the script engine.
        Assert.NotNull(json);
        using var doc = System.Text.Json.JsonDocument.Parse(json!);
        Assert.True(doc.RootElement.TryGetProperty("status", out _));
    }

    [Fact]
    public void TheTransportRefusesToBeBuiltWithoutAClient()
    {
        Assert.Throws<ArgumentNullException>(() => KasadaSolver.NetTransport(null!));
    }
}
