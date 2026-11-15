using Cybersole.Http;
using System.Text;

// `verify.ps1 -Full` could not read this program's output when it ran after `dotnet test`: the
// process exited 0 with an empty stdout, even though the same exe prints normally from a shell
// and even through Start-Process with redirection when run on its own. The probe was fine; the
// pipe was not. Rather than keep guessing at Windows PowerShell 5.1's stdio handling, the probe
// can write its own file:
//
//     TlsProbe.Cli --own example.com --out C:\temp\probe.txt
//
// --out is stripped from the argument list before dispatch, so every existing invocation keeps
// working unchanged.
var argList = args.ToList();
var outIndex = argList.IndexOf("--out");
if (outIndex >= 0 && outIndex + 1 < argList.Count)
{
    var outPath = argList[outIndex + 1];
    argList.RemoveRange(outIndex, 2);
    var writer = new StreamWriter(outPath, append: false, new UTF8Encoding(false))
    {
        AutoFlush = true,
    };
    Console.SetOut(writer);
}
args = argList.ToArray();

if (args.Length >= 2 && args[0] == "--own")
{
    var target = args[1].StartsWith("http") ? args[1] : "https://" + args[1];
    Console.WriteLine($"OwnTls transport -> {target}");
    using var ownClient = new Cybersole.Http.NetClient();
    ownClient.Transport = Cybersole.Http.TransportMode.OwnTls;
    var isPost = args.Length > 2 && args[2].Equals("POST", StringComparison.OrdinalIgnoreCase);
    Cybersole.Http.NetResponse res;
    if (isPost)
    {
        var payload = "{\"probe\":\"own-tls\",\"n\":42}";
        res = await ownClient.PostJsonAsync(target, payload);
    }
    else
    {
        res = await ownClient.GetAsync(target);
    }
    Console.WriteLine($"  HTTP {res.StatusCode}  {res.Bytes} bytes  proto={res.Protocol}" +
                      $"  transport={res.Headers.GetValueOrDefault("X-Cyb-Transport")}" +
                      $"  alpn={res.Headers.GetValueOrDefault("X-Cyb-Alpn")}");
    var head = res.Body.Length > 120 ? res.Body[..120] : res.Body;
    Console.WriteLine("  body: " + head.Replace("\r\n", " | "));
    return;
}


if (args.Length >= 2 && args[0] == "--tls12-full")
{
    var parts = args[1].Split(':');
    var fhost = parts[0];
    var fport = parts.Length > 1 && int.TryParse(parts[1], out var fp) ? fp : 443;
    Console.WriteLine($"full TLS1.2 handshake (own stack) -> {fhost}:{fport}");
    var useProfile = Cybersole.Http.TlsProfile.Chrome;
    if (args.Length > 2 && args[2] == "p256")
    {
        useProfile = new Cybersole.Http.TlsProfile
        {
            Name = "p256",
            CipherSuiteNames = Cybersole.Http.TlsProfile.Chrome.CipherSuiteNames,
            Alpn = Cybersole.Http.TlsProfile.Chrome.Alpn,
            Curves = new List<int> { 23 },
            Grease = true,
        };
        Console.WriteLine("  (using P-256-only profile)");
    }
    try
    {
        using var tls = await Cybersole.Http.Tls12Client.ConnectAsync(fhost, fport, useProfile);
        Console.WriteLine($"  handshake OK  version={tls.Version}  cipher={tls.CipherSuite}  alpn={tls.Alpn ?? "-"}");
        var res = await tls.GetAsync("/", fhost);
        Console.WriteLine($"  HTTP {res.StatusCode}  {res.Bytes} bytes");
        var head = res.Body.Length > 160 ? res.Body[..160] : res.Body;
        Console.WriteLine("  body head: " + head.Replace("\r\n", " | "));
    }
    catch (Exception ex)
    {
        Console.WriteLine($"  FAILED: {ex.GetType().Name}: {ex.Message}");
    }
    return;
}


if (args.Length >= 2 && args[0] == "--flight")
{
    var parts = args[1].Split(':');
    var fhost = parts[0];
    var fport = parts.Length > 1 && int.TryParse(parts[1], out var fp) ? fp : 443;
    Console.WriteLine($"reading server flight from {fhost}:{fport} (hand-built ClientHello)");
    var flight = await Cybersole.Http.Tls12FlightReader.ReadAsync(fhost, fport, Cybersole.Http.TlsProfile.Chrome);
    Console.WriteLine($"ok={flight.Ok} err={flight.Error ?? "-"}");
    if (flight.ServerHello is { } sh)
        Console.WriteLine($"  server_hello version={sh.Version} cipher={sh.CipherSuite} alpn={sh.Alpn ?? "-"} ext={sh.ExtensionCount}");
    Console.WriteLine($"  certificates={flight.CertificateCount}");
    if (flight.ServerEcdhePublicKey is { } pk)
        Console.WriteLine($"  server_ecdhe_len={pk.Length} first_byte=0x{pk[0]:X2}");
    Console.WriteLine($"  pre_master_len={flight.PreMasterLength}");
    return;
}


if (args.Length >= 2 && args[0] == "--tls12")
{
    var parts = args[1].Split(':');
    var thost = parts[0];
    var tport = parts.Length > 1 && int.TryParse(parts[1], out var tp) ? tp : 443;
    var hello = Cybersole.Http.Ja3.BuildClientHello(Cybersole.Http.TlsProfile.Chrome, thost, out var ja3);
    Console.WriteLine($"ja3={ja3}");
    Console.WriteLine($"sending {hello.Length}-byte hand-built ClientHello to {thost}:{tport}");
    var sh = await Cybersole.Http.Tls12Handshake.ProbeAsync(thost, tport, Cybersole.Http.TlsProfile.Chrome);
    Console.WriteLine($"server_hello ok={sh.Ok} version={sh.Version} cipher={sh.CipherSuite} alpn={sh.Alpn ?? "-"} extensions={sh.ExtensionCount} err={sh.Error}");
    return;
}


if (args.Length >= 2 && args[0] == "--ja3")
{
    var parts = args[1].Split(':');
    var jhost = parts[0];
    var jport = parts.Length > 1 && int.TryParse(parts[1], out var jp) ? jp : 443;
    var hello = Cybersole.Http.Ja3.BuildClientHello(Cybersole.Http.TlsProfile.Chrome, "example.com", out var ja3);
    using var tcp = new System.Net.Sockets.TcpClient();
    await tcp.ConnectAsync(jhost, jport);
    await using var net = tcp.GetStream();
    await net.WriteAsync(hello);
    await net.FlushAsync();
    Console.WriteLine($"ja3={ja3}");
    Console.WriteLine($"sent {hello.Length} bytes to {jhost}:{jport}");
    return;
}


var host = args.Length > 0 ? args[0] : "api.cybersole.io";
var port = args.Length > 1 && int.TryParse(args[1], out var p) ? p : 443;

Console.WriteLine($"TLS / HTTP fingerprint probe -> {host}:{port}");
Console.WriteLine(new string('-', 112));

Console.WriteLine("SChannel (SslStream + CipherSuitesPolicy):");
Console.WriteLine($"  {"profile",-10} {"ok",-6} {"protocol",-9} {"cipher",-46} {"alpn",-9} ms");
foreach (var profile in TlsProfile.All)
{
    var r = await TlsProbe.ProbeAsync(host, port, profile);
    Console.WriteLine($"  {profile.Name,-10} {r.Ok,-6} {r.Protocol,-9} {Trunc(r.CipherSuite, 46),-46} {r.Alpn ?? "-",-9} {r.HandshakeMs}");
    if (!r.Ok) Console.WriteLine($"             error: {Trunc(r.Error ?? "", 90)}");
}

Console.WriteLine();
Console.WriteLine("BouncyCastle (custom ClientHello: cipher list + hand-encoded SNI/ALPN):");
Console.WriteLine($"  {"profile",-10} {"ok",-6} {"protocol",-9} {"cipher",-46} ms");
foreach (var profile in TlsProfile.All)
{
    var (protocol, result) = await BouncyTls.ConnectAsync(host, port, profile);
    Console.WriteLine($"  {profile.Name,-10} {result.Ok,-6} {result.Protocol,-9} {Trunc(result.CipherSuite, 46),-46} {result.HandshakeMs}");
    if (!result.Ok) Console.WriteLine($"             error: {Trunc(result.Error ?? "", 90)}");
    protocol?.Close();
}

Console.WriteLine();
Console.WriteLine("HTTP round-trips:");
using var client = new NetClient();
try
{
    var res = await client.GetAsync($"https://{host}/", new RequestOptions { Timeout = TimeSpan.FromSeconds(15), Tag = "probe" });
    Console.WriteLine($"  SChannel/NetClient   HTTP {res.StatusCode}  {res.Protocol}  {res.Bytes} bytes  {res.Elapsed.TotalMilliseconds:0} ms  server={res.Headers.GetValueOrDefault("Server", "-")}");
}
catch (Exception ex)
{
    Console.WriteLine($"  SChannel/NetClient   request failed: {Trunc(ex.Message, 90)}");
}

try
{
    using var h2 = new BouncyH2Client();
    var r = await h2.GetAsync($"https://{host}/", TlsProfile.Chrome, tag: "h2");
    Console.WriteLine($"  BouncyCastle/h2      HTTP {r.StatusCode}  {r.Protocol}  {r.Bytes} bytes  {r.Elapsed.TotalMilliseconds:0} ms");
    Console.WriteLine($"                       server={r.Headers.GetValueOrDefault("server", "-")}  cf-ray={r.Headers.GetValueOrDefault("cf-ray", "-")}");
}
catch (Exception ex)
{
    Console.WriteLine($"  BouncyCastle/h2      request failed: {Trunc(ex.Message, 110)}");
}

try
{
    using var bc = new BouncyHttpClient();
    var bcTarget = Environment.GetEnvironmentVariable("BC_HTTP_HOST") ?? "example.com";
    var bcRes = await bc.GetAsync($"https://{bcTarget}/", TlsProfile.Chrome, forceHttp11: true, tag: "bc");
    Console.WriteLine($"  BouncyCastle/http1.1 HTTP {bcRes.StatusCode}  {bcRes.Bytes} bytes  {bcRes.Elapsed.TotalMilliseconds:0} ms  host={bcTarget}  server={bcRes.Headers.GetValueOrDefault("Server", "-")}");
}
catch (Exception ex)
{
    Console.WriteLine($"  BouncyCastle/http1.1 request failed: {Trunc(ex.Message, 90)}");
}


Console.WriteLine();
Console.WriteLine("NetClient with TransportMode.BouncyH2 (store modules can opt into the own stack):");
try
{
    using var h2Client = new NetClient { Transport = TransportMode.BouncyH2 };
    var h2res = await h2Client.GetAsync($"https://{host}/", new RequestOptions { Timeout = TimeSpan.FromSeconds(15), Tag = "netclient-h2" });
    Console.WriteLine($"  NetClient/h2         HTTP {h2res.StatusCode}  {h2res.Protocol}  {h2res.Bytes} bytes  {h2res.Elapsed.TotalMilliseconds:0} ms");
}
catch (Exception ex)
{
    Console.WriteLine($"  NetClient/h2         request failed: {Trunc(ex.Message, 100)}");
}

try
{
    using var h11Client = new NetClient { Transport = TransportMode.BouncyHttp11 };
    var target11 = Environment.GetEnvironmentVariable("BC_HTTP_HOST") ?? "example.com";
    var r11 = await h11Client.GetAsync($"https://{target11}/", new RequestOptions { Timeout = TimeSpan.FromSeconds(15), Tag = "netclient-h11" });
    Console.WriteLine($"  NetClient/http1.1    HTTP {r11.StatusCode}  {r11.Protocol}  {r11.Bytes} bytes  {r11.Elapsed.TotalMilliseconds:0} ms  host={target11}");
}
catch (Exception ex)
{
    Console.WriteLine($"  NetClient/http1.1    request failed: {Trunc(ex.Message, 100)}");
}


Console.WriteLine();
Console.WriteLine("Header dump (h2 over BC TLS) — verifies HPACK Huffman decoding:");
try
{
    using var h2dump = new BouncyH2Client();
    var dumpTarget = Environment.GetEnvironmentVariable("BC_HTTP_HOST") ?? "example.com";
    var dr = await h2dump.GetAsync($"https://{dumpTarget}/", TlsProfile.Chrome, tag: "h2-dump");
    Console.WriteLine($"  {dumpTarget}: HTTP {dr.StatusCode}");
    foreach (var kv in dr.Headers.OrderBy(k => k.Key))
        Console.WriteLine($"    {kv.Key}: {Trunc(kv.Value, 70)}");
}
catch (Exception ex)
{
    Console.WriteLine($"  header dump failed: {Trunc(ex.Message, 100)}");
}

static string Trunc(string s, int n) => s.Length <= n ? s : s[..n];
