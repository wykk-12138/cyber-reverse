import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Http\HttpAnalytics.cs"
t = io.open(p, encoding="utf-8").read()

# 1) the interface the analytics layer owns, so the payload stays in the layer that knows what it is
old = '''public sealed class HttpConnectionEvent'''
new = '''/// <summary>
/// Something the analytics flush can hand a session summary to.
///
/// <para>
/// R155: the payload builder lives in <c>Cybersole.Stores</c>, which references this assembly and not the
/// other way round. So the interface lives here and the implementation lives there — the direction of the
/// dependency is the reason, and it also keeps this class from knowing what a fingerprint is.
/// </para>
/// </summary>
public interface ISessionSink
{
    /// <summary>True when the sink has somewhere to send. A false sink is not called at all.</summary>
    bool IsConfigured { get; }

    /// <summary>Build and send one session payload. Never throws.</summary>
    Task<bool> SendAsync(CancellationToken ct = default);
}

public sealed class HttpConnectionEvent'''

if old not in t:
    raise SystemExit("connection event anchor missing")
t = t.replace(old, new, 1)

# 2) the hook
old2 = '''    /// <summary>Optional ClickHouse HTTP endpoint; when null, events stay in memory.</summary>
    public string? SinkUrl { get; set; }'''
new2 = '''    /// <summary>Optional ClickHouse HTTP endpoint; when null, events stay in memory.</summary>
    public string? SinkUrl { get; set; }

    /// <summary>
    /// Optional session-payload sink, drained by the same flush (R155).
    ///
    /// <para>
    /// Separate from <see cref="SinkUrl"/> on purpose: the two send different documents to different hosts,
    /// and either can be configured without the other. A flush with neither does nothing at all, which is the
    /// offline case.
    /// </para>
    /// </summary>
    public ISessionSink? SessionSink { get; set; }'''

if old2 not in t:
    raise SystemExit("sink url anchor missing")
t = t.replace(old2, new2, 1)

# 3) the flush: early return only when there is nothing to do on either side
old3 = '''    public void Flush()
    {
        if (SinkUrl is null) return;     // nothing to do, and nothing to lose'''
new3 = '''    public void Flush()
    {
        // R155: the session sink is a second, independent destination. Returning early on `SinkUrl is null`
        // would have made a telemetry-only configuration silently never send — the same class of defect as
        // R127's dequeue-before-test.
        var session = SessionSink;
        if (session is not null && session.IsConfigured)
        {
            _ = Task.Run(async () =>
            {
                try { await session.SendAsync(CancellationToken.None).ConfigureAwait(false); }
                catch (Exception ex) { _failures.Enqueue($"{DateTime.UtcNow:O} session sink failed: {ex.Message}"); }
            });
        }

        if (SinkUrl is null) return;     // nothing to do on the request side, and nothing to lose'''

if old3 not in t:
    raise SystemExit("flush anchor missing")
t = t.replace(old3, new3, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the flush drains both destinations")
