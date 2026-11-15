using System.Linq;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R199: the voice list. The replica used to answer six Windows/Google voices; the device answers 68 Apple ones, so the
/// count AND every voiceURI disagreed with the persona.
/// </summary>
public sealed class VoiceListTests
{
    private readonly ITestOutputHelper _out;
    public VoiceListTests(ITestOutputHelper output) => _out = output;

    const string IPhone = "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) " +
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/156.0.8078.54 " +
                          "Mobile/15E148 Safari/604.1";

    private const string Probe =
        "(() => { const v = speechSynthesis.getVoices(); const first = v[0] || {}; " +
        "const d = v.filter((x) => x.default); " +
        "return JSON.stringify([v.length, first.name || '', first.voiceURI || '', first.lang || '', " +
        "d.length, d[0] ? d[0].name : '', " +
        "v.every((x) => x.voiceURI.indexOf('com.apple') === 0), " +
        "v.filter((x) => x.lang === 'nl-BE').length]); })()";

    private static async Task<string?> MeasureAsync(bool stealth)
    {
        await using var bridge = await ChromiumBridge.LaunchAsync(userAgent: IPhone);
        if (stealth) await bridge.ApplyStealthAsync(IPhone);
        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        return await bridge.EvaluateAsync(Probe);
    }

    [Fact]
    public async Task TheVoiceListIsTheDevices()
    {
        var raw = await MeasureAsync(stealth: false);
        var patched = await MeasureAsync(stealth: true);
        _out.WriteLine("raw     = " + raw);
        _out.WriteLine("patched = " + patched);

        using var doc = System.Text.Json.JsonDocument.Parse(patched!);
        var r = doc.RootElement;

        var table = System.Text.Json.JsonDocument.Parse(VoiceTable.VoicesJs).RootElement;
        var expected = table.EnumerateArray().ToList();

        Assert.Equal(VoiceTable.Count, r[0].GetInt32());
        Assert.Equal(68, r[0].GetInt32());

        // the first row is the device's, name and URI
        Assert.Equal(expected[0].GetProperty("name").GetString(), r[1].GetString());
        Assert.Equal(expected[0].GetProperty("voiceURI").GetString(), r[2].GetString());
        Assert.Equal(expected[0].GetProperty("lang").GetString(), r[3].GetString());

        // every URI is an Apple one — the tell the old Microsoft/Google list produced
        Assert.True(r[6].GetBoolean(), "a voiceURI is not com.apple…");

        // the capture records every one of them as default and local, which is what the device reported
        Assert.Equal(VoiceTable.Count, r[4].GetInt32());
        Assert.Equal(VoiceTable.DefaultName, r[5].GetString());
        Assert.True(r[7].GetInt32() >= 1, "no nl-BE voice for a nl-BE persona");
    }

    [Fact]
    public void TheTableIsVerbatim()
    {
        Assert.Equal(68, VoiceTable.Count);
        Assert.Equal("Ellen", VoiceTable.DefaultName);
        Assert.Contains("com.apple.voice.super-compact.nl-BE.Ellen", VoiceTable.VoicesJs);
        Assert.DoesNotContain("Microsoft", VoiceTable.VoicesJs);
        Assert.DoesNotContain("Google US English", VoiceTable.VoicesJs);
    }
}
