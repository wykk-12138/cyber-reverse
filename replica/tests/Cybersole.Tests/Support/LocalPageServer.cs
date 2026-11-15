using System.Net;
using System.Net.Sockets;
using System.Text;

namespace Cybersole.Tests;

/// <summary>
/// A one-page HTTP server on loopback.
///
/// 127.0.0.1 counts as a secure context, so APIs gated behind one — userAgentData, usb, serial,
/// mediaDevices, bluetooth, clipboard, gpu, serviceWorker and about thirty navigator members —
/// are present here exactly as they would be on a real store over https. Navigating to a data:
/// URL instead reports all of them absent, which reads as missing features when it is one wrong
/// page.
/// </summary>
internal sealed class LocalPageServer : IDisposable
{
    private readonly HttpListener _listener;
    private readonly CancellationTokenSource _cts = new();
    private readonly Task _loop;

    public string Url { get; }

    public LocalPageServer(string body = "<!doctype html><html><head><title>page</title></head><body>page</body></html>")
    {
        var port = FreePort();
        Url = $"http://127.0.0.1:{port}/";

        _listener = new HttpListener();
        _listener.Prefixes.Add(Url);
        _listener.Start();

        var payload = Encoding.UTF8.GetBytes(body);

        _loop = Task.Run(async () =>
        {
            while (!_cts.IsCancellationRequested)
            {
                try
                {
                    var ctx = await _listener.GetContextAsync();
                    ctx.Response.ContentType = "text/html; charset=utf-8";
                    ctx.Response.ContentLength64 = payload.Length;
                    await ctx.Response.OutputStream.WriteAsync(payload);
                    ctx.Response.Close();
                }
                catch (Exception)
                {
                    return;
                }
            }
        });
    }

    private static int FreePort()
    {
        var probe = new TcpListener(IPAddress.Loopback, 0);
        probe.Start();
        var port = ((IPEndPoint)probe.LocalEndpoint).Port;
        probe.Stop();
        return port;
    }

    public void Dispose()
    {
        _cts.Cancel();
        try { _listener.Stop(); } catch (Exception) { }
        try { _listener.Close(); } catch (Exception) { }
        try { _loop.Wait(1000); } catch (Exception) { }
        _cts.Dispose();
    }
}
