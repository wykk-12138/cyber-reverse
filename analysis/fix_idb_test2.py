import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\IDBEvidenceTests.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    /// <summary>Every row must say the cursor was done")
end = t.find("    /// <summary>The unrecoverable list is present")
if start < 0 or end < 0:
    raise SystemExit("anchors: %d .. %d" % (start, end))

new_test = '''    /// <summary>
    /// Every query in the log is marked complete. Counting the cells is more robust than trying to
    /// recognise a row: the table has a header, a separator and a second table further down, and a
    /// row-shaped filter catches all three.
    /// </summary>
    [Fact]
    public void EveryQueryInTheTableIsMarkedComplete()
    {
        var doc = Doc();
        var cut = doc.IndexOf("## 数字与代码的对应", StringComparison.Ordinal);
        Assert.True(cut > 0, "the query table section is missing");

        var section = doc[..cut];
        var done = Count(section, "| ✅ |");
        var failed = Count(section, "| ❌ |");
        var paged = Count(section, "…");

        _out.WriteLine($"done={done} failed={failed} paged={paged}");

        Assert.Equal(6, done);      // six facts recorded so far
        Assert.Equal(0, failed);
        Assert.Equal(0, paged);
    }

    private static int Count(string haystack, string needle)
    {
        var n = 0;
        var i = haystack.IndexOf(needle, StringComparison.Ordinal);
        while (i >= 0)
        {
            n++;
            i = haystack.IndexOf(needle, i + needle.Length, StringComparison.Ordinal);
        }

        return n;
    }

'''

t = t[:start] + new_test + t[end:]
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("completeness test rewritten to count cells")
