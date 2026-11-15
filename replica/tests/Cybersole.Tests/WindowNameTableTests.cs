using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 183: the device's two window orders, read out of the capture — and the number this workspace had wrong.
///
/// <para>
/// <c>Object.getOwnPropertyNames(window)</c> reports <b>1062</b> names and <c>Object.keys(window)</c> reports
/// <b>228</b>. The previous round recorded 1290, which was a guess about the list rather than a count of it.
/// </para>
///
/// <para>
/// Comparing the two orders also explains a sentence that had looked odd: the iPhone reported
/// <c>["__gCrWeb","hsw","__wdata","webkit"]</c> with <c>webkit</c> <b>last</b>, after two script-created globals — because
/// <c>webkit</c> is in the own-names order and <b>not</b> in the enumerable one.
/// </para>
/// </summary>
public sealed class WindowNameTableTests
{
    private readonly ITestOutputHelper _out;

    public WindowNameTableTests(ITestOutputHelper output) => _out = output;

    /// <summary>The two counts, and the correction.</summary>
    [Fact]
    public void TheCountsAreMeasured()
    {
        Assert.Equal(1062, WindowNameTable.AllCount);
        Assert.Equal(228, WindowNameTable.EnumCount);
        Assert.Equal(1062, WindowBaseline.RecordedNameCount);
        Assert.Equal(228, WindowBaseline.RecordedEnumCount);

        // the enumerable list is a strict subset, in its own order
        Assert.All(WindowNameTable.Enum, n => Assert.Contains(n, WindowNameTable.All));
        Assert.True(WindowNameTable.OwnOnly.Count > 0);

        Assert.Contains("1062", WindowNameTable.Correction);
        _out.WriteLine($"{WindowNameTable.AllCount} own, {WindowNameTable.EnumCount} enumerable, "
                       + $"{WindowNameTable.OwnOnly.Count} own-only");
    }

    /// <summary><c>webkit</c> is last in one order and absent from the other.</summary>
    [Fact]
    public void WebkitIsTheProof()
    {
        Assert.Equal("webkit", WindowNameTable.All.Last());
        Assert.DoesNotContain("webkit", WindowNameTable.Enum);
        Assert.Equal("webkit", WindowNameTable.LastOwnOnly);

        // and __gCrWeb IS enumerable, which is why the device's four-name sample ends with webkit
        Assert.Contains("__gCrWeb", WindowNameTable.Enum);
        Assert.Equal("__gCrWeb", WindowNameTable.Enum.Last());

        Assert.Contains("lands BEFORE the script globals", WindowNameTable.Rule);
    }

    /// <summary>All twelve Chrome-for-iOS names are enumerable on the device.</summary>
    [Fact]
    public void TheInjectedNamesAreEnumerable()
    {
        Assert.Equal(12, WindowNameTable.Injected.Count);
        Assert.All(WindowBaseline.InjectedNames, n => Assert.Contains(n, WindowNameTable.Enum));

        // and the device's own list starts with them
        Assert.Equal("_injected_programmatic_form_submission_handler", WindowNameTable.All[2]);
        Assert.Equal("gcrweb", WindowNameTable.All[3]);

        foreach (var name in WindowBaseline.InjectedNames) _out.WriteLine("  " + name);
    }
}
