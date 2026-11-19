using System.Linq;
using System.Reflection;
using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Cart priming: AddToCartDummy is a placeholder item, not a dry run.
///
/// <para>
/// R941. R940 called it the one gap that need not wait on endpoint evidence, reasoning that its name says it does not talk
/// to a shop. Its neighbours say otherwise -- AddToCartDummy is followed immediately by RemoveDummy, an add and its
/// remove, which is how a cart is created early so the real add reuses one that already exists. The name is about the item
/// being a placeholder, not the call being fake.
/// </para>
/// </summary>
public class CartPrimingTests
{
    private static string[] Arr(string name) =>
        (string[])typeof(CartPriming)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetValue(null)!;

    private static string Const(string name) =>
        (string)typeof(CartPriming)
            .GetField(name, BindingFlags.NonPublic | BindingFlags.Static)!
            .GetRawConstantValue()!;

    /// <summary>The four consecutive state machines, with the add before its remove.</summary>
    [Fact]
    public void TheSequenceIsAddThenRemove()
    {
        var sequence = Arr("PrimingSequence");

        Assert.Equal(new[] { "GetProduct", "AddToCartDummy", "AddToCartMulti", "RemoveDummy" }, sequence);
        Assert.True(Array.IndexOf(sequence, "AddToCartDummy") < Array.IndexOf(sequence, "RemoveDummy"));
    }

    /// <summary>Priming is the recorded meaning, and the constant says so in words rather than leaving it to a comment.</summary>
    [Fact]
    public void TheMeaningIsPrimingNotADryRun()
    {
        var meaning = Const("Meaning");

        Assert.Contains("placeholder", meaning);
        Assert.Contains("reuses a cart", meaning);
        Assert.DoesNotContain("dry run", meaning);
    }

    /// <summary>The pair is classified together, since an add without its remove leaves a stray item.</summary>
    [Theory]
    [InlineData("AddToCartDummy", true)]
    [InlineData("RemoveDummy", true)]
    [InlineData("AddToCartMulti", false)]
    [InlineData("AddToCartNext", false)]
    [InlineData(null, false)]
    public void ThePairIsRecognisedTogether(string? name, bool expected)
    {
        Assert.Equal(expected, CartPriming.IsPriming(name));
    }

    /// <summary>
    /// Two calls for one priming step, in order. A caller cannot add without removing, which is the failure the pair
    /// exists to prevent -- a stray item left in the cart.
    /// </summary>
    [Fact]
    public void TwoCallsInOrderForOneStep()
    {
        var calls = CartPriming.CallsFor("sku-1");

        Assert.Equal(2, calls.Count);
        Assert.Equal("add:sku-1", calls[0]);
        Assert.Equal("remove:sku-1", calls[1]);
    }

    /// <summary>
    /// The loyalty surface narrows which shop this belongs to without naming it, and the narrowing is inference from names
    /// rather than something recovered.
    /// </summary>
    [Fact]
    public void TheLoyaltySurfaceIsRecordedAsInference()
    {
        var surface = Arr("LoyaltySurface");

        Assert.Contains("FetchBalance", surface);
        Assert.Contains("CheckFanRewardStat", surface);
        Assert.Contains("EnterSweepStakesRaffle", surface);
        Assert.Contains("LoginVerify2FA", surface);

        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Scripts", "CartPriming.cs"));
        Assert.Contains("labelled as such", doc);
    }

    /// <summary>What is still missing is per-shop data, and the constant says which datum rather than saying unknown.</summary>
    [Fact]
    public void TheMissingDatumIsNamed()
    {
        var unknown = Const("UnknownForPriming");

        Assert.Contains("which item", unknown);
        Assert.Contains("per-shop", unknown);
    }

    private static string RepoRoot()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}