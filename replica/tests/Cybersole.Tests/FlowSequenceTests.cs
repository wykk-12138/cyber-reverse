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
            "StoreFlow declares 166 virtual steps; a dispatch map of " + map.Count + " means the reflection query broke");
    }

    /// <summary>
    /// The measured gap, as a number that moves: one of Pop Mart's twenty-four image steps is dispatchable.
    ///
    /// <para>
    /// R871 raised this from zero by adding <c>GetOrders</c>, which R116 paired with
    /// <see cref="Cybersole.Stores.Flows.PopMartEndpoints.OrderList"/> by name and R849 confirmed exists. That is what
    /// the number is for: it went from 0 to 1 because a step was written, and it will go to 2 next time. When this
    /// assertion fails the fix is to write the new number in and say which step arrived — never to delete the
    /// assertion.
    /// </para>
    ///
    /// <para>
    /// It is a pair with <see cref="TheTableIsNotEmptyWhichIsWhyTheZeroAboveMeansDisjoint"/>: that one proves the map is
    /// populated, so this number measures the two name sets rather than the health of the reflection.
    /// </para>
    /// </summary>
    [Fact]
    public void OnePopMartImageStepIsDispatchable()
    {
        var flow = new PopMartFlow();
        var map = flow.StepDispatch;
        var implementable = flow.StepSequence.Count(map.ContainsKey);

        // R891 raised the map from 172 to 174 with GetInstoreOrdersAsync and FindProductInstoreAsync, and the
        // sequence's coverage from seven to eight.
        //
        // Eight rather than nine is the interesting number: FindProductInstore is implemented but is not one of the
        // twenty-four names in Pop Mart's sequence. It is ordinal 76, which sits in the earlier literal run R882 read
        // (56 through 77, the one holding the five Start-prefixed flows), while Pop Mart's own run starts at 104. So
        // implementing a step and the step being in this sequence are separate facts, and this test now pins both:
        // the coverage counts only names the sequence declares.
        // R908 added AddToCartBoxAsync, taking the map from 174 to 175. It is not one of Pop Mart's twenty-four
        // names either, so the sequence's coverage stays at eight: the image has the method and the flow does not
        // list it, the same split as FindProductInstore.
        //
        // R916 added RunShieldAsync, taking it to 176. Same split again: the image names RunShield at ordinal
        // eighteen in the payment class, and Pop Mart's twenty-four names do not include it, so implementable stays
        // at eight for the third time in a row. Three additions that raise the map and not the coverage is the
        // finding, not an accident of counting -- the image's step vocabulary is wider than any one flow's sequence.
        Assert.Equal(176, map.Count);
        Assert.Equal(24, flow.StepSequence.Count);
        Assert.Equal(8, implementable);
        Assert.True(flow.CanRunStep("GetOrders"), "GetOrders was added in R871");
        Assert.True(flow.CanRunStep("FindExhibit"), "FindExhibit was added in R872");
        Assert.True(flow.CanRunStep("EnterExhibit"), "EnterExhibit was added in R872");
        Assert.True(flow.CanRunStep("StartDrawFlow"), "StartDrawFlow was added in R873");
        Assert.True(flow.CanRunStep("FindDraw"), "FindDraw was added in R873");
        Assert.True(flow.CanRunStep("FindDates"), "FindDates was added in R873");
        Assert.True(flow.CanRunStep("FindTimeSlots"), "FindTimeSlots was added in R873");
        Assert.True(flow.CanRunStep("GetInstoreOrders"), "GetInstoreOrders was added in R891");
        Assert.True(flow.CanRunStep("FindProductInstore"), "FindProductInstore was added in R891 but is not in this sequence");
        Assert.DoesNotContain("FindProductInstore", flow.StepSequence);
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
