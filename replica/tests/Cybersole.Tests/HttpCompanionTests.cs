using System.Buffers;
using System.Buffers.Binary;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http;
using Cybersole.Http.Content;
using Cybersole.Http.X509;
using Cybersole.Tests.Support;
using Newtonsoft.Json.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Wave 2D behavioral &amp; protocol tests for <see cref="IBody"/> (<see cref="LegacyJsonBody"/>,
/// <see cref="LegacyJarrayBody"/>, <see cref="BytesBody"/>, <see cref="StringBody"/>),
/// <see cref="ClickHouseSink"/> (gzip JSONEachRow + zero disk spill), <see cref="HttpDebug"/> CSHD v1
/// binary TCP framing, and <see cref="RootCertificateStore"/>.
/// </summary>
public sealed class HttpCompanionTests
{
    [Fact]
    public async Task LegacyBodiesSerializeWithoutBomAndDispatchViaNetClient()
    {
        var nullBody = new LegacyJsonBody((JToken?)null);
        var abwNull = new ArrayBufferWriter<byte>();
        nullBody.WriteTo(abwNull);
        Assert.Equal("null", Encoding.UTF8.GetString(abwNull.WrittenSpan));

        var objBody = new LegacyJsonBody().Set("sku", "ABC-1");
        objBody["qty"] = 2;
        var abwObj = new ArrayBufferWriter<byte>();
        objBody.WriteTo(abwObj);
        Assert.Equal("{\"sku\":\"ABC-1\",\"qty\":2}", Encoding.UTF8.GetString(abwObj.WrittenSpan));

        var arrBody = new LegacyJarrayBody().Add("x").Add(7);
        var nonObject = new LegacyJsonBody(new JArray { 1 });
        var ex = Assert.Throws<InvalidOperationException>(() => nonObject["k"] = "v");
        Assert.Equal("The body does not hold a JSON object.", ex.Message);

        string? seenContentType = null;
        string? seenBody = null;
        using var server = new TinyServer((req, body) =>
        {
            seenContentType = req.ContentType;
            seenBody = body;
            return (200, "{\"ok\":true}");
        });

        using var http = new NetClient();
        var res = await http.PostBodyAsync(server.BaseUrl + "/items", arrBody);
        Assert.Equal(200, res.StatusCode);
        Assert.StartsWith("application/json", seenContentType);
        Assert.Equal("[\"x\",7]", seenBody);

        // Caller-supplied Content-Type is preserved instead of overwritten (0x14128a8e0)
        var customOpts = new RequestOptions();
        customOpts.Headers["Content-Type"] = "application/vnd.custom+json";
        await http.PostBodyAsync(server.BaseUrl + "/raw", new BytesBody("raw"u8.ToArray(), "application/octet-stream"), customOpts);
        Assert.Equal("application/vnd.custom+json", seenContentType);
    }

    [Fact]
    public async Task ClickHouseSinkPostsGzipJsonEachRowWithExactColumnsAndNoDiskSpill()
    {
        var captured = new List<(string PathAndQuery, string? User, string? Key, string? Encoding, string? Type, string Body)>();
        var port = FreePort();
        var baseUrl = $"http://127.0.0.1:{port}";
        using var listener = new HttpListener();
        listener.Prefixes.Add(baseUrl + "/");
        listener.Start();

        var acceptTask = Task.Run(async () =>
        {
            for (var i = 0; i < 2; i++)
            {
                var ctx = await listener.GetContextAsync();
                using var gz = new GZipStream(ctx.Request.InputStream, CompressionMode.Decompress);
                using var sr = new StreamReader(gz, Encoding.UTF8);
                var text = await sr.ReadToEndAsync();
                captured.Add((
                    ctx.Request.Url?.PathAndQuery ?? "",
                    ctx.Request.Headers["x-clickhouse-user"],
                    ctx.Request.Headers["x-clickhouse-key"],
                    ctx.Request.Headers["content-encoding"],
                    ctx.Request.ContentType,
                    text));
                ctx.Response.StatusCode = 200;
                ctx.Response.Close();
            }
        });

        using var sink = new ClickHouseSink(new ClickHouseSinkOptions
        {
            EndpointOverride = baseUrl,
            User = "http_writer",
            Key = "secret-key",
            Database = "default",
            BatchSize = 50,
            Capacity = 100,
        });

        using var analytics = new HttpAnalytics { ClickHouse = sink, BatchSize = 100 };
        analytics.Record(new HttpRequestEvent
        {
            RequestId = "req-1",
            Method = "POST",
            Url = "https://shop.test/cart?id=1",
            Status = 201,
            ElapsedMs = 42,
            Bytes = 128,
            Protocol = "h2",
            Profile = "chrome",
            Tag = "atc",
        });
        analytics.RecordConnection(new HttpConnectionEvent
        {
            ConnectionId = "conn-1",
            Endpoint = "https://shop.test:443",
            State = "opened",
            Protocol = "h2",
            TlsVersion = "Tls13",
            Alpn = "h2",
        });

        await sink.DrainLocalQueueAsync();
        await acceptTask.WaitAsync(TimeSpan.FromSeconds(5));

        Assert.Equal(2, captured.Count);
        Assert.Contains("INSERT%20INTO%20default.http_requests%20FORMAT%20JSONEachRow", captured[0].PathAndQuery);
        Assert.Equal("gzip", captured[0].Encoding);
        Assert.Equal("application/x-ndjson", captured[0].Type);
        Assert.Equal("http_writer", captured[0].User);
        Assert.Equal("secret-key", captured[0].Key);

        var reqRow = JObject.Parse(captured[0].Body.Trim());
        Assert.Equal("req-1", reqRow["request_id"]?.ToString());
        Assert.Equal("shop.test", reqRow["host"]?.ToString());
        Assert.Equal(201, reqRow["status"]?.Value<int>());
        Assert.NotNull(reqRow["request_header_bytes"]);
        Assert.NotNull(reqRow["connection_reused"]);

        var connRow = JObject.Parse(captured[1].Body.Trim());
        Assert.Equal("opened", connRow["event"]?.ToString());
        Assert.Equal("conn-1", connRow["connection_id"]?.ToString());
        Assert.Equal("Tls13", connRow["tls_version"]?.ToString());

        // Failure drops batch in memory, increments DroppedCount, invokes throttled OnError (no disk spill)
        using var failing = new ClickHouseSink(new ClickHouseSinkOptions { EndpointOverride = "http://127.0.0.1:1" });
        string? errMsg = null;
        failing.OnError = msg => errMsg = msg;
        failing.TryEnqueue(new HttpRequestEvent { Url = "https://shop.test/a" });
        await failing.DrainLocalQueueAsync();
        Assert.Equal(1, failing.DroppedCount);
        Assert.StartsWith("Rows could not be sent:", errMsg);
    }

    [Fact]
    public async Task HttpDebugStreamsCshdBinaryFramesOverTcp()
    {
        using var httpServer = new TinyServer(_ => (200, "pong"));
        using var listener = new TcpListener(IPAddress.Loopback, 0);
        listener.Start();
        var port = ((IPEndPoint)listener.LocalEndpoint).Port;

        var frames = new List<(HttpDebugFrameType Type, JObject Json, byte[] Bin)>();
        byte[]? greeting = null;

        try
        {
            var readerTask = Task.Run(async () =>
            {
                using var tcp = await listener.AcceptTcpClientAsync();
                using var stream = tcp.GetStream();
                greeting = await ReadExactAsync(stream, 5);

                // Read Hello + Request + Response frames (3 frames)
                for (var i = 0; i < 3; i++)
                {
                    var lenBuf = await ReadExactAsync(stream, 4);
                    var totalLen = BinaryPrimitives.ReadInt32LittleEndian(lenBuf);
                    var payload = await ReadExactAsync(stream, totalLen);
                    var frameType = (HttpDebugFrameType)payload[0];
                    var jsonLen = BinaryPrimitives.ReadInt32LittleEndian(payload.AsSpan(1, 4));
                    var jsonText = Encoding.UTF8.GetString(payload, 5, jsonLen);
                    var bin = payload.AsSpan(5 + jsonLen).ToArray();
                    frames.Add((frameType, JObject.Parse(jsonText), bin));
                }
            });

            HttpDebug.EnableStream($"127.0.0.1:{port}", connectTimeout: TimeSpan.FromSeconds(2), reconnectDelay: TimeSpan.FromMilliseconds(50));
            using var client = new NetClient();
            var res = await client.PostBodyAsync(httpServer.BaseUrl + "/dbg", new StringBody("hello-wire"));
            Assert.Equal("pong", res.Body);

            await readerTask.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.Equal("CSHD\x01", Encoding.ASCII.GetString(greeting!));
            Assert.Equal(HttpDebugFrameType.Hello, frames[0].Type);
            Assert.Equal("Cybersole.Http", frames[0].Json["library"]?.ToString());
            Assert.Equal(HttpDebugFrameType.Request, frames[1].Type);
            Assert.Equal("hello-wire", Encoding.UTF8.GetString(frames[1].Bin));
            Assert.Equal(HttpDebugFrameType.Response, frames[2].Type);
            Assert.Equal(200, frames[2].Json["status"]?.Value<int>());
            Assert.Equal("pong", Encoding.UTF8.GetString(frames[2].Bin));
            Assert.NotNull(frames[2].Json["timing"]?["metrics"]);
        }
        finally
        {
            HttpDebug.DisableStream();
        }
    }

    [Fact]
    public void RootCertificateStoreRoundTripsLengthPrefixedDerBundleAndVerifiesChain()
    {
        using var rootKey = RSA.Create(2048);
        var rootReq = new CertificateRequest("CN=Cybersole Test Root", rootKey, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        rootReq.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        rootReq.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(rootReq.PublicKey, false));
        using var rootCert = rootReq.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddDays(30));

        using var leafKey = RSA.Create(2048);
        var leafReq = new CertificateRequest("CN=shop.test", leafKey, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        leafReq.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
        var serial = new byte[8];
        RandomNumberGenerator.Fill(serial);
        using var leafCert = leafReq.Create(rootCert, DateTimeOffset.UtcNow.AddHours(-1), DateTimeOffset.UtcNow.AddDays(7), serial);

        using var ms = new MemoryStream();
        RootCertificateStore.WriteBundleStream(ms, new[] { rootCert });
        ms.Position = 0;

        var loaded = RootCertificateStore.LoadFromBundleStream(ms);
        Assert.Equal(1, loaded.Count);
        Assert.Single(loaded.FindBySubject(rootCert.SubjectName.Name));
        Assert.True(loaded.VerifyChain(leafCert));
        Assert.False(new RootCertificateStore().VerifyChain(leafCert));
    }

    private static async Task<byte[]> ReadExactAsync(NetworkStream stream, int count)
    {
        var buf = new byte[count];
        var read = 0;
        while (read < count)
        {
            var n = await stream.ReadAsync(buf.AsMemory(read, count - read));
            if (n == 0) throw new EndOfStreamException();
            read += n;
        }
        return buf;
    }

    private static int FreePort()
    {
        using var tcp = new TcpListener(IPAddress.Loopback, 0);
        tcp.Start();
        return ((IPEndPoint)tcp.LocalEndpoint).Port;
    }
}
