import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\SessionTelemetry.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    /// <summary>The reason the last attempt did not send, or null when it did.</summary>
    public string? LastError { get; private set; }'''

new = '''    /// <summary>The reason the last attempt did not send, or null when it did.</summary>
    public string? LastError { get; private set; }

    /// <summary>
    /// Where the inputs come from when the analytics flush calls this sink (R155).
    ///
    /// <para>
    /// The flush runs on a timer and knows nothing about sessions, so the caller supplies a factory rather
    /// than a snapshot: the payload must describe the session as it is at send time, not as it was when the
    /// sink was attached.
    /// </para>
    /// </summary>
    public Func<SessionPayloadBuilder.Inputs>? InputsFactory { get; set; }

    /// <summary>The flush's entry point: build from the factory and send.</summary>
    async Task<bool> Cybersole.Http.ISessionSink.SendAsync(CancellationToken ct)
    {
        if (InputsFactory is null)
        {
            LastError = "no inputs factory: nothing to describe";
            return false;
        }

        return await SendAsync(InputsFactory(), ct).ConfigureAwait(false);
    }'''

if old not in t:
    raise SystemExit("last error anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the sink implements the interface through a factory")
