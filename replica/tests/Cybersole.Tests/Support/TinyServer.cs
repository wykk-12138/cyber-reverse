using System.Net;
using System.Text;

namespace Cybersole.Tests.Support;

/// <summary>Loopback HTTP server used by integration-style tests.</summary>
public sealed class TinyServer : IDisposable
{
    private HttpListener _listener = new();
    public string BaseUrl { get; }

    /// <summary>Requests seen, in arrival order: (method, path, body).</summary>
    public List<(string Method, string Path, string Body)> Requests { get; } = new();

    /// <summary>Headers of each request, in the same order as <see cref="Requests"/>.</summary>
    public List<Dictionary<string, string>> RequestHeaders { get; } = new();

    /// <summary>Raw request target — path plus query — of each request, in the same order as <see cref="Requests"/>.</summary>
    public List<string> RequestTargets { get; } = new();

    public TinyServer(Func<HttpListenerRequest, string, (int Status, string Body)> handler)
    {
        // R206: FreePort() closes its probe socket before this listener binds, so another process (or a listener left
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

        _ = Task.Run(async () =>
        {
            while (_listener.IsListening)
            {
                HttpListenerContext ctx;
                try { ctx = await _listener.GetContextAsync().ConfigureAwait(false); }
                catch { return; }

                string body;
                using (var reader = new StreamReader(ctx.Request.InputStream, Encoding.UTF8))
                    body = await reader.ReadToEndAsync().ConfigureAwait(false);

                Requests.Add((ctx.Request.HttpMethod, ctx.Request.Url?.AbsolutePath ?? "/", body));

                // R1311: the headers, alongside the request, because some behaviour only exists in them --
                // Cybersource Flex carries its capture context as an Authorization bearer, and a body-only
                // record cannot tell a request that sent it from one that did not. Additive: `Requests` keeps
                // its shape so no existing case changes.
                var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                foreach (string key in ctx.Request.Headers)
                    headers[key] = ctx.Request.Headers[key] ?? string.Empty;
                RequestHeaders.Add(headers);
                // R1314: the query string, because a GET carries its payload there and `Requests` keeps only
                // the path. Additive again: the existing tuple shape is untouched.
                RequestTargets.Add(ctx.Request.RawUrl ?? string.Empty);

                var (status, responseBody) = handler(ctx.Request, body);
                var bytes = Encoding.UTF8.GetBytes(responseBody);
                ctx.Response.StatusCode = status;
                ctx.Response.ContentType = "application/json";
                await ctx.Response.OutputStream.WriteAsync(bytes).ConfigureAwait(false);
                ctx.Response.Close();
            }
        });
    }

    public TinyServer(Func<HttpListenerRequest, (int Status, string Body)> handler)
        : this((req, _) => handler(req))
    {
    }

    private static int FreePort()
    {
        var l = new System.Net.Sockets.TcpListener(IPAddress.Loopback, 0);
        l.Start();
        var port = ((IPEndPoint)l.LocalEndpoint).Port;
        l.Stop();
        return port;
    }

    public void Dispose()
    {
        try { _listener.Stop(); } catch { }
        _listener.Close();
    }
}
