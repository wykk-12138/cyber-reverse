import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ParityProbe.cs"
t = io.open(p, encoding="utf-8").read()

marker = '''        _out.WriteLine("errsrc  = " + await bridge.EvaluateAsync('''
addition = '''        // isolate the Error block and let the exception through
        _out.WriteLine("isolate = " + await bridge.EvaluateAsync(
            "(() => { const G = window; const name = 'Error'; try { " +
            "const Original = G[name]; " +
            "const Wrapped = function (...args) { return Original(...args); }; " +
            "Wrapped.prototype = Original.prototype; " +
            "Object.getOwnPropertyNames(Original).forEach((key) => { try { Wrapped[key] = Original[key]; } catch (e) {} }); " +
            "Object.defineProperty(Wrapped, 'name', { value: name, configurable: true }); " +
            "Object.defineProperty(Wrapped, 'length', { value: Original.length, configurable: true }); " +
            "G[name] = Wrapped; " +
            "return String(G.Error === Wrapped) + ':' + String(String(Error).length); } " +
            "catch (e) { return 'err:' + e.name + ':' + e.message; } })()"));

'''
t = t.replace(marker, addition + marker, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("isolation probe added")
