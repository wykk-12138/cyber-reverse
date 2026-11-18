using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using Cybersole.Stores.Actions;
using Cybersole.Stores.Flows;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R1142: which of John Lewis's nineteen steps the flow actually implements.
///
/// Every step name in the image's list must be dispatchable — that is the runner's contract — and a
/// store that runs the step must override it, otherwise the base class answers with a refusal and the
/// step silently does nothing. This turns "all nineteen are covered" from a claim into a checked fact,
/// and names the exceptions instead of counting them.
/// </summary>
public sealed class JohnLewisStepCoverageTests
{
    private readonly ITestOutputHelper _out;

    public JohnLewisStepCoverageTests(ITestOutputHelper output) => _out = output;

    /// <summary>
    /// R1142: exactly one step stays on the base class. R1140 found one function issuing the orders
    /// URL while the map names two steps for it, so PlaceOrder owns the call and SubmitOrder is left
    /// alone rather than posting to the endpoint it used to invent. Named, not counted: a count would
    /// let a swap slip through.
    /// </summary>
    private static readonly string[] DeliberatelyNotImplemented = { "SubmitOrder" };

    [Fact]
    public void EveryImageStepIsDispatchable()
    {
        var known = StoreFlowSteps.JohnLewis.Names.Where(n => !StepActionRunner.Knows(n)).ToList();
        Assert.Empty(known);
    }

    [Fact]
    public void EveryStepIsEitherOverriddenOrNamedAsAnException()
    {
        var flowType = typeof(JohnLewisFlow);

        var overridden = new List<string>();
        var notOverridden = new List<string>();
        foreach (var name in StoreFlowSteps.JohnLewis.Names)
        {
            var method = flowType.GetMethod(name + "Async");
            var declared = method is not null && method.DeclaringType == flowType;
            (declared ? overridden : notOverridden).Add(name);
        }

        _out.WriteLine($"overridden ({overridden.Count}): {string.Join(", ", overridden)}");
        _out.WriteLine($"not overridden ({notOverridden.Count}): {string.Join(", ", notOverridden)}");

        // The exceptions are named, not counted: a count would let a swap slip through unnoticed.
        Assert.Equal(
            DeliberatelyNotImplemented.OrderBy(n => n, StringComparer.Ordinal),
            notOverridden.OrderBy(n => n, StringComparer.Ordinal));
    }
}
