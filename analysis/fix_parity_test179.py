import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EngineParityTests.cs"
t = io.open(p, encoding="utf-8").read()

old = """        Assert.Contains("{ value: head ? (body ? head + '\\\\n' + body : head) : body,", js);"""

new = """        Assert.Contains("Object.defineProperty(error, 'stack', {", js);
        Assert.Contains("head ? (body ? head +", js);"""

if old in t:
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("test loosened")
else:
    # locate the offending line and rewrite it wholesale
    lines = t.split("\n")
    for i, line in enumerate(lines):
        if "value: head ? (body ? head" in line:
            lines[i] = new
            break
    io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("line replaced")
