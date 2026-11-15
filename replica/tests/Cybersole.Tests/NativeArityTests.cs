using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 162: the other two readable fields — <c>length</c> and <c>name</c>.
///
/// <para>
/// The image's shim entry is a triple: <c>{name, length, src}</c>. R161 masked <c>src</c> and copied the arity from
/// the function it had just replaced — which is the shim, so a shim written as <c>function () {…}</c> reported
/// <c>length</c> 0 where the platform reports 1. That is a difference a detector reads in one expression.
/// </para>
/// </summary>
public sealed class NativeArityTests
{
    private readonly ITestOutputHelper _out;

    public NativeArityTests(ITestOutputHelper output) => _out = output;

    /// <summary>The table carries the platform's arities.</summary>
    [Fact]
    public void TheTableIsThePlatformsSignatures()
    {
        Assert.Equal(0, NativeArity.For("getVoices"));
        Assert.Equal(1, NativeArity.For("createEvent"));
        Assert.Equal(1, NativeArity.For("getParameter"));
        Assert.Equal(0, NativeArity.For("toString"));

        Assert.Null(NativeArity.For("noSuchFunction"));
        Assert.Null(NativeArity.For(null));

        Assert.Equal(0, NativeArity.GetterArity);
        Assert.Equal("get plugins", NativeArity.GetterName("plugins"));

        _out.WriteLine(string.Join(", ", NativeArity.Functions.Select(kv => kv.Key + "=" + kv.Value)));
    }

    /// <summary>Every function the mask pass registers has an arity on record.</summary>
    [Fact]
    public void TheTableCoversThePass()
    {
        Assert.True(NativeArity.CoversAll());

        foreach (var target in MaskTargets.Functions)
            Assert.NotNull(NativeArity.For(target.Property));
    }

    /// <summary>The generated pass writes the table's numbers, not the replaced function's.</summary>
    [Fact]
    public void ThePassWritesTheTablesNumber()
    {
        var js = MaskTargets.ApplyJs();

        Assert.Contains("'createEvent', 1)", js);
        Assert.Contains("'getVoices', 0)", js);
        Assert.Contains("'getParameter', 1)", js);

        // the old shape must be gone
        Assert.DoesNotContain(".length)", js);

        Assert.True(JsGuard.IsClean(js), string.Join("; ", JsGuard.Inspect(js).Select(p => p.Kind)));
    }

    /// <summary>The rule names the mistake.</summary>
    [Fact]
    public void TheRuleStands()
    {
        Assert.Contains("copies your own shim", NativeArity.Rule);
        Assert.Contains("recorded rather than inferred", NativeArity.Rule);
    }
}
