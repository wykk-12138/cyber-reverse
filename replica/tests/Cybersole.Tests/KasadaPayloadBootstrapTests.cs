using System;
using System.IO;
using System.Text.Json;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Pins the one step of the payload's bootstrap that decides what bytecode the VM will run: after
/// decoding its literal pool it removes that pool from the same array with <c>splice</c>, which
/// reindexes everything after the cut. Those three numbers come out of the payload's own arithmetic
/// (<c>H = t.length + 4</c>, <c>y = t[length-1] ^ H</c>), so a change in them means the decode path
/// was altered — most likely by a shim edit that changed a value the decoder reads.
///
/// Observed once and asserted here rather than re-derived, because the payload is minified and the
/// derivation depends on reading four nested IIFEs by hand.
/// </summary>
public sealed class KasadaPayloadBootstrapTests
{
    private static string Fixture()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "fixtures", "nike-p.js");
        Assert.True(File.Exists(path), "real payload fixture missing at " + path);
        return File.ReadAllText(path);
    }

    [Fact]
    public void TheLiteralPoolIsCutFromTheBytecodeArrayAtTheSamePlace()
    {
        using var solver = new KasadaSolver(new BrowserShim());
        // The payload now runs to completion (was throwing at opcode 12 until `document.dispatchEvent`
        // was installed). The splice numbers below are what this test exists to pin, not the outcome.
        solver.Runtime.TryExecute(Fixture(), out _);

        var json = solver.Runtime.TryString("JSON.stringify(__dshSplices || [])");
        Assert.False(string.IsNullOrWhiteSpace(json), "the splice recorder produced nothing");

        using var doc = JsonDocument.Parse(json!);
        var splices = doc.RootElement;
        Assert.Equal(1, splices.GetArrayLength());

        var s = splices[0];
        Assert.Equal(13772, s.GetProperty("start").GetInt32());
        Assert.Equal(6283, s.GetProperty("count").GetInt32());
        Assert.Equal(75771, s.GetProperty("len").GetInt32());

        // t[0] is not executed (the frame starts with a program counter of 1); t[1] is the first opcode.
        var head = s.GetProperty("head");
        Assert.Equal(59, head[0].GetInt32());
        Assert.Equal(62, head[1].GetInt32());
        Assert.Equal(3, head[2].GetInt32());
        Assert.Equal(62, head[3].GetInt32());
    }

    [Fact]
    public void ThePayloadRebuildsItsLiteralsThroughFromCharCode()
    {
        using var solver = new KasadaSolver(new BrowserShim());
        solver.Runtime.TryExecute(Fixture(), out _);

        var decoded = solver.Runtime.DecodedStrings;
        Assert.False(string.IsNullOrEmpty(decoded), "the decoder saw nothing built through String.fromCharCode");

        // Names that only exist once the payload's own literal table is rebuilt: a plain grep of the
        // file finds none of them, so their presence proves the decode ran.
        Assert.Contains("x-kpsdk-h", decoded, StringComparison.Ordinal);
        Assert.Contains("clientTime", decoded, StringComparison.Ordinal);
        Assert.Contains("sha256", decoded, StringComparison.Ordinal);
        Assert.Contains("userAgent", decoded, StringComparison.Ordinal);
    }
}
