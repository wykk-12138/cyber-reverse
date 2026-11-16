using System.Net;
using System.Net.Sockets;
using System.Text;
using Cybersole.Core.Models;

namespace Cybersole.Http;

/// <summary>Selects the next proxy from a group according to its behaviour.</summary>
public sealed class ProxyRotator
{
    private readonly ProxyGroup _group;
    private readonly Random _random = new();
    private int _index;
    private readonly Dictionary<string, int> _usage = new();

    public ProxyRotator(ProxyGroup group) => _group = group;

    public Proxy? Next()
    {
        // proxyGroup.maxUsage: stop handing out proxies that already hit their budget
        var budget = _group.MaxUsage;
        var pool = _group.Proxies
            .Where(p => p.Enabled())
            .Where(p => budget <= 0 || p.Usage < budget)
            .ToList();

        if (pool.Count == 0) return null;

        return _group.Behaviour switch
        {
            ProxyGroupBehaviour.Random => pool[_random.Next(pool.Count)],
            ProxyGroupBehaviour.LeastUsed => pool.OrderBy(p => p.Usage).ThenBy(p => _usage.GetValueOrDefault(p.Id)).First(),
            _ => pool[Interlocked.Increment(ref _index) % pool.Count],
        };
    }

    public void MarkUsed(Proxy proxy)
    {
        proxy.Usage++;                                   // persisted usage counter
        _usage[proxy.Id] = _usage.GetValueOrDefault(proxy.Id) + 1;
    }

    /// <summary>Proxies still under budget (diagnostics / proxy page).</summary>
    public IReadOnlyList<Proxy> Available()
    {
        var budget = _group.MaxUsage;
        return _group.Proxies.Where(p => budget <= 0 || p.Usage < budget).ToList();
    }

    public void MarkStatus(Proxy proxy, bool ok)
        => proxy.Status = ok ? Status.Running : Status.Failed;
}

internal static class ProxyExtensions
{
    public static bool Enabled(this Proxy proxy) => true;
}

/// <summary>Minimal SOCKS5 / HTTP CONNECT plumbing used by the NetClient connect callback.</summary>
public static class ProxyConnector
{
    public static async Task<Stream> ConnectAsync(Proxy proxy, string host, int port, CancellationToken ct)
    {
        var tcp = new TcpClient();
        await tcp.ConnectAsync(proxy.Host, proxy.Port, ct).ConfigureAwait(false);
        var stream = tcp.GetStream();

        if (proxy.Scheme.StartsWith("socks", StringComparison.OrdinalIgnoreCase))
            await Socks5HandshakeAsync(stream, proxy, host, port, ct).ConfigureAwait(false);
        else
            await HttpConnectAsync(stream, proxy, host, port, ct).ConfigureAwait(false);

        // per-proxy traffic is written back on dispose (proxy.totalUpload / totalDownload)
        return new TrafficCountingStream(stream, proxy);
    }

    private static async Task HttpConnectAsync(Stream stream, Proxy proxy, string host, int port, CancellationToken ct)
    {
        var auth = string.IsNullOrEmpty(proxy.Username)
            ? string.Empty
            : $"Proxy-Authorization: Basic {Convert.ToBase64String(Encoding.UTF8.GetBytes($"{proxy.Username}:{proxy.Password}"))}\r\n";
        var request = $"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n{auth}\r\n";
        var bytes = Encoding.ASCII.GetBytes(request);
        await stream.WriteAsync(bytes, ct).ConfigureAwait(false);

        var buffer = new byte[1024];
        var read = await stream.ReadAsync(buffer, ct).ConfigureAwait(false);
        var text = Encoding.ASCII.GetString(buffer, 0, read);
        if (!text.StartsWith("HTTP/1.1 200", StringComparison.OrdinalIgnoreCase) &&
            !text.StartsWith("HTTP/1.0 200", StringComparison.OrdinalIgnoreCase))
            throw new NetException($"proxy CONNECT rejected: {text.Split('\r')[0]}");
    }

    private static async Task Socks5HandshakeAsync(Stream stream, Proxy proxy, string host, int port, CancellationToken ct)
    {
        var greeting = string.IsNullOrEmpty(proxy.Username)
            ? new byte[] { 0x05, 0x01, 0x00 }
            : new byte[] { 0x05, 0x02, 0x00, 0x02 };
        await stream.WriteAsync(greeting, ct).ConfigureAwait(false);

        var resp = new byte[2];
        await stream.ReadExactlyAsync(resp, ct).ConfigureAwait(false);
        if (resp[0] != 0x05) throw new NetException("socks5: bad version");

        if (resp[1] == 0x02)
        {
            var user = Encoding.UTF8.GetBytes(proxy.Username ?? string.Empty);
            var pass = Encoding.UTF8.GetBytes(proxy.Password ?? string.Empty);
            var auth = new byte[3 + user.Length + pass.Length];
            auth[0] = 0x01;
            auth[1] = (byte)user.Length;
            user.CopyTo(auth, 2);
            auth[2 + user.Length] = (byte)pass.Length;
            pass.CopyTo(auth, 3 + user.Length);
            await stream.WriteAsync(auth, ct).ConfigureAwait(false);
            await stream.ReadExactlyAsync(resp, ct).ConfigureAwait(false);
            if (resp[1] != 0x00) throw new NetException("socks5: auth failed");
        }

        var hostBytes = Encoding.ASCII.GetBytes(host);
        var request = new byte[7 + hostBytes.Length];
        request[0] = 0x05; request[1] = 0x01; request[2] = 0x00; request[3] = 0x03;
        request[4] = (byte)hostBytes.Length;
        hostBytes.CopyTo(request, 5);
        request[5 + hostBytes.Length] = (byte)(port >> 8);
        request[6 + hostBytes.Length] = (byte)(port & 0xFF);
        await stream.WriteAsync(request, ct).ConfigureAwait(false);

        var head = new byte[4];
        await stream.ReadExactlyAsync(head, ct).ConfigureAwait(false);
        if (head[1] != 0x00) throw new NetException($"socks5: connect failed (code {head[1]})");
        var addrLen = head[3] switch { 0x01 => 4, 0x04 => 16, 0x03 => (byte)0, _ => 0 };
        if (addrLen == 0x00)
        {
            var l = new byte[1];
            await stream.ReadExactlyAsync(l, ct).ConfigureAwait(false);
            addrLen = l[0];
        }
        var tail = new byte[addrLen + 2];
        await stream.ReadExactlyAsync(tail, ct).ConfigureAwait(false);
    }
}
