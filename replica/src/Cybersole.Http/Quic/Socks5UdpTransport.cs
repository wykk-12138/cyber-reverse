using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Channels;
using Cybersole.Http.Protocol;

namespace Cybersole.Http.Quic;

/// <summary>Abstract bidirectional QUIC UDP datagram transport.</summary>
public interface IQuicDatagramTransport : IAsyncDisposable
{
    EndPoint? RemoteEndPoint { get; }
    ValueTask SendDatagramAsync(ReadOnlyMemory<byte> datagram, CancellationToken cancellationToken = default);
    ValueTask<int> ReceiveDatagramAsync(Memory<byte> buffer, CancellationToken cancellationToken = default);
}

/// <summary>30s TTL DNS cache matching <c>DnsCache</c> (<c>0x1412C39C0</c>).</summary>
public sealed class QuicDnsCache
{
    public const int MaxEntries = 4096;
    public static readonly TimeSpan DefaultTtl = TimeSpan.FromSeconds(30);

    private sealed record CacheEntry(IPAddress[] Addresses, DateTimeOffset ExpiresAtUtc);

    private readonly ConcurrentDictionary<string, CacheEntry> _cache = new(StringComparer.OrdinalIgnoreCase);
    private readonly TimeSpan _ttl;
    private readonly Func<DateTimeOffset> _clock;
    private readonly Func<string, CancellationToken, ValueTask<IPAddress[]>> _resolver;

    public QuicDnsCache(
        TimeSpan? ttl = null,
        Func<DateTimeOffset>? clock = null,
        Func<string, CancellationToken, ValueTask<IPAddress[]>>? resolver = null)
    {
        _ttl = ttl ?? DefaultTtl;
        _clock = clock ?? (() => DateTimeOffset.UtcNow);
        _resolver = resolver ?? DefaultResolveAsync;
    }

    public int Count => _cache.Count;

    public async ValueTask<IPAddress[]> ResolveAsync(string host, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(host);

        string normalized = host.Trim();
        if (normalized.StartsWith('[') && normalized.EndsWith(']') && normalized.Length >= 2)
            normalized = normalized[1..^1];

        if (IPAddress.TryParse(normalized, out IPAddress? literal))
            return new[] { literal };

        DateTimeOffset now = _clock();
        if (_cache.TryGetValue(normalized, out CacheEntry? existing) && existing.ExpiresAtUtc > now)
            return existing.Addresses;

        IPAddress[] resolved = await _resolver(normalized, cancellationToken).ConfigureAwait(false);
        if (resolved.Length == 0)
            throw new SocketException((int)SocketError.HostNotFound);

        if (_cache.Count >= MaxEntries)
            PruneOrClear(now);

        _cache[normalized] = new CacheEntry(resolved, now + _ttl);
        return resolved;
    }

    public void Clear() => _cache.Clear();

    private void PruneOrClear(DateTimeOffset now)
    {
        foreach (KeyValuePair<string, CacheEntry> kv in _cache)
        {
            if (kv.Value.ExpiresAtUtc <= now)
                _cache.TryRemove(kv.Key, out _);
        }

        if (_cache.Count >= MaxEntries)
            _cache.Clear();
    }

    private static async ValueTask<IPAddress[]> DefaultResolveAsync(string host, CancellationToken ct) =>
        await Dns.GetHostAddressesAsync(host, ct).ConfigureAwait(false);
}

/// <summary>Direct OS UDP socket transport for QUIC.</summary>
public sealed class DirectUdpTransport : IQuicDatagramTransport
{
    private readonly Socket _socket;
    private int _disposed;

    public DirectUdpTransport(Socket connectedSocket)
    {
        _socket = connectedSocket ?? throw new ArgumentNullException(nameof(connectedSocket));
        RemoteEndPoint = connectedSocket.RemoteEndPoint;
    }

    public EndPoint? RemoteEndPoint { get; }

    public static async Task<DirectUdpTransport> ConnectAsync(
        string host,
        int port,
        QuicDnsCache? dnsCache = null,
        CancellationToken cancellationToken = default)
    {
        QuicDnsCache cache = dnsCache ?? new QuicDnsCache();
        IPAddress[] addrs = await cache.ResolveAsync(host, cancellationToken).ConfigureAwait(false);

        SocketException? lastError = null;
        foreach (IPAddress ip in OrderAddressesPreferIPv4(addrs))
        {
            var sock = new Socket(ip.AddressFamily, SocketType.Dgram, ProtocolType.Udp);
            try
            {
                sock.ReceiveBufferSize = 1024 * 1024;
                sock.SendBufferSize = 1024 * 1024;
                await sock.ConnectAsync(new IPEndPoint(ip, port), cancellationToken).ConfigureAwait(false);
                return new DirectUdpTransport(sock);
            }
            catch (SocketException ex)
            {
                lastError = ex;
                sock.Dispose();
            }
        }

        throw lastError ?? new SocketException((int)SocketError.HostNotFound);
    }

    private static IEnumerable<IPAddress> OrderAddressesPreferIPv4(IPAddress[] addrs)
    {
        for (int i = 0; i < addrs.Length; i++)
        {
            if (addrs[i].AddressFamily == AddressFamily.InterNetwork)
                yield return addrs[i];
        }
        for (int i = 0; i < addrs.Length; i++)
        {
            if (addrs[i].AddressFamily != AddressFamily.InterNetwork)
                yield return addrs[i];
        }
    }

    public async ValueTask SendDatagramAsync(ReadOnlyMemory<byte> datagram, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(Volatile.Read(ref _disposed) != 0, this);
        await _socket.SendAsync(datagram, SocketFlags.None, cancellationToken).ConfigureAwait(false);
    }

    public async ValueTask<int> ReceiveDatagramAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(Volatile.Read(ref _disposed) != 0, this);
        return await _socket.ReceiveAsync(buffer, SocketFlags.None, cancellationToken).ConfigureAwait(false);
    }

    public ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) == 0)
            _socket.Dispose();
        return ValueTask.CompletedTask;
    }
}

/// <summary>
/// RFC 1928 SOCKS5 UDP ASSOCIATE transport matching <c>Socks5UdpTransport</c> (<c>0x14133DB90</c>):
/// keeps the TCP control socket open, uses a 66,048-byte UDP receive buffer, resolves target origins
/// via a 30s TTL DNS cache, and frames datagrams with <c>[RSV(2)=0, FRAG(1)=0, ATYP, DST.ADDR, DST.PORT_be]</c>.
/// </summary>
public sealed class Socks5UdpTransport : IQuicDatagramTransport
{
    public const int UdpBufferSize = 66_048;
    public static readonly TimeSpan DefaultDnsCacheTtl = QuicDnsCache.DefaultTtl;

    private readonly Socket _tcpControlSocket;
    private readonly Socket _udpSocket;
    private readonly string _targetHost;
    private readonly int _targetPort;
    private readonly QuicDnsCache _dnsCache;
    private readonly byte[] _recvBuffer;
    private readonly byte[] _sendScratch;
    private readonly SemaphoreSlim _sendLock = new(1, 1);
    private int _disposed;

    private Socks5UdpTransport(
        Socket tcpControlSocket,
        Socket udpSocket,
        IPEndPoint relayEndPoint,
        string targetHost,
        int targetPort,
        QuicDnsCache dnsCache)
    {
        _tcpControlSocket = tcpControlSocket;
        _udpSocket = udpSocket;
        RelayEndPoint = relayEndPoint;
        _targetHost = targetHost;
        _targetPort = targetPort;
        _dnsCache = dnsCache;
        _recvBuffer = new byte[UdpBufferSize];
        _sendScratch = new byte[UdpBufferSize];
    }

    public IPEndPoint RelayEndPoint { get; }
    public EndPoint? RemoteEndPoint => RelayEndPoint;
    public int ReceiveBufferLength => _recvBuffer.Length;

    public static async Task<Socks5UdpTransport> ConnectAsync(
        ProxySpec proxy,
        string targetHost,
        int targetPort,
        QuicDnsCache? dnsCache = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(proxy);
        ArgumentException.ThrowIfNullOrWhiteSpace(targetHost);
        if (proxy.Kind != ProxyProtocolKind.Socks5)
            throw new ProxyException($"SOCKS5 UDP transport requires a socks5/socks5h proxy, got {proxy.Kind}.");

        QuicDnsCache cache = dnsCache ?? new QuicDnsCache();
        IPAddress[] proxyAddrs = await cache.ResolveAsync(proxy.Host, cancellationToken).ConfigureAwait(false);

        Socket? tcp = null;
        SocketException? lastConnectErr = null;
        foreach (IPAddress ip in proxyAddrs)
        {
            var candidate = new Socket(ip.AddressFamily, SocketType.Stream, ProtocolType.Tcp)
            {
                NoDelay = true,
            };
            try
            {
                await candidate.ConnectAsync(new IPEndPoint(ip, proxy.Port), cancellationToken).ConfigureAwait(false);
                tcp = candidate;
                break;
            }
            catch (SocketException ex)
            {
                lastConnectErr = ex;
                candidate.Dispose();
            }
        }

        if (tcp is null)
            throw new ProxyException($"Failed to connect to SOCKS5 proxy {proxy.Host}:{proxy.Port}.", lastConnectErr);

        try
        {
            bool hasAuth = !string.IsNullOrEmpty(proxy.Username) || !string.IsNullOrEmpty(proxy.Password);
            byte[] greeting = hasAuth
                ? new byte[] { 0x05, 0x02, 0x00, 0x02 }
                : new byte[] { 0x05, 0x01, 0x00 };
            await SendAllTcpAsync(tcp, greeting, cancellationToken).ConfigureAwait(false);

            var methodReply = new byte[2];
            await ReadExactTcpAsync(tcp, methodReply, cancellationToken).ConfigureAwait(false);
            if (methodReply[0] != 0x05)
                throw new ProxyException($"socks5: invalid greeting version 0x{methodReply[0]:X2}");

            if (methodReply[1] == 0x02)
            {
                if (!hasAuth)
                    throw new ProxyException("socks5: server requested username/password auth but no credentials were supplied");

                byte[] userBytes = Encoding.UTF8.GetBytes(proxy.Username ?? string.Empty);
                byte[] passBytes = Encoding.UTF8.GetBytes(proxy.Password ?? string.Empty);
                if (userBytes.Length > 255 || passBytes.Length > 255)
                    throw new ProxyException("socks5: username/password exceeds 255 bytes");

                var authReq = new byte[3 + userBytes.Length + passBytes.Length];
                authReq[0] = 0x01;
                authReq[1] = (byte)userBytes.Length;
                userBytes.CopyTo(authReq, 2);
                authReq[2 + userBytes.Length] = (byte)passBytes.Length;
                passBytes.CopyTo(authReq, 3 + userBytes.Length);
                await SendAllTcpAsync(tcp, authReq, cancellationToken).ConfigureAwait(false);

                var authReply = new byte[2];
                await ReadExactTcpAsync(tcp, authReply, cancellationToken).ConfigureAwait(false);
                if (authReply[1] != 0x00)
                    throw new ProxyException($"socks5: username/password authentication failed (status=0x{authReply[1]:X2})");
            }
            else if (methodReply[1] != 0x00)
            {
                throw new ProxyException($"socks5: unsupported auth method 0x{methodReply[1]:X2}");
            }

            // Send UDP ASSOCIATE (CMD = 0x03) with unspecified local address/port.
            bool isV6 = tcp.AddressFamily == AddressFamily.InterNetworkV6;
            byte[] assocReq = isV6
                ? new byte[]
                {
                    0x05, 0x03, 0x00, 0x04,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0x00, 0x00,
                }
                : new byte[] { 0x05, 0x03, 0x00, 0x01, 0, 0, 0, 0, 0x00, 0x00 };
            await SendAllTcpAsync(tcp, assocReq, cancellationToken).ConfigureAwait(false);

            var replyHdr = new byte[4];
            await ReadExactTcpAsync(tcp, replyHdr, cancellationToken).ConfigureAwait(false);
            if (replyHdr[0] != 0x05)
                throw new ProxyException($"socks5: invalid UDP ASSOCIATE reply version 0x{replyHdr[0]:X2}");
            if (replyHdr[1] != 0x00)
                throw new ProxyException($"socks5: UDP ASSOCIATE failed with reply code 0x{replyHdr[1]:X2}");

            byte atyp = replyHdr[3];
            if (atyp == 0x03)
                throw new ProxyException("socks5: UDP ASSOCIATE returned a domain name relay address");

            IPAddress relayIp;
            if (atyp == 0x01)
            {
                var ip4 = new byte[4];
                await ReadExactTcpAsync(tcp, ip4, cancellationToken).ConfigureAwait(false);
                relayIp = new IPAddress(ip4);
            }
            else if (atyp == 0x04)
            {
                var ip6 = new byte[16];
                await ReadExactTcpAsync(tcp, ip6, cancellationToken).ConfigureAwait(false);
                relayIp = new IPAddress(ip6);
            }
            else
            {
                throw new ProxyException($"socks5: UDP ASSOCIATE returned unknown ATYP 0x{atyp:X2}");
            }

            var portBuf = new byte[2];
            await ReadExactTcpAsync(tcp, portBuf, cancellationToken).ConfigureAwait(false);
            ushort relayPort = BinaryPrimitives.ReadUInt16BigEndian(portBuf);
            if (relayPort == 0)
                throw new ProxyException("socks5: UDP ASSOCIATE returned port 0");

            if (relayIp.Equals(IPAddress.Any) || relayIp.Equals(IPAddress.IPv6Any))
                relayIp = ((IPEndPoint)tcp.RemoteEndPoint!).Address;

            var relayEp = new IPEndPoint(relayIp, relayPort);
            var udp = new Socket(relayIp.AddressFamily, SocketType.Dgram, ProtocolType.Udp);
            try
            {
                udp.ReceiveBufferSize = 1024 * 1024;
                udp.SendBufferSize = 1024 * 1024;
                await udp.ConnectAsync(relayEp, cancellationToken).ConfigureAwait(false);
            }
            catch
            {
                udp.Dispose();
                throw;
            }

            return new Socks5UdpTransport(tcp, udp, relayEp, targetHost, targetPort, cache);
        }
        catch
        {
            tcp.Dispose();
            throw;
        }
    }

    public async ValueTask SendDatagramAsync(ReadOnlyMemory<byte> datagram, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(Volatile.Read(ref _disposed) != 0, this);

        IPAddress[] addrs = await _dnsCache.ResolveAsync(_targetHost, cancellationToken).ConfigureAwait(false);
        IPAddress targetIp = SelectTargetAddress(addrs, _udpSocket.AddressFamily);

        await _sendLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            int totalLen = FrameOutboundDatagram(targetIp, datagram.Span);
            await _udpSocket.SendAsync(_sendScratch.AsMemory(0, totalLen), SocketFlags.None, cancellationToken).ConfigureAwait(false);
        }
        finally
        {
            _sendLock.Release();
        }
    }

    private int FrameOutboundDatagram(IPAddress targetIp, ReadOnlySpan<byte> datagram)
    {
        int hdrLen = EncodeUdpHeader(targetIp, _targetPort, _sendScratch);
        if (hdrLen + datagram.Length > _sendScratch.Length)
            throw new ArgumentOutOfRangeException(nameof(datagram), "Encapsulated SOCKS5 UDP datagram exceeds buffer size.");

        datagram.CopyTo(_sendScratch.AsSpan(hdrLen));
        return hdrLen + datagram.Length;
    }

    public async ValueTask<int> ReceiveDatagramAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(Volatile.Read(ref _disposed) != 0, this);

        while (true)
        {
            int received = await _udpSocket.ReceiveAsync(_recvBuffer.AsMemory(), SocketFlags.None, cancellationToken).ConfigureAwait(false);
            if (received == 0)
                return 0;

            if (TryCopyDecodedPayload(received, buffer.Span, out int copyLen))
                return copyLen;
        }
    }

    private bool TryCopyDecodedPayload(int receivedBytes, Span<byte> destination, out int copiedLength)
    {
        if (TryDecodeUdpPacket(_recvBuffer.AsSpan(0, receivedBytes), out _, out _, out ReadOnlySpan<byte> payload))
        {
            copiedLength = Math.Min(destination.Length, payload.Length);
            payload.Slice(0, copiedLength).CopyTo(destination);
            return true;
        }
        copiedLength = 0;
        return false;
    }

    public static int EncodeUdpHeader(IPAddress targetIp, int targetPort, Span<byte> destination)
    {
        ArgumentNullException.ThrowIfNull(targetIp);
        if (targetIp.AddressFamily == AddressFamily.InterNetwork)
        {
            if (destination.Length < 10)
                throw new ArgumentException("Destination too small for IPv4 SOCKS5 UDP header.", nameof(destination));
            destination[0] = 0x00;
            destination[1] = 0x00;
            destination[2] = 0x00; // FRAG = 0
            destination[3] = 0x01; // ATYP = IPv4
            targetIp.TryWriteBytes(destination.Slice(4, 4), out _);
            BinaryPrimitives.WriteUInt16BigEndian(destination.Slice(8, 2), (ushort)targetPort);
            return 10;
        }

        if (targetIp.AddressFamily == AddressFamily.InterNetworkV6)
        {
            if (destination.Length < 22)
                throw new ArgumentException("Destination too small for IPv6 SOCKS5 UDP header.", nameof(destination));
            destination[0] = 0x00;
            destination[1] = 0x00;
            destination[2] = 0x00; // FRAG = 0
            destination[3] = 0x04; // ATYP = IPv6
            targetIp.TryWriteBytes(destination.Slice(4, 16), out _);
            BinaryPrimitives.WriteUInt16BigEndian(destination.Slice(20, 2), (ushort)targetPort);
            return 22;
        }

        throw new ArgumentException($"Unsupported address family {targetIp.AddressFamily}.", nameof(targetIp));
    }

    public static bool TryDecodeUdpPacket(
        ReadOnlySpan<byte> packet,
        out string address,
        out int port,
        out ReadOnlySpan<byte> payload)
    {
        address = string.Empty;
        port = 0;
        payload = default;

        if (packet.Length < 4 || packet[0] != 0x00 || packet[1] != 0x00 || packet[2] != 0x00)
            return false;

        byte atyp = packet[3];
        int offset = 4;

        switch (atyp)
        {
            case 0x01:
                if (packet.Length < offset + 4 + 2)
                    return false;
                address = new IPAddress(packet.Slice(offset, 4)).ToString();
                offset += 4;
                break;

            case 0x03:
                if (packet.Length < offset + 1)
                    return false;
                byte hostLen = packet[offset++];
                if (packet.Length < offset + hostLen + 2)
                    return false;
                address = Encoding.UTF8.GetString(packet.Slice(offset, hostLen));
                offset += hostLen;
                break;

            case 0x04:
                if (packet.Length < offset + 16 + 2)
                    return false;
                address = new IPAddress(packet.Slice(offset, 16)).ToString();
                offset += 16;
                break;

            default:
                return false;
        }

        port = BinaryPrimitives.ReadUInt16BigEndian(packet.Slice(offset, 2));
        offset += 2;
        payload = packet.Slice(offset);
        return true;
    }

    private static IPAddress SelectTargetAddress(IPAddress[] addresses, AddressFamily preferredFamily)
    {
        for (int i = 0; i < addresses.Length; i++)
        {
            if (addresses[i].AddressFamily == preferredFamily)
                return addresses[i];
        }
        return addresses[0];
    }

    private static async Task SendAllTcpAsync(Socket sock, byte[] data, CancellationToken ct)
    {
        int sent = 0;
        while (sent < data.Length)
        {
            int n = await sock.SendAsync(data.AsMemory(sent), SocketFlags.None, ct).ConfigureAwait(false);
            if (n == 0)
                throw new EndOfStreamException("SOCKS5 TCP control channel closed unexpectedly.");
            sent += n;
        }
    }

    private static async Task ReadExactTcpAsync(Socket sock, byte[] buffer, CancellationToken ct)
    {
        int read = 0;
        while (read < buffer.Length)
        {
            int n = await sock.ReceiveAsync(buffer.AsMemory(read), SocketFlags.None, ct).ConfigureAwait(false);
            if (n == 0)
                throw new EndOfStreamException("SOCKS5 TCP control channel closed before completing handshake.");
            read += n;
        }
    }

    public ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) == 0)
        {
            _udpSocket.Dispose();
            _tcpControlSocket.Dispose();
            _sendLock.Dispose();
        }
        return ValueTask.CompletedTask;
    }
}

/// <summary>
/// Deterministic in-memory bidirectional UDP transport pair for QUIC &amp; HTTP/3 loopback tests.
/// </summary>
public sealed class LoopbackQuicTransportPair : IAsyncDisposable
{
    private sealed class EndpointTransport : IQuicDatagramTransport
    {
        private readonly ChannelReader<byte[]> _rx;
        private readonly ChannelWriter<byte[]> _tx;
        private readonly Action<byte[]>? _onSend;
        private int _disposed;

        public EndpointTransport(
            EndPoint remoteEndPoint,
            ChannelReader<byte[]> rx,
            ChannelWriter<byte[]> tx,
            Action<byte[]>? onSend)
        {
            RemoteEndPoint = remoteEndPoint;
            _rx = rx;
            _tx = tx;
            _onSend = onSend;
        }

        public EndPoint? RemoteEndPoint { get; }

        public ValueTask SendDatagramAsync(ReadOnlyMemory<byte> datagram, CancellationToken cancellationToken = default)
        {
            if (Volatile.Read(ref _disposed) != 0)
                return ValueTask.CompletedTask;
            byte[] copy = datagram.ToArray();
            _onSend?.Invoke(copy);
            _tx.TryWrite(copy);
            return ValueTask.CompletedTask;
        }

        public async ValueTask<int> ReceiveDatagramAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
        {
            if (!await _rx.WaitToReadAsync(cancellationToken).ConfigureAwait(false))
                return 0;
            if (!_rx.TryRead(out byte[]? msg))
                return 0;
            int copyLen = Math.Min(buffer.Length, msg.Length);
            msg.AsSpan(0, copyLen).CopyTo(buffer.Span);
            return copyLen;
        }

        public ValueTask DisposeAsync()
        {
            if (Interlocked.Exchange(ref _disposed, 1) == 0)
                _tx.TryComplete();
            return ValueTask.CompletedTask;
        }
    }

    private readonly Channel<byte[]> _c2s = Channel.CreateUnbounded<byte[]>(new UnboundedChannelOptions { SingleReader = false, SingleWriter = false });
    private readonly Channel<byte[]> _s2c = Channel.CreateUnbounded<byte[]>(new UnboundedChannelOptions { SingleReader = false, SingleWriter = false });

    public LoopbackQuicTransportPair(Action<byte[]>? onClientSend = null, Action<byte[]>? onServerSend = null)
    {
        Client = new EndpointTransport(new IPEndPoint(IPAddress.Loopback, 443), _s2c.Reader, _c2s.Writer, onClientSend);
        Server = new EndpointTransport(new IPEndPoint(IPAddress.Loopback, 50000), _c2s.Reader, _s2c.Writer, onServerSend);
    }

    public IQuicDatagramTransport Client { get; }
    public IQuicDatagramTransport Server { get; }

    public async ValueTask DisposeAsync()
    {
        await Client.DisposeAsync().ConfigureAwait(false);
        await Server.DisposeAsync().ConfigureAwait(false);
    }
}
