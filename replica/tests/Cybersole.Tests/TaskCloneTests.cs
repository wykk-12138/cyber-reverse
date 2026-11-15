using Cybersole.Core;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 60: <c>TaskGroups.Context.CloneFormat</c> ("Clone {0}") had a button-shaped hole — there
/// was a Delete, a Pin and a New, and no Clone. Producing one needed a task copy, which did not
/// exist either.
///
/// These tests pin what a clone carries and what it deliberately does not.
/// </summary>
public sealed class TaskCloneTests
{
    private readonly ITestOutputHelper _out;

    public TaskCloneTests(ITestOutputHelper output) => _out = output;

    private static BotTask MakeTask() => new()
    {
        Name = "Nike Dunk",
        Store = "nike",
        GroupId = "g1",
        ProfileId = "p1",
        ProxyGroupId = "x1",
        AccountId = "a1",
        Quantity = 3,
        MonitorMode = true,
        CheckoutDelay = 250,
        MonitorDelay = 1500,
        RetryDelay = 900,
        Timeout = 30,
        State = TaskState.Success,
        StartTime = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
        Product = new Product
        {
            Name = "Dunk Low",
            Url = "https://www.nike.com/t/dunk",
            Price = "110",
            Sizes = { "9", "10" },
        },
        ExtraProducts = { new Product { Name = "Air Max", Url = "https://www.nike.com/t/airmax" } },
    };

    /// <summary>Configuration travels; the run does not.</summary>
    [Fact]
    public void ACloneCopiesConfigurationButNotState()
    {
        var original = MakeTask();
        var clone = original.Clone();

        _out.WriteLine($"id: {original.Id} -> {clone.Id}");
        _out.WriteLine($"state: {original.State} -> {clone.State}");
        _out.WriteLine($"start: {original.StartTime:u} -> {(clone.StartTime is null ? "(none)" : clone.StartTime.ToString())}");

        Assert.NotEqual(original.Id, clone.Id);
        Assert.Equal(TaskState.Idle, clone.State);
        Assert.Null(clone.StartTime);

        Assert.Equal(original.Name, clone.Name);
        Assert.Equal(original.Store, clone.Store);
        Assert.Equal(original.Quantity, clone.Quantity);
        Assert.Equal(original.MonitorDelay, clone.MonitorDelay);
        Assert.Equal(original.RetryDelay, clone.RetryDelay);
        Assert.Equal(original.Timeout, clone.Timeout);
        Assert.Equal(original.ProfileId, clone.ProfileId);
        Assert.Equal(original.ProxyGroupId, clone.ProxyGroupId);
        Assert.Equal(original.AccountId, clone.AccountId);
    }

    /// <summary>
    /// The product is deep-copied. Two tasks sharing one <c>Product</c> instance would overwrite
    /// each other's detected price and variant during monitoring.
    /// </summary>
    [Fact]
    public void TheProductIsNotShared()
    {
        var original = MakeTask();
        var clone = original.Clone();

        _out.WriteLine($"same product instance: {ReferenceEquals(original.Product, clone.Product)}");

        Assert.NotSame(original.Product, clone.Product);
        Assert.Equal(original.Product.Name, clone.Product.Name);
        Assert.Equal(original.Product.Url, clone.Product.Url);

        // Sizes must be a separate list too, or editing one changes both.
        Assert.NotSame(original.Product.Sizes, clone.Product.Sizes);
        Assert.Equal(original.Product.Sizes, clone.Product.Sizes);

        // Mutating the clone must leave the original alone.
        clone.Product.Price = "999";
        _out.WriteLine($"original price after clone edit: {original.Product.Price}");
        Assert.Equal("110", original.Product.Price);
    }

    /// <summary>Extra products are copied one by one, not shared by reference.</summary>
    [Fact]
    public void ExtraProductsAreCopied()
    {
        var original = MakeTask();
        var clone = original.Clone();

        _out.WriteLine($"extra count: {original.ExtraProducts.Count} -> {clone.ExtraProducts.Count}");
        Assert.Equal(original.ExtraProducts.Count, clone.ExtraProducts.Count);
        Assert.NotSame(original.ExtraProducts[0], clone.ExtraProducts[0]);
        Assert.Equal(original.ExtraProducts[0].Name, clone.ExtraProducts[0].Name);
    }

    /// <summary>
    /// A group clone starts with no counters. This is the TaskGroup-level half of the same rule:
    /// copying TotalCheckouts would make a brand-new group claim it had already landed orders.
    /// </summary>
    [Fact]
    public void AGroupCloneStartsWithNoCounters()
    {
        var group = new TaskGroup { Name = "G", UsageExpiry = TimeSpans.OneDay };
        group.TotalCheckouts = 12;
        group.TotalDeclines = 4;
        group.Tasks.Add(MakeTask());

        // The clone block in TasksViews copies configuration only; this asserts the model's
        // defaults, which is what that block relies on.
        var clone = new TaskGroup { Name = "G (copy)", UsageExpiry = group.UsageExpiry };
        foreach (var task in group.Tasks) clone.Tasks.Add(task.Clone());

        _out.WriteLine($"counters: {group.TotalCheckouts}/{group.TotalDeclines} -> " +
                       $"{clone.TotalCheckouts}/{clone.TotalDeclines}");
        _out.WriteLine($"tasks: {group.Tasks.Count} -> {clone.Tasks.Count}");

        Assert.Equal(12, group.TotalCheckouts);
        Assert.Equal(0, clone.TotalCheckouts);
        Assert.Equal(0, clone.TotalDeclines);
        Assert.Single(clone.Tasks);
        Assert.NotEqual(group.Tasks[0].Id, clone.Tasks[0].Id);
    }
}
