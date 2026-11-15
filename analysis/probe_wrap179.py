import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ParityProbe.cs"
t = io.open(p, encoding="utf-8").read()

tail = '''
        // does the wrapper itself run?
        _out.WriteLine("wrapped = " + await bridge.EvaluateAsync(
            "(() => { const e = new Error('x'); const out = []; " +
            "out.push(String(e.stack).indexOf('@') >= 0 ? 'jsc' : 'v8'); " +
            "out.push(!!Object.getOwnPropertyDescriptor(e, 'stack').get); " +
            "try { Object.defineProperty(e, 'stack', { value: 'rewritten', writable: true, configurable: true }); " +
            "out.push(String(e.stack)); } catch (err) { out.push('throw:' + err.message); } " +
            "return JSON.stringify(out); })()"));
    }
}
'''

idx = t.rstrip().rfind("}")
idx = t.rstrip()[:idx].rstrip().rfind("}")
t = t.rstrip()[:idx].rstrip() + "\n" + tail
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("probe extended again")
