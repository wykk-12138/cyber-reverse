using System.Buffers;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Cybersole.Http.Content;

/// <summary>
/// Streaming HTTP request body abstraction (<c>Cybersole.Http.Content.IBody</c>),
/// matching the binary's <c>ContentType</c> / <c>SizeHint</c> / <c>WriteTo(IBufferWriter&lt;byte&gt;)</c> contract.
/// </summary>
public interface IBody
{
    string ContentType { get; }
    int? SizeHint { get; }
    void WriteTo(IBufferWriter<byte> writer);
}

/// <summary>Raw memory request body with a fast-path slice accessor to avoid redundant buffer copies.</summary>
public sealed class BytesBody : IBody
{
    private readonly ReadOnlyMemory<byte> _bytes;

    public BytesBody(ReadOnlyMemory<byte> bytes, string contentType = "application/octet-stream")
    {
        _bytes = bytes;
        ContentType = string.IsNullOrWhiteSpace(contentType) ? "application/octet-stream" : contentType;
    }

    public string ContentType { get; }
    public int? SizeHint => _bytes.Length;
    public ReadOnlyMemory<byte> Memory => _bytes;

    public void WriteTo(IBufferWriter<byte> writer)
    {
        if (!_bytes.IsEmpty)
            writer.Write(_bytes.Span);
    }
}

/// <summary>Encoded text body defaulting to UTF-8 without BOM.</summary>
public sealed class StringBody : IBody
{
    private static readonly Encoding Utf8NoBom = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
    private readonly string _text;
    private readonly Encoding _encoding;

    public StringBody(string? text, string contentType = "text/plain; charset=utf-8", Encoding? encoding = null)
    {
        _text = text ?? string.Empty;
        ContentType = string.IsNullOrWhiteSpace(contentType) ? "text/plain; charset=utf-8" : contentType;
        _encoding = encoding ?? Utf8NoBom;
    }

    public string ContentType { get; }
    public int? SizeHint => _encoding.GetByteCount(_text);

    public void WriteTo(IBufferWriter<byte> writer)
    {
        if (_text.Length == 0) return;
        var maxBytes = _encoding.GetMaxByteCount(_text.Length);
        var span = writer.GetSpan(maxBytes);
        var written = _encoding.GetBytes(_text.AsSpan(), span);
        writer.Advance(written);
    }
}

internal static class JsonBodyWriter
{
    private static readonly Encoding Utf8NoBom = new UTF8Encoding(encoderShouldEmitUTF8Identifier: false);
    private static readonly byte[] NullLiteral = "null"u8.ToArray();
    private static readonly JsonSerializer DefaultSerializer = new() { Formatting = Formatting.None };

    public static void Write(IBufferWriter<byte> writer, JToken? token, JsonSerializer? serializer)
    {
        if (token is null)
        {
            writer.Write(NullLiteral);
            return;
        }

        using var bufferStream = new BufferWriterStream(writer);
        using var streamWriter = new StreamWriter(bufferStream, Utf8NoBom, bufferSize: 1024, leaveOpen: true);
        using var jsonWriter = new JsonTextWriter(streamWriter)
        {
            Formatting = Formatting.None,
            CloseOutput = false,
        };
        (serializer ?? DefaultSerializer).Serialize(jsonWriter, token);
        jsonWriter.Flush();
        streamWriter.Flush();
    }

    private sealed class BufferWriterStream : Stream
    {
        private readonly IBufferWriter<byte> _writer;
        public BufferWriterStream(IBufferWriter<byte> writer) => _writer = writer;
        public override bool CanRead => false;
        public override bool CanSeek => false;
        public override bool CanWrite => true;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override int Read(byte[] buffer, int offset, int count) => throw new NotSupportedException();
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count)
        {
            if (count > 0)
                _writer.Write(buffer.AsSpan(offset, count));
        }
        public override void Write(ReadOnlySpan<byte> buffer)
        {
            if (!buffer.IsEmpty)
                _writer.Write(buffer);
        }
    }
}

/// <summary>
/// Newtonsoft <see cref="JToken"/> JSON body (<c>Cybersole.Http.Content.LegacyJsonBody</c>).
/// Defaults to an empty <see cref="JObject"/> and throws <see cref="InvalidOperationException"/>
/// on object indexer/mutation access when holding a non-object token.
/// </summary>
public sealed class LegacyJsonBody : IBody
{
    private readonly JsonSerializer? _serializer;

    public LegacyJsonBody(JsonSerializer? serializer = null)
        : this(new JObject(), serializer)
    {
    }

    public LegacyJsonBody(JToken? token, JsonSerializer? serializer = null)
    {
        Token = token;
        _serializer = serializer;
    }

    public JToken? Token { get; set; }
    public string ContentType => "application/json";
    public int? SizeHint => null;

    public JToken? this[string propertyName]
    {
        get => EnsureObject()[propertyName];
        set => EnsureObject()[propertyName] = value;
    }

    public LegacyJsonBody Set(string propertyName, JToken? value)
    {
        EnsureObject()[propertyName] = value;
        return this;
    }

    public bool Remove(string propertyName) => EnsureObject().Remove(propertyName);

    private JObject EnsureObject() =>
        Token as JObject ?? throw new InvalidOperationException("The body does not hold a JSON object.");

    public void WriteTo(IBufferWriter<byte> writer) => JsonBodyWriter.Write(writer, Token, _serializer);
}

/// <summary>Newtonsoft <see cref="JArray"/> JSON body (<c>Cybersole.Http.Content.LegacyJarrayBody</c>).</summary>
public sealed class LegacyJarrayBody : IBody
{
    private readonly JsonSerializer? _serializer;

    public LegacyJarrayBody(JsonSerializer? serializer = null)
        : this(new JArray(), serializer)
    {
    }

    public LegacyJarrayBody(JArray array, JsonSerializer? serializer = null)
    {
        Array = array ?? new JArray();
        _serializer = serializer;
    }

    public JArray Array { get; }
    public string ContentType => "application/json";
    public int? SizeHint => null;

    public LegacyJarrayBody Add(JToken? item)
    {
        Array.Add(item ?? JValue.CreateNull());
        return this;
    }

    public void WriteTo(IBufferWriter<byte> writer) => JsonBodyWriter.Write(writer, Array, _serializer);
}
