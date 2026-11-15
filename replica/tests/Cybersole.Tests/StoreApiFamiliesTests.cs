using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 102: three more endpoint families, dumped before anything was written against them.
///
/// <para>
/// Twenty-two literals across three store engines:
/// </para>
///
/// <code>
/// /rpc/ec/*                        7   stock, addresses, freight, buy rules, order
/// /component/singlepagecheckout/*  7   Hybris-style single-page checkout
/// /apps/gatekeeper/api/*           8   a release gate: token, challenge, audit
/// </code>
///
/// <para>
/// The gatekeeper family is the interesting one. It is a <b>release gate</b>, not a cart: a drop
/// hands out a challenge, the client renders a token, swaps it for a gatekeeper token, and the
/// server has to agree the token is valid before anything can be added. A flow that skips it does
/// not fail with an error — it fails with a 403 that looks like a ban.
/// </para>
/// </summary>
public sealed class StoreApiFamiliesTests
{
    private readonly ITestOutputHelper _out;

    public StoreApiFamiliesTests(ITestOutputHelper output) => _out = output;

    /// <summary>Seven, seven and eight — twenty-two in total, all distinct.</summary>
    [Fact]
    public void TheThreeFamiliesHaveTheirImagesCounts()
    {
        Assert.Equal(7, StoreApiFamilies.RpcEc.All.Count);
        Assert.Equal(7, StoreApiFamilies.SinglePageCheckout.All.Count);
        Assert.Equal(8, StoreApiFamilies.Gatekeeper.All.Count);

        Assert.Equal(22, StoreApiFamilies.All.Count);
        Assert.Equal(22, StoreApiFamilies.All.Distinct().Count());

        foreach (var p in StoreApiFamilies.All) _out.WriteLine(p);
    }

    /// <summary>Every path is under its family's prefix — no stragglers from another engine.</summary>
    [Fact]
    public void EachPathSitsUnderItsOwnPrefix()
    {
        Assert.All(StoreApiFamilies.RpcEc.All, p => Assert.StartsWith("/rpc/ec/", p));
        Assert.All(StoreApiFamilies.SinglePageCheckout.All,
            p => Assert.StartsWith("/component/singlepagecheckout/", p));
        Assert.All(StoreApiFamilies.Gatekeeper.All, p => Assert.StartsWith("/apps/gatekeeper/api/", p));
    }

    /// <summary>The chains are in walk order and subsets of their family.</summary>
    [Fact]
    public void TheChainsAreInWalkOrder()
    {
        _out.WriteLine("rpc: " + string.Join(" → ", StoreApiFamilies.RpcEc.Chain));
        _out.WriteLine("spc: " + string.Join(" → ", StoreApiFamilies.SinglePageCheckout.Chain));
        _out.WriteLine("gate: " + string.Join(" → ", StoreApiFamilies.Gatekeeper.Gate));

        Assert.Equal(7, StoreApiFamilies.RpcEc.Chain.Count);
        Assert.Equal(6, StoreApiFamilies.SinglePageCheckout.Chain.Count);
        Assert.Equal(6, StoreApiFamilies.Gatekeeper.Gate.Count);

        Assert.All(StoreApiFamilies.RpcEc.Chain, p => Assert.Contains(p, StoreApiFamilies.RpcEc.All));
        Assert.All(StoreApiFamilies.SinglePageCheckout.Chain,
            p => Assert.Contains(p, StoreApiFamilies.SinglePageCheckout.All));
        Assert.All(StoreApiFamilies.Gatekeeper.Gate, p => Assert.Contains(p, StoreApiFamilies.Gatekeeper.All));

        // the gate starts at bootstrap and ends at the release
        Assert.Equal(StoreApiFamilies.Gatekeeper.Bootstrap, StoreApiFamilies.Gatekeeper.Gate[0]);
        Assert.Equal(StoreApiFamilies.Gatekeeper.ReleaseDetails, StoreApiFamilies.Gatekeeper.Gate[^1]);
    }

    /// <summary>
    /// The gate's token exchange is the whole point: bootstrap → challenge → render → token →
    /// validate. A flow that has the cart paths but not these gets 403s.
    /// </summary>
    [Fact]
    public void TheGateTokenExchangeIsRecorded()
    {
        Assert.Equal("/apps/gatekeeper/api/gatekeeper-token?", StoreApiFamilies.Gatekeeper.Token);
        Assert.Equal("/apps/gatekeeper/api/render-token?", StoreApiFamilies.Gatekeeper.RenderToken);
        Assert.Equal("/apps/gatekeeper/api/validate-gatekeeper-token?",
            StoreApiFamilies.Gatekeeper.ValidateToken);
        Assert.Equal("/apps/gatekeeper/api/interaction-challenge/create?",
            StoreApiFamilies.Gatekeeper.CreateChallenge);

        Assert.True(StoreApiFamilies.IsKnown(StoreApiFamilies.Gatekeeper.Token));
        Assert.False(StoreApiFamilies.IsKnown("/apps/gatekeeper/api/nope"));
        Assert.False(StoreApiFamilies.IsKnown(null));
    }

    /// <summary>
    /// The audit endpoints carry the shop as a query parameter — the same two events R96 saw as
    /// <c>/api/audit-events/*</c>. They are telemetry, not checkout: a flow must not gate on them.
    /// </summary>
    [Fact]
    public void TheAuditEndpointsAreTelemetry()
    {
        Assert.Contains("cart-add?shop=", StoreApiFamilies.Gatekeeper.AuditCartAdd);
        Assert.Contains("checkout-behaviour?shop=", StoreApiFamilies.Gatekeeper.AuditCheckoutBehaviour);

        // telemetry is not part of the gate chain
        Assert.DoesNotContain(StoreApiFamilies.Gatekeeper.AuditCartAdd, StoreApiFamilies.Gatekeeper.Gate);
        Assert.DoesNotContain(StoreApiFamilies.Gatekeeper.AuditCheckoutBehaviour,
            StoreApiFamilies.Gatekeeper.Gate);
    }
}
