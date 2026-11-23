using System.Text;

namespace Cybersole.Http.Protocol;

/// <summary>
/// Buffered async stream reader with bounded line reading, single-byte lookahead,
/// exact-length reads, and lossless handoff of unread buffered bytes (e.g. after HTTP CONNECT).
/// </summary>
public sealed class BufferedStreamReader : IAsyncDisposable, IDisposable
{
    public const int DefaultBufferSize = 64 * 1024;

    private readonly Stream _stream;
    private readonly byte[] _buffer;
    private readonly bool _leaveOpen;
    private int _pos;
    private int _len;
    private long _totalBytesConsumed;
    private bool _disposed;

    public BufferedStreamReader(Stream stream, int bufferSize = DefaultBufferSize, bool leaveOpen = true)
    {
        ArgumentNullException.ThrowIfNull(stream);
        if (bufferSize <= 0)
            throw new ArgumentOutOfRangeException(nameof(bufferSize), "Buffer size must be positive.");

        _stream = stream;
        _buffer = new byte[bufferSize];
        _leaveOpen = leaveOpen;
    }

    public Stream BaseStream => _stream;

    public bool HasBufferedBytes => _pos < _len;

    public int BufferedCount => _len - _pos;

    public ReadOnlyMemory<byte> BufferedMemory => _buffer.AsMemory(_pos, _len - _pos);

    public long TotalBytesConsumed => _totalBytesConsumed;

    public async ValueTask<int> PeekByteAsync(CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (_pos < _len)
            return _buffer[_pos];

        int read = await FillBufferAsync(cancellationToken).ConfigureAwait(false);
        return read == 0 ? -1 : _buffer[_pos];
    }

    public async ValueTask<int> ReadByteAsync(CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (_pos >= _len)
        {
            int read = await FillBufferAsync(cancellationToken).ConfigureAwait(false);
            if (read == 0)
                return -1;
        }

        _totalBytesConsumed++;
        return _buffer[_pos++];
    }

    public async ValueTask<int> ReadUpToAsync(Memory<byte> destination, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        if (destination.IsEmpty)
            return 0;

        int buffered = _len - _pos;
        if (buffered > 0)
        {
            int take = Math.Min(buffered, destination.Length);
            _buffer.AsSpan(_pos, take).CopyTo(destination.Span);
            _pos += take;
            _totalBytesConsumed += take;
            if (_pos == _len)
            {
                _pos = 0;
                _len = 0;
            }
            return take;
        }

        if (destination.Length >= _buffer.Length)
        {
            int directRead = await _stream.ReadAsync(destination, cancellationToken).ConfigureAwait(false);
            _totalBytesConsumed += directRead;
            return directRead;
        }

        int filled = await FillBufferAsync(cancellationToken).ConfigureAwait(false);
        if (filled == 0)
            return 0;

        int copy = Math.Min(filled, destination.Length);
        _buffer.AsSpan(_pos, copy).CopyTo(destination.Span);
        _pos += copy;
        _totalBytesConsumed += copy;
        if (_pos == _len)
        {
            _pos = 0;
            _len = 0;
        }
        return copy;
    }

    public async ValueTask ReadExactAsync(Memory<byte> destination, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        while (!destination.IsEmpty)
        {
            int read = await ReadUpToAsync(destination, cancellationToken).ConfigureAwait(false);
            if (read == 0)
                throw new EndOfStreamException("Unexpected end of stream while reading exact bytes.");

            destination = destination[read..];
        }
    }

    /// <summary>
    /// Reads a CR/LF or LF terminated ASCII/Latin-1 line up to <paramref name="maxLineBytes"/>.
    /// Returns <see langword="null"/> on clean EOF at line start; throws <see cref="EndOfStreamException"/>
    /// on truncated EOF mid-line and <see cref="PureHttpException"/> (<see cref="HttpErrorKind.Protocol"/>)
    /// when line length exceeds <paramref name="maxLineBytes"/>.
    /// </summary>
    public async ValueTask<string?> ReadLineAsciiAsync(int maxLineBytes = DefaultBufferSize, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (maxLineBytes <= 0)
            throw new ArgumentOutOfRangeException(nameof(maxLineBytes), "maxLineBytes must be positive.");

        if (_pos >= _len)
        {
            int initialFill = await FillBufferAsync(cancellationToken).ConfigureAwait(false);
            if (initialFill == 0)
                return null;
        }

        int fastNl = Array.IndexOf(_buffer, (byte)'\n', _pos, _len - _pos);
        if (fastNl >= 0)
        {
            int consumed = fastNl - _pos + 1;
            if (consumed > maxLineBytes)
            {
                throw new PureHttpException(
                    HttpErrorKind.Protocol,
                    $"HTTP line exceeded maximum length of {maxLineBytes} bytes.");
            }

            int textLen = (fastNl > _pos && _buffer[fastNl - 1] == (byte)'\r')
                ? fastNl - _pos - 1
                : fastNl - _pos;

            string line = Encoding.Latin1.GetString(_buffer, _pos, textLen);
            _pos = fastNl + 1;
            _totalBytesConsumed += consumed;
            if (_pos == _len)
            {
                _pos = 0;
                _len = 0;
            }
            return line;
        }

        using var accum = new MemoryStream(256);
        while (true)
        {
            if (_pos >= _len)
            {
                int filled = await FillBufferAsync(cancellationToken).ConfigureAwait(false);
                if (filled == 0)
                {
                    if (accum.Length == 0)
                        return null;
                    throw new EndOfStreamException("Unexpected end of stream before line terminator.");
                }
            }

            int nlIdx = Array.IndexOf(_buffer, (byte)'\n', _pos, _len - _pos);
            if (nlIdx >= 0)
            {
                int partLen = nlIdx - _pos;
                long totalWithNl = accum.Length + partLen + 1;
                if (totalWithNl > maxLineBytes)
                {
                    throw new PureHttpException(
                        HttpErrorKind.Protocol,
                        $"HTTP line exceeded maximum length of {maxLineBytes} bytes.");
                }

                if (partLen > 0)
                    accum.Write(_buffer, _pos, partLen);

                _pos = nlIdx + 1;
                _totalBytesConsumed += partLen + 1;
                if (_pos == _len)
                {
                    _pos = 0;
                    _len = 0;
                }

                if (!accum.TryGetBuffer(out ArraySegment<byte> seg))
                    seg = new ArraySegment<byte>(accum.ToArray());

                int len = seg.Count;
                if (len > 0 && seg.Array![seg.Offset + len - 1] == (byte)'\r')
                    len--;

                return Encoding.Latin1.GetString(seg.Array!, seg.Offset, len);
            }

            int avail = _len - _pos;
            if (accum.Length + avail > maxLineBytes)
            {
                throw new PureHttpException(
                    HttpErrorKind.Protocol,
                    $"HTTP line exceeded maximum length of {maxLineBytes} bytes.");
            }

            accum.Write(_buffer, _pos, avail);
            _pos = 0;
            _len = 0;
            _totalBytesConsumed += avail;
        }
    }

    public byte[] TakeBufferedBytes()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        int count = _len - _pos;
        if (count <= 0)
            return Array.Empty<byte>();

        var copy = new byte[count];
        _buffer.AsSpan(_pos, count).CopyTo(copy);
        _pos = 0;
        _len = 0;
        return copy;
    }

    /// <summary>
    /// Returns a <see cref="Stream"/> yielding any unread buffered bytes followed seamlessly by the
    /// underlying stream (required when proxy CONNECT responses arrive coalesced with TLS handshake bytes).
    /// </summary>
    public Stream DetachRemainingStream(bool leaveInnerOpen = false)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        byte[] prefix = TakeBufferedBytes();
        if (prefix.Length == 0 && !leaveInnerOpen)
            return _stream;

        return new PrefixedStream(prefix, _stream, leaveInnerOpen);
    }

    private async ValueTask<int> FillBufferAsync(CancellationToken cancellationToken)
    {
        _pos = 0;
        _len = 0;
        int read = await _stream.ReadAsync(_buffer.AsMemory(), cancellationToken).ConfigureAwait(false);
        _len = read;
        return read;
    }

    public void Dispose()
    {
        if (_disposed)
            return;
        _disposed = true;
        if (!_leaveOpen)
            _stream.Dispose();
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
            return;
        _disposed = true;
        if (!_leaveOpen)
            await _stream.DisposeAsync().ConfigureAwait(false);
    }
}

/// <summary>
/// Full-duplex stream wrapper that replays an already-buffered byte prefix before delegating reads
/// to the underlying stream while forwarding all writes directly.
/// </summary>
public sealed class PrefixedStream : Stream
{
    private readonly byte[] _prefix;
    private readonly Stream _inner;
    private readonly bool _leaveInnerOpen;
    private int _prefixOffset;
    private bool _disposed;

    public PrefixedStream(byte[] prefix, Stream inner, bool leaveInnerOpen = false)
    {
        _prefix = prefix ?? throw new ArgumentNullException(nameof(prefix));
        _inner = inner ?? throw new ArgumentNullException(nameof(inner));
        _leaveInnerOpen = leaveInnerOpen;
    }

    public bool HasUnreadPrefix => _prefixOffset < _prefix.Length;

    public override bool CanRead => !_disposed && _inner.CanRead;
    public override bool CanSeek => false;
    public override bool CanWrite => !_disposed && _inner.CanWrite;
    public override long Length => throw new NotSupportedException();
    public override long Position
    {
        get => throw new NotSupportedException();
        set => throw new NotSupportedException();
    }

    public override int Read(byte[] buffer, int offset, int count)
    {
        ValidateBufferArguments(buffer, offset, count);
        return Read(buffer.AsSpan(offset, count));
    }

    public override int Read(Span<byte> buffer)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (buffer.IsEmpty)
            return 0;

        int remaining = _prefix.Length - _prefixOffset;
        if (remaining > 0)
        {
            int take = Math.Min(remaining, buffer.Length);
            _prefix.AsSpan(_prefixOffset, take).CopyTo(buffer);
            _prefixOffset += take;
            return take;
        }

        return _inner.Read(buffer);
    }

    public override Task<int> ReadAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
    {
        ValidateBufferArguments(buffer, offset, count);
        return ReadAsync(buffer.AsMemory(offset, count), cancellationToken).AsTask();
    }

    public override ValueTask<int> ReadAsync(Memory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (buffer.IsEmpty)
            return ValueTask.FromResult(0);

        int remaining = _prefix.Length - _prefixOffset;
        if (remaining > 0)
        {
            int take = Math.Min(remaining, buffer.Length);
            _prefix.AsSpan(_prefixOffset, take).CopyTo(buffer.Span);
            _prefixOffset += take;
            return ValueTask.FromResult(take);
        }

        return _inner.ReadAsync(buffer, cancellationToken);
    }

    public override void Write(byte[] buffer, int offset, int count)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        _inner.Write(buffer, offset, count);
    }

    public override void Write(ReadOnlySpan<byte> buffer)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        _inner.Write(buffer);
    }

    public override Task WriteAsync(byte[] buffer, int offset, int count, CancellationToken cancellationToken)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return _inner.WriteAsync(buffer, offset, count, cancellationToken);
    }

    public override ValueTask WriteAsync(ReadOnlyMemory<byte> buffer, CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return _inner.WriteAsync(buffer, cancellationToken);
    }

    public override void Flush()
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        _inner.Flush();
    }

    public override Task FlushAsync(CancellationToken cancellationToken)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        return _inner.FlushAsync(cancellationToken);
    }

    public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
    public override void SetLength(long value) => throw new NotSupportedException();

    protected override void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            _disposed = true;
            if (disposing && !_leaveInnerOpen)
                _inner.Dispose();
        }
        base.Dispose(disposing);
    }

    public override async ValueTask DisposeAsync()
    {
        if (!_disposed)
        {
            _disposed = true;
            if (!_leaveInnerOpen)
                await _inner.DisposeAsync().ConfigureAwait(false);
        }
        await base.DisposeAsync().ConfigureAwait(false);
    }
}
