import io, re

# 1) GlobalSurfaceTests: route its ProbeAsync through BrowserProbe
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GlobalSurfaceTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await Task.Delay(50);
        }
        return await bridge.EvaluateAsync(js);'''
new = '''        await bridge.NavigateAsync("data:text/html,<html><body>x</body></html>");
        // R206: readyState alone was not enough -- Chromium puts `chrome` back after the prune, and how late depends on
        // load. Wait for the name count to stop moving before measuring.
        await Support.BrowserProbe.ReadyAsync(bridge);
        return await bridge.EvaluateAsync(js);'''
assert old in t, 'surface probe'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))

# 2) GlobalPruneTests: both tests wait for readyState then measure; insert the settle call
p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GlobalPruneTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
old2 = '''        for (var i = 0; i < 100; i++)
        {
            if (await bridge.EvaluateAsync("document.readyState") == "complete") break;
            await System.Threading.Tasks.Task.Delay(50);
        }'''
new2 = '''        // R206: wait for the window to settle, not just for readyState -- see Support/BrowserProbe.
        await Support.BrowserProbe.ReadyAsync(bridge);'''
n = t2.count(old2)
assert n >= 1, 'prune probe'
t2 = t2.replace(old2, new2)
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('patched probes:', n, 'in prune tests')
