using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 116: Pop Mart's twenty-four steps against its thirty-nine endpoints.
///
/// <para>
/// The largest step/endpoint pair in the image, and the first one where the <b>gaps are data</b>:
/// fourteen pairs are drawn where the nouns agree, and the ten steps and twenty-five endpoints that
/// are left over are recorded as lists rather than quietly dropped.
/// </para>
///
/// <para>
/// The discipline is R115's: name correlation, not capture — and the label is asserted here so it
/// cannot be removed without a test failing.
/// </para>
/// </summary>
public sealed class PopMartStepMapTests
{
    private readonly ITestOutputHelper _out;

    public PopMartStepMapTests(ITestOutputHelper output) => _out = output;

    /// <summary>Fourteen pairs, and both sides of every pair are real names.</summary>
    [Fact]
    public void ThePairsPointAtRealStepsAndRealEndpoints()
    {
        Assert.Equal(14, PopMartStepMap.Pairs.Count);

        foreach (var (step, endpoint) in PopMartStepMap.Pairs)
        {
            Assert.True(StoreFlowSteps.IsStep(step), step);
            Assert.True(PopMartEndpoints.IsKnown(endpoint), endpoint);
            _out.WriteLine($"{step,-20} → {endpoint}");
        }
    }

    /// <summary>Step plus unmapped steps equals the flow; endpoint plus unmapped equals the family.</summary>
    [Fact]
    public void TheRemaindersAddUp()
    {
        var flow = StoreFlowSteps.PopMart.Names;
        var mapped = PopMartStepMap.MappedSteps;

        _out.WriteLine($"{mapped.Count} mapped + {PopMartStepMap.UnmappedSteps.Count} unmapped = {flow.Count} steps");
        Assert.Equal(flow.Count, mapped.Count + PopMartStepMap.UnmappedSteps.Count);

        var endpoints = PopMartEndpoints.All;
        var distinctTargets = PopMartStepMap.Pairs.Values.Distinct().Count();

        _out.WriteLine($"{distinctTargets} distinct endpoints used, {PopMartStepMap.UnmappedEndpoints.Count} unused");
        Assert.Equal(endpoints.Count, distinctTargets + PopMartStepMap.UnmappedEndpoints.Count);
    }

    /// <summary>The clearly-named pairs are the ones the names spell out.</summary>
    [Fact]
    public void TheObviousPairsAreTheObviousOnes()
    {
        Assert.Equal(PopMartEndpoints.DrawScratchDraw, PopMartStepMap.EndpointFor("EnterDraw"));
        Assert.Equal(PopMartEndpoints.DrawScratchChooseGoods, PopMartStepMap.EndpointFor("ChooseGoods"));
        Assert.Equal(PopMartEndpoints.LuckyPointsDraw, PopMartStepMap.EndpointFor("RedeemLuckPoints"));
        Assert.Equal(PopMartEndpoints.StoreTicketDates, PopMartStepMap.EndpointFor("FindDates"));
        Assert.Equal(PopMartEndpoints.OrderList, PopMartStepMap.EndpointFor("GetOrders"));

        Assert.Null(PopMartStepMap.EndpointFor("CheckResult"));
        Assert.Null(PopMartStepMap.EndpointFor(null));
    }

    /// <summary>
    /// The steps left unmapped are exactly the ones whose names do not settle it — recorded so a
    /// later capture has a checklist rather than a blank.
    /// </summary>
    [Fact]
    public void TheUnmappedStepsAreRecorded()
    {
        foreach (var step in PopMartStepMap.UnmappedSteps) _out.WriteLine("unmapped step: " + step);

        Assert.Contains("CheckResult", PopMartStepMap.UnmappedSteps);
        Assert.Contains("StartDrawCheckFlow", PopMartStepMap.UnmappedSteps);
        Assert.Contains("StartReservationFlow", PopMartStepMap.UnmappedSteps);
        Assert.False(string.IsNullOrEmpty(string.Join(",", PopMartStepMap.UnmappedSteps)));
    }

    /// <summary>The label says correlation, not capture.</summary>
    [Fact]
    public void TheMapSaysWhatItIs()
    {
        var evidence = PopMartStepMap.Evidence;

        Assert.Contains("name correlation", evidence);
        Assert.Contains("no request capture", evidence);
        Assert.Contains("unmapped", evidence);

        _out.WriteLine(evidence);
    }
}
