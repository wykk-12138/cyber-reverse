using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 182: the twelve Chrome-for-iOS window names, installed and measured.
///
/// <para>
/// R181 read the list and found them; this round puts them on the window and checks two things a page can check:
/// that a phone profile carries them, and that a child frame does <b>not</b> carry the two its real counterpart lacks —
/// "a frame advertised two names its real counterpart lacks".
/// </para>
/// </summary>
public sealed class WindowNamesInstalledTests
{
    private readonly ITestOutputHelper _out;

    public WindowNamesInstalledTests(ITestOutputHelper output) => _out = output;

    private const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                                  "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                                  "Mobile/15E148 Safari/604.1";

    /// <summary>Measured: all twelve names are on the window, and the baseline says how it was taken.</summary>
    [Fact]
    public async Task TheNamesAreOnTheWindow()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "JSON.stringify([['_injected_clipboard','_injected_passkey_controller','__gCrWeb','gcrweb'," +
            "'_injected_print','_injected_choose_file'].filter((n) => n in window).length, " +
            "typeof window.__windowBaseline, window.__windowBaseline ? window.__windowBaseline.framed : null, " +
            "window.__windowBaseline ? window.__windowBaseline.injected.length : null])");

        _out.WriteLine("probe = " + probe);
        Assert.Equal("[6,\"object\",false,12]", probe);

        // and they are enumerable, which is what Object.keys(window) reads
        var keys = await bridge.EvaluateAsync(
            "(() => { const k = Object.keys(window); " +
            "return String(k.indexOf('__gCrWeb') >= 0) + ':' + String(k.indexOf('_injected_clipboard') >= 0); })()");
        Assert.Equal("true:true", keys);
    }

    /// <summary>Measured: a child frame lacks the two main-frame-only names and keeps the rest.</summary>
    [Fact]
    public async Task AChildFrameLacksTheTwo()
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        await bridge.EvaluateAsync(
            "(() => { const f = document.createElement('iframe'); f.id = 'probe'; document.body.appendChild(f); " +
            "return 'ok'; })()");

        for (var i = 0; i < 100; i++)
        {
            var ready = await bridge.EvaluateAsync(
                "(() => { const f = document.getElementById('probe'); " +
                "return String(!!(f && f.contentDocument && f.contentDocument.readyState === 'complete')); })()");
            if (ready == "true") break;
            await System.Threading.Tasks.Task.Delay(50);
        }

        var probe = await bridge.EvaluateAsync(
            "(() => { const w = document.getElementById('probe').contentWindow; " +
            "return JSON.stringify([('_injected_scroll_helper' in w), ('_injected_navigation' in w), " +
            "('__gCrWeb' in w), ('gcrweb' in w)]); })()");

        _out.WriteLine("child = " + probe);
        Assert.Equal("[false,false,true,true]", probe);
    }
}
