using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R196: the event-handler attributes. The measured shape is the point — hsw reads the descriptor, not just `in`.
/// </summary>
public sealed class HandlerSurfaceTests
{
    private readonly ITestOutputHelper _out;
    public HandlerSurfaceTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private static async Task<string?> ProbeAsync(string js)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(js);
    }

    private const string Probe =
        "(() => { const names = ['ontouchstart', 'ontouchend', 'ontouchmove', 'ontouchcancel', " +
        "'ontouchforcechange']; " +
        "const d = Object.getOwnPropertyDescriptor(window, 'ontouchstart'); " +
        "const src = d && d.get ? Function.prototype.toString.call(d.get) : ''; " +
        "window.ontouchstart = 1; " +
        "const afterNumber = window.ontouchstart; " +
        "const fake = function () {}; window.ontouchstart = fake; " +
        "const afterFunction = window.ontouchstart === fake; " +
        "let branded = 'none'; try { d.get.call({}); branded = 'allowed'; } catch (e) { branded = e.message; } " +
        "const ev = (() => { try { return document.createEvent('TouchEvent').type; } catch (e) { return 'threw:' + e.name; } })(); " +
        "return JSON.stringify([names.filter((n) => n in window).length, " +
        "d ? (d.get ? 'get' : 'nodget') + (d.set ? '+set' : '') + (d.value === undefined ? '+nodvalue' : '+value') : 'none', " +
        "src.split('\\n').length, src.indexOf('function ontouchstart()') === 0, " +
        "afterNumber === null, afterFunction, branded, ev, " +
        "('webkitIndexedDB' in window), ('memory' in performance)]); })()";

    [Fact]
    public async Task TheHandlersAreAccessorPairs()
    {
        var probe = await ProbeAsync(Probe);
        _out.WriteLine("handlers = " + probe);
        Assert.False(string.IsNullOrWhiteSpace(probe));

        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        // all five touch handlers exist: hsw gates its worker path on one of them
        Assert.Equal(5, r[0].GetInt32());

        // the descriptor is an accessor pair with no `value` — not a data slot holding null (R193's shape)
        Assert.Equal("get+set+nodvalue", r[1].GetString());

        // and the getter is cloaked in WebKit's three-line native form
        Assert.Equal(3, r[2].GetInt32());
        Assert.True(r[3].GetBoolean(), "the getter's source does not read as a native accessor");

        // the setter keeps the handler when it is a function and drops anything else
        Assert.True(r[4].GetBoolean(), "assigning a number was kept instead of becoming null");
        Assert.True(r[5].GetBoolean(), "assigning a function did not stick");

        // the brand check, in WebKit's wording
        Assert.Contains("can only be used on instances of Window", r[6].GetString());
    }

    [Fact]
    public async Task TheThreeCorrectionsHold()
    {
        var probe = await ProbeAsync(Probe);
        using var doc = System.Text.Json.JsonDocument.Parse(probe!);
        var r = doc.RootElement;

        // createEvent('TouchEvent') succeeds, as it does on WebKit — the payload records it as a boolean
        Assert.Equal("", r[7].GetString());
        Assert.True(r[8].GetBoolean(), "webkitIndexedDB is missing");
        Assert.False(r[9].GetBoolean(), "performance.memory is still there");
    }

    [Fact]
    public void TheTableIsVerbatim()
    {
        Assert.Contains("\"onabort\"", HandlerTable.HandlersJs);
        Assert.Contains("\"ontouchforcechange\"", HandlerTable.HandlersJs);
        Assert.Equal(5, HandlerTable.Touch.Length);
        Assert.Equal(3, HandlerSurface.Corrections.Length);
        Assert.Contains("{value: null, writable: true}", HandlerSurface.Rule);
    }
}
