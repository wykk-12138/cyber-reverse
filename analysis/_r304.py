import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\Support\BrowserProbe.cs'
t = io.open(p, encoding='utf-8').read()

anchor = '''    /// <summary>Readies a freshly navigated page: readyState complete, then a settled name count.</summary>'''
add = '''    /// <summary>
    /// Waits until the actual <b>name list</b> — not its length — is identical across three samples.
    ///
    /// <para>
    /// R304: <see cref="SettleAsync"/> watches the count, which is a proxy. On 2026-11-13 the suite failed
    /// <c>NoNameIsAdvertisedWithoutAProperty</c> twice with a stable count and a different set, i.e. Chromium had swapped
    /// one name for another inside the same length. Measuring what the assertion measures removes that gap without
    /// weakening a single assertion.
    /// </para>
    /// </summary>
    public static async Task SettleNamesAsync(ChromiumBridge bridge, int stableSamples = 3, int maxSamples = 60)
    {
        string? last = null;
        var steady = 0;

        for (var i = 0; i < maxSamples; i++)
        {
            string? names;
            try
            {
                names = await bridge.EvaluateAsync("Object.getOwnPropertyNames(window).sort().join(',')");
            }
            catch (Exception) { names = last; }

            if (names == last && names is not null) steady++;
            else steady = 0;

            last = names;
            if (steady >= stableSamples - 1) return;

            await Task.Delay(60).ConfigureAwait(false);
        }
    }

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SettleNamesAsync added')

p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GlobalSurfaceTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''        await Support.BrowserProbe.ReadyAsync(bridge);
        return await bridge.EvaluateAsync(js);'''
new2 = '''        await Support.BrowserProbe.ReadyAsync(bridge);
        // R304: the count can be stable while the set is not, so settle on the names themselves before measuring.
        await Support.BrowserProbe.SettleNamesAsync(bridge);
        return await bridge.EvaluateAsync(js);'''
assert old2 in t2
io.open(p2, 'w', encoding='utf-8', newline='').write(t2.replace(old2, new2, 1))
print('ProbeAsync now settles on the name list')
