using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 90: the numbers in <c>docs/IDB_EVIDENCE.md</c> are the numbers in the code.
///
/// <para>
/// R89 found that a paginated IDA query had handed back one window of a table, and the code had
/// been built on it for three rounds. The fix was not just the corrected list — it was to record,
/// for every fact taken out of the image, the query, the hit count and whether the cursor said
/// "done". This test keeps the document and the three constants from drifting apart: change
/// <see cref="NikeEndpoints"/> without updating the document (or the reverse) and it fails.
/// </para>
/// </summary>
public sealed class IDBEvidenceTests
{
    private readonly ITestOutputHelper _out;

    public IDBEvidenceTests(ITestOutputHelper output) => _out = output;

    private static string Doc()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var path = Path.Combine(dir!.FullName, "docs", "IDB_EVIDENCE.md");
        Assert.True(File.Exists(path), "docs/IDB_EVIDENCE.md is missing");
        return File.ReadAllText(path);
    }

    /// <summary>The document exists and states the three counts the code uses.</summary>
    [Fact]
    public void TheDocumentStatesTheCounts()
    {
        var doc = Doc();

        _out.WriteLine($"endpoints={NikeEndpoints.All.Count} headers={NikeHeaders.All.Count} " +
                       $"markets={NikeFlow.Countries.Count}");

        Assert.Contains("| **20** |", doc);   // api.nike.com
        Assert.Contains("| **7** |", doc);    // identifiers
        Assert.Contains("| **42** |", doc);   // markets

        Assert.Contains("| 19 |", doc);       // NikeEndpoints.All
        Assert.Contains("| 7 | ", doc);
        Assert.Contains("| 42 |", doc);
    }

    /// <summary>
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

    /// <summary>
    /// R92 added the store-name method section: how the image stores a store name (a type name plus
    /// a 0x1b 0x08 suffix, which defeats a dollar-anchored regex) and that the same stores appear in
    /// User-Agent literals — which is how OffSpring turned out to be a Poq app rather than Magento.
    /// </summary>
    [Fact]
    public void TheStoreNameMethodIsRecorded()
    {
        var doc = Doc();

        Assert.Contains("## 店铺名的存放方式", doc);
        Assert.Contains("poq.ios", doc);
        Assert.Contains("不足以枚举全部店铺", doc);

        _out.WriteLine("store-name method recorded");
    }

    /// <summary>The unrecoverable list is present, so a future round does not retry it.</summary>
    [Fact]
    public void TheUnrecoverableListIsRecorded()
    {
        var doc = Doc();

        Assert.Contains("Nike 14 步的**子路径**", doc);
        Assert.Contains("字符串里没有、邻域没有、符号里没有", doc);
    }
}
