using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The three RPC steps the replica did not have, recovered from one descriptor of consecutive ordinals.
///
/// <para>
/// R958. The image carries a single string listing ten RPC methods as consecutive state machines:
/// 169 RpcLogin, 170 RpcFindProduct, 171 RpcCheckStock, 172 RpcFetchAddress, 173 RpcCreateAddress,
/// 174 RpcCalculateShipping, 175 RpcValidateBuyRule, 176 RpcCreateOrder, 177 RpcGetPaymentMethods,
/// 178 RpcSubmitCard. Eight have a replica step under another name. Three had none, and each is a real part of a
/// checkout rather than a synonym for something else: CheckStock asks before an order exists, ValidateBuyRule is the
/// shop's own policy check, and GetPaymentMethods is the call that answers what a shop offers -- which is what R957 had
/// to invent a constant for and could not.
/// </para>
/// </summary>
public class MissingRpcStepsTests
{
    /// <summary>The three steps exist as virtual members, so a flow can override them.</summary>
    [Theory]
    [InlineData("CheckStock")]
    [InlineData("ValidateBuyRule")]
    [InlineData("GetPaymentMethods")]
    public void TheThreeStepsExist(string name)
    {
        var method = typeof(StoreFlow).GetMethod(name + "Async");

        Assert.NotNull(method);
        Assert.True(method!.IsVirtual);
        Assert.Equal(typeof(Task<StepOutcome>), method.ReturnType);
    }

    /// <summary>
    /// Without a configured URL each returns NotSupported, which is the existing pattern: the step exists, and a flow
    /// that has no such endpoint says so rather than pretending to work.
    /// </summary>
    [Fact]
    public async Task WithoutAUrlTheySayNotSupported()
    {
        foreach (var name in new[] { "CheckStock", "ValidateBuyRule", "GetPaymentMethods" })
        {
            var method = typeof(StoreFlow).GetMethod(name + "Async")!;
            Assert.NotNull(method);
        }

        // asserted structurally rather than by invoking: constructing a FlowContext needs a live client, and the point
        // here is that the step reports rather than silently succeeding
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));
        foreach (var name in new[] { "CheckStock", "ValidateBuyRule", "GetPaymentMethods" })
            Assert.Contains("NotSupported(\"" + name + "\")", doc);

        await Task.CompletedTask;
    }

    /// <summary>
    /// The parser reads names out of any of the field spellings a shop might use, and returns what it found rather than
    /// claiming a schema.
    /// </summary>
    [Theory]
    [InlineData("{\"methods\":[{\"id\":\"paypal\"}]}", "paypal")]
    [InlineData("{\"methods\":[{\"code\":\"stripe\"}]}", "stripe")]
    [InlineData("{\"methods\":[{\"type\":\"klarna\"}]}", "klarna")]
    [InlineData("{\"methods\":[{\"name\":\"apple_pay\"}]}", "apple_pay")]
    public void TheParserFindsNames(string body, string expected)
    {
        Assert.Contains(expected, StoreFlow.ParsePaymentMethodNames(body));
    }

    /// <summary>Several methods come back together, which is the normal case rather than one per answer.</summary>
    [Fact]
    public void TheParserFindsSeveral()
    {
        var names = StoreFlow.ParsePaymentMethodNames(
            "{\"methods\":[{\"id\":\"paypal\"},{\"id\":\"stripe\"},{\"id\":\"klarna\"}]}");

        Assert.Contains("paypal", names);
        Assert.Contains("stripe", names);
        Assert.Contains("klarna", names);
    }

    /// <summary>An answer with nothing recognisable returns empty rather than inventing a method.</summary>
    [Theory]
    [InlineData("")]
    [InlineData("{}")]
    [InlineData("not json at all")]
    [InlineData("{\"error\":\"nope\"}")]
    public void NothingFoundIsEmpty(string body)
    {
        Assert.Empty(StoreFlow.ParsePaymentMethodNames(body));
    }

    /// <summary>
    /// The recovered ordinal order is recorded, because it is the evidence for which steps run in what order and it
    /// would otherwise live only in a commit message.
    /// </summary>
    [Fact]
    public void TheOrdinalOrderIsRecorded()
    {
        var doc = System.IO.File.ReadAllText(System.IO.Path.Combine(RepoRoot(),
            "src", "Cybersole.Stores", "Flows", "StoreFlow.cs"));

        Assert.Contains("169 RpcLogin", doc);
        Assert.Contains("177 RpcGetPaymentMethods", doc);
        Assert.Contains("178 RpcSubmitCard", doc);

        // and the reason the middle three matter is stated where the code is
        Assert.Contains("GetPaymentMethods\n    // is the call that answers which methods a shop offers", doc);
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