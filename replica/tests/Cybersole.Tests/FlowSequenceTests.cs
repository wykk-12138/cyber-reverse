using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The step-sequence mechanism added in R868: a flow may declare the order it runs, and a step name can be
/// dispatched to the method that implements it.
///
/// <para>
/// This exists because of a structural finding rather than a feature request. R851 established that the replica
/// drove one generic twenty-one-step sequence for every flow while the image gives each flow its own — Nike
/// sixteen, Pop Mart twenty-four — and R866 that the fourteen Pop Mart draw steps therefore had nowhere to sit:
/// adding them to the generic list would make every store call them, and leaving them out would make them dead
/// code. These tests pin the two pieces that make that possible, so the mechanism cannot quietly regress to a
/// state where a sequence exists but cannot be run.
/// </para>
/// </summary>
public class FlowSequenceTests
{
    /// <summary>
    /// A flow that has not declared a sequence must report none, so the runner keeps its built-in list and the
    /// twenty-five flows that predate this mechanism behave exactly as before.
    /// </summary>
    [Fact]
    public void AFlowWithoutItsOwnSequenceReportsNone()
    {
        var flow = new ShopifyFlow();
        Assert.Empty(flow.StepSequence);
    }

    /// <summary>
    /// Pop Mart declares the image's twenty-four steps. The count is asserted rather than a prefix so that
    /// trimming the list — the cheapest way to make a parity number look better — cannot pass.
    /// </summary>
    [Fact]
    public void PopMartDeclaresTheImagesTwentyFourSteps()
    {
        var flow = new PopMartFlow();
        Assert.Equal(24, flow.StepSequence.Count);
        Assert.Equal(StoreFlowSteps.PopMart.Names, flow.StepSequence);
    }

    /// <summary>
    /// The sequence is the image's order, not an alphabetical or insertion-order accident. Two names whose
    /// ordinals are known — GetOrders at 104 and EnterReservation at 153 — must appear in that relative order.
    /// </summary>
    [Fact]
    public void PopMartSequenceFollowsTheImagesOrdinals()
    {
        var names = new PopMartFlow().StepSequence.ToList();
        Assert.Contains("GetOrders", names);
        Assert.Contains("EnterReservation", names);
        Assert.True(names.IndexOf("GetOrders") < names.IndexOf("EnterReservation"),
            "GetOrders (ordinal 104) must precede EnterReservation (ordinal 153)");
    }

    /// <summary>
    /// Dispatch reaches the inherited methods, not only the ones the flow overrides. GetHome is overridden by
    /// PopMart while SubmitBillingAddress comes from the base; both have to be callable for a sequence to run.
    /// </summary>
    [Fact]
    public void DispatchReachesBothOverriddenAndInheritedSteps()
    {
        var map = new PopMartFlow().StepDispatch;
        Assert.True(map.ContainsKey("GetHome"), "GetHome is overridden by PopMartFlow");
        Assert.True(map.ContainsKey("SubmitBillingAddress"), "SubmitBillingAddress is inherited from StoreFlow");
        Assert.True(map.ContainsKey("Init"), "Init is inherited from StoreFlow");
    }

    /// <summary>
    /// The dispatch table must not be empty — a reflection query that matches nothing would satisfy every
    /// ContainsKey assertion above if they were written the other way round, so the size is pinned loosely.
    /// </summary>
    [Fact]
    public void DispatchIsNotSilentlyEmpty()
    {
        var map = new PopMartFlow().StepDispatch;
        Assert.True(map.Count >= 150,
            "StoreFlow declares 165 virtual steps; a dispatch map of " + map.Count + " means the reflection query broke");
    }

    /// <summary>
    /// The measured gap: none of Pop Mart's twenty-four image steps shares a name with any of StoreFlow's 165 methods.
    ///
    /// <para>
    /// Asserting zero looks like asserting a failure, and it is — of the flow, not of the mechanism. Before this
    /// mechanism there was no way to state the gap as a number; R844 guessed at 22 of 130 by comparing names across two
    /// layers and had to hedge. This is the same comparison done where it means something: a step the image lists
    /// against a method the replica can actually invoke.
    /// </para>
    ///
    /// <para>
    /// The number going up is the work. When the draw steps are written this assertion will fail, and the fix is to
    /// change it to the new number and say what was added — not to delete it.
    /// </para>
    /// </summary>
    [Fact]
    public void NoPopMartImageStepIsDispatchableYet()
    {
        var flow = new PopMartFlow();
        var map = flow.StepDispatch;
        var implementable = flow.StepSequence.Count(map.ContainsKey);

        Assert.Equal(165, map.Count);
        Assert.Equal(24, flow.StepSequence.Count);
        Assert.Equal(0, implementable);
    }

    /// <summary>
    /// The dispatch table does reach the steps the replica genuinely has, so a zero above means the two name sets are
    /// disjoint rather than the table being empty. Without this, the test above would pass just as happily on a
    /// broken map.
    /// </summary>
    [Fact]
    public void TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint()
    {
        var map = new PopMartFlow().StepDispatch;
        Assert.True(map.ContainsKey("GetHome"));
        Assert.True(map.ContainsKey("AddToCart"));
        Assert.True(map.ContainsKey("SubmitOrder"));
    }
}
