import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\StackElisionTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        // no frame of ours: the injected script is a data: or blob: URL with a line and column
        Assert.DoesNotContain("at illegalInvocation", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("blob:", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("<anonymous>:", stack, System.StringComparison.Ordinal);'''

new = '''        // No frame of OURS: not the helper, and not the injected script's URL. The frame below the native one is the
        // CALLER — here that is the harness's own evaluate, which renders as `<anonymous>:` and is exactly what the
        // device shows for a page's own code, so it is not a tell and is not asserted against.
        Assert.DoesNotContain("at illegalInvocation", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("blob:", stack, System.StringComparison.Ordinal);
        Assert.DoesNotContain("__nativeMask", stack, System.StringComparison.Ordinal);

        // and the native frame sits immediately under the message
        var lines = stack!.Split('\\n');
        Assert.Contains("Illegal invocation", lines[0], System.StringComparison.Ordinal);
        Assert.Contains("at get platform (native)", lines[1], System.StringComparison.Ordinal);'''

if old not in t:
    raise SystemExit("assertion anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("the assertion names the real tell")
