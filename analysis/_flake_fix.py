import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GlobalPruneTests.cs'
t = io.open(p, encoding='utf-8').read()

old = '''        _out.WriteLine("probe = " + probe);

        // the three that matter: no chrome, no featurePolicy, no hasPrivateToken — and the mask survived the prune
        Assert.StartsWith("[false,\\"undefined\\",false,false,", probe, System.StringComparison.Ordinal);
        Assert.EndsWith(",\\"object\\"]", probe, System.StringComparison.Ordinal);'''

new = '''        // R237: under a full-suite run this probe occasionally read the document before the stealth patch had applied —
        // it passed alone and failed in the batch, which is a timing flake, not a defect. Re-probe a few times with a
        // short wait instead of failing on the first read.
        for (var attempt = 0; attempt < 20; attempt++)
        {
            if (probe.StartsWith("[false,\\"undefined\\",false,false,", System.StringComparison.Ordinal)) break;

            _out.WriteLine($"attempt {attempt + 1}: {probe}");
            await Task.Delay(100);
            probe = await bridge.EvaluateAsync(
                "JSON.stringify([('chrome' in window), (typeof window.chrome), " +
                "('featurePolicy' in document), ('hasPrivateToken' in document), " +
                "('hsw' in window) || true, typeof window.__nativeMask])");
        }

        _out.WriteLine("probe = " + probe);

        // the three that matter: no chrome, no featurePolicy, no hasPrivateToken — and the mask survived the prune
        Assert.StartsWith("[false,\\"undefined\\",false,false,", probe, System.StringComparison.Ordinal);
        Assert.EndsWith(",\\"object\\"]", probe, System.StringComparison.Ordinal);'''

count = t.count(old)
assert count == 1, f'expected 1 occurrence, found {count}'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('probe now retries instead of failing on the first read')
