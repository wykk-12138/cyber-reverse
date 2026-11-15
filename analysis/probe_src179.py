import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ParityProbe.cs"
t = io.open(p, encoding="utf-8").read()

marker = '''        _out.WriteLine("wrapped = " + await bridge.EvaluateAsync('''
addition = '''        _out.WriteLine("errsrc  = " + await bridge.EvaluateAsync(
            "JSON.stringify(String(Error))"));
        _out.WriteLine("errOwn  = " + await bridge.EvaluateAsync(
            "JSON.stringify(Object.getOwnPropertyNames(Error).slice(0, 6))"));

'''

t = t.replace(marker, addition + marker, 1)
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("probe extended with the source text")
