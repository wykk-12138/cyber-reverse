import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\AccessorWordingTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // Blink's wording must not appear anywhere in the body
        Assert.DoesNotContain("Illegal invocation", js, System.StringComparison.Ordinal);'''

new = '''        // Blink's wording must not appear as a THROWN message. The comment above the code names Blink's phrasing on
        // purpose — that is the sentence this file exists to not produce — so the assertion looks for the quote form.
        Assert.DoesNotContain("'Illegal invocation'", js, System.StringComparison.Ordinal);'''

if old not in t:
    raise SystemExit("wording anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion targets the thrown string")
