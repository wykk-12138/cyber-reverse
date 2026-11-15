import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Support\TinyServer.cs'
t = io.open(p, encoding='utf-8').read()

old = '''    private readonly HttpListener _listener = new();
    public string BaseUrl { get; }'''
new = '''    private HttpListener _listener = new();
    public string BaseUrl { get; }'''

old2 = '''        var port = FreePort();
        BaseUrl = $"http://127.0.0.1:{port}";
        _listener.Prefixes.Add(BaseUrl + "/");
        _listener.Start();
'''
new2 = '''        // R206: FreePort() closes its probe socket before this listener binds, so another process (or a listener left
        // over from the previous test run) can take the port in between -- measured as
        // "System.Net.HttpListenerException : Access is denied" roughly one run in six, which is enough to make a
        // mutation-check verdict unreadable. Each attempt gets a fresh port and a fresh listener; five is plenty and
        // the failure names the reason rather than surfacing a bare Access-denied.
        string? baseUrl = null;
        Exception? lastError = null;

        for (var attempt = 1; attempt <= 5 && baseUrl is null; attempt++)
        {
            var candidate = $"http://127.0.0.1:{FreePort()}";
            var listener = new HttpListener();
            listener.Prefixes.Add(candidate + "/");
            try
            {
                listener.Start();
                _listener = listener;
                baseUrl = candidate;
            }
            catch (Exception error)
            {
                lastError = error;
                try { listener.Close(); } catch { /* the next attempt gets its own listener */ }
            }
        }

        if (baseUrl is null)
            throw new InvalidOperationException(
                "TinyServer could not bind a loopback port after 5 attempts", lastError);

        BaseUrl = baseUrl;
'''
assert old in t and old2 in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new).replace(old2, new2))
print('patched TinyServer')
