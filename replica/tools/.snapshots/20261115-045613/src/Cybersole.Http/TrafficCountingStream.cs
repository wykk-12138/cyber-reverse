using Cybersole.Core.Models;

namespace Cybersole.Http;

/// <summary>
/// Wraps a proxy tunnel stream and accumulates per-proxy traffic counters
/// (<c>Proxy.TotalUpload</c> / <c>Proxy.TotalDownload</c>), flushing them back to the model on dispose.
/// </summary>
public sealed class TrafficCountingStream : Stream
{
    private readonly Stream _inner;
    private readonly Proxy _proxy;
    private long _read;
    private long _written;

    public TrafficCountingStream(Stream inner, Proxy proxy)
    {
        _inner = inner;
        _proxy = proxy;
    }

    public long BytesRead => Interlocked.Read(ref _read);
    public long BytesWritten => Interlocked.Read(ref _written);

    public override bool CanRead => _inner.CanRead;
    public override bool CanSeek => false;
    public override bool CanWrite => _inner.CanWrite;
    public override long Length => throw new NotSupportedException();
    public override long Position
    {
        get => throw new NotSupportedException();
        set => throw new NotSupportedException();
    }

    public override int Read(byte[] buffer, int offset, int count)
    {
        var read = _inner.Read(buffer, offset, count);
        Interlocked.Add(ref _read, read);
        return read;
    }

    public override async Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken ct)
    {
        var read = await _inner.ReadAsync(buffer, offset, count, ct).ConfigureAwait(false);
        Interlocked.Add(ref _read, read);
        return read;
    }

    public override async ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken ct = default)
    {
        var read = await _inner.ReadAsync(buffer, ct).ConfigureAwait(false);
        Interlocked.Add(ref _read, read);
        return read;
    }

    public override void Write(byte[] buffer, int offset, int count)
    {
        _inner.Write(buffer, offset, count);
        Interlocked.Add(ref _written, count);
    }

    public override async Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken ct)
    {
        await _inner.WriteAsync(buffer, offset, count, ct).ConfigureAwait(false);
        Interlocked.Add(ref _written, count);
    }

    public override async ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken ct = default)
    {
        await _inner.WriteAsync(buffer, ct).ConfigureAwait(false);
        Interlocked.Add(ref _written, buffer.Length);
    }

    public override void Flush() => _inner.Flush();
    public override Task FlushAsync(CancellationToken ct) => _inner.FlushAsync(ct);
    public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
    public override void SetLength(long value) => throw new NotSupportedException();

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            _proxy.TotalDownload += BytesRead;
            _proxy.TotalUpload += BytesWritten;
            _inner.Dispose();
        }

        base.Dispose(disposing);
    }
}
