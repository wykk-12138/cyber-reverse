using System;
using System.Linq;
using Cybersole.Stores.Flows;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The task-kind axis added in R880: fourteen flow kinds and two task kinds, every one of them traceable to a line in
/// the baseline inventory.
///
/// <para>
/// These tests exist because the counts are the whole point of the type. R857 said five kinds from one code region and
/// that number survived twenty-odd rounds unexamined, precisely because the conclusion around it was right. A test that
/// asserts fourteen fails loudly if someone adds a kind from memory or trims one that looks redundant.
/// </para>
/// </summary>
public class TaskKindTests
{
    /// <summary>
    /// Fourteen, not five. The number comes from <c>recovered_async_methods.txt</c>, which holds every async method
    /// name in the image, and each of these appears there exactly once as a <c>Start*Flow</c>.
    /// </summary>
    [Fact]
    public void ThereAreFourteenFlowKinds()
    {
        Assert.Equal(14, TaskKindCatalog.FlowKinds.Count);
        Assert.Equal(14, Enum.GetValues<FlowKind>().Length);
    }

    /// <summary>
    /// Two task kinds, kept separate from the flow kinds because the image's own names distinguish them. Merging would
    /// be the error R877 resolved, where storeOfflineDraw and drawScratch looked like one family and turned out to
    /// serve different things.
    /// </summary>
    [Fact]
    public void ThereAreTwoTaskKinds()
    {
        Assert.Equal(2, TaskKindCatalog.TaskKinds.Count);
        Assert.Equal(2, Enum.GetValues<TaskKind>().Length);
    }

    /// <summary>
    /// Every declared member resolves to an image name and back. A member with no name would be one I invented, which
    /// is the failure mode R876 committed in prose and R878 retracted.
    /// </summary>
    [Fact]
    public void EveryMemberHasAnImageNameAndResolvesBackToItself()
    {
        foreach (var kind in Enum.GetValues<FlowKind>())
        {
            var name = TaskKindCatalog.ImageName(kind);
            Assert.False(string.IsNullOrEmpty(name), kind + " has no image name");
            Assert.StartsWith("Start", name!);
            Assert.EndsWith("Flow", name!);

            var (flow, task) = TaskKindCatalog.Resolve(name!);
            Assert.Equal(kind, flow);
            Assert.Null(task);
        }

        foreach (var kind in Enum.GetValues<TaskKind>())
        {
            var name = TaskKindCatalog.ImageName(kind);
            Assert.False(string.IsNullOrEmpty(name), kind + " has no image name");
            Assert.EndsWith("Task", name!);

            var (flow, task) = TaskKindCatalog.Resolve(name!);
            Assert.Equal(kind, task);
            Assert.Null(flow);
        }
    }

    /// <summary>
    /// The names are distinct, so resolution is unambiguous. A duplicate would make <see cref="TaskKindCatalog.Resolve"/>
    /// return whichever came first while looking authoritative.
    /// </summary>
    [Fact]
    public void TheImageNamesAreDistinct()
    {
        var all = Enum.GetValues<FlowKind>().Select(k => TaskKindCatalog.ImageName(k))
            .Concat(Enum.GetValues<TaskKind>().Select(k => TaskKindCatalog.ImageName(k)))
            .ToList();

        Assert.Equal(16, all.Count);
        Assert.Equal(16, all.Distinct(StringComparer.Ordinal).Count());
    }

    /// <summary>
    /// A name the catalog does not claim resolves to nothing rather than to a near match. This is the guard against
    /// the adjacency habit: an unknown name must not be answered with the closest-looking member.
    /// </summary>
    [Fact]
    public void AnUnclaimedNameResolvesToNothing()
    {
        var (flow, task) = TaskKindCatalog.Resolve("StartSomethingNobodyFoundFlow");
        Assert.Null(flow);
        Assert.Null(task);
    }

    /// <summary>
    /// The two kinds the replica can currently drive end to end are the ones whose flows declare a sequence. Asserting
    /// the pairing keeps the axis tied to something real instead of floating free as a list of strings.
    /// </summary>
    [Fact]
    public void TheKindAxisIsNotYetWiredToAnyFlow()
    {
        // Nothing in the replica maps a FlowKind to a StoreFlow yet. That is the next piece of work, and asserting the
        // absence keeps it visible rather than letting the catalog look like an integrated feature.
        var mappingExists = typeof(TaskKindCatalog)
            .GetMethods()
            .Any(m => m.Name.Contains("For", StringComparison.Ordinal) || m.Name.Contains("Map", StringComparison.Ordinal));

        Assert.False(mappingExists, "if a FlowKind-to-StoreFlow mapping has been added, replace this test with one that pins it");
    }
}
