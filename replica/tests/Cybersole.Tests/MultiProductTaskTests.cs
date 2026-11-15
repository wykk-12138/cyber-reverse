using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// One task can carry several products.
///
/// The original's task creator has an "Add Input" row on its Cart tab (observed in the live UI,
/// round 94), so a single task monitors more than one URL. The replica only ever had the single
/// <c>BotTask.Product</c>; round 95 added <c>ExtraProducts</c> and made the engine poll them
/// round-robin.
///
/// The risk this test guards is the shape of the change: <c>Product</c> had to stay as the
/// primary entry so every existing consumer kept working, and <c>AllProducts</c> is the accessor
/// that callers should use when they want the whole set.
/// </summary>
public class MultiProductTaskTests
{
    private readonly ITestOutputHelper _out;
    public MultiProductTaskTests(ITestOutputHelper output) => _out = output;

    private static Product P(string name, string url) => new() { Name = name, Url = url };

    [Fact]
    public void ASingleProductTaskStillReportsExactlyOne()
    {
        var task = new BotTask { Product = P("one", "https://a/x") };

        Assert.Empty(task.ExtraProducts);
        Assert.Single(task.AllProducts);
        Assert.Same(task.Product, task.AllProducts[0]);
    }

    [Fact]
    public void ExtraProductsComeAfterThePrimary()
    {
        var task = new BotTask { Product = P("first", "https://a/1") };
        task.ExtraProducts.Add(P("second", "https://a/2"));
        task.ExtraProducts.Add(P("third", "https://a/3"));

        var all = task.AllProducts;

        _out.WriteLine("order: " + string.Join(" -> ", all.Select(p => p.Name)));
        Assert.Equal(3, all.Count);
        Assert.Equal(new[] { "first", "second", "third" }, all.Select(p => p.Name));
    }

    /// <summary>
    /// The engine indexes into AllProducts with a modulo, so the accessor must never return an
    /// empty list — a task with a null Product still has to produce one entry to poll.
    /// </summary>
    [Fact]
    public void AllProductsIsNeverEmpty()
    {
        var task = new BotTask();

        Assert.NotNull(task.Product);
        Assert.NotEmpty(task.AllProducts);
    }

    [Fact]
    public void TheRoundRobinCoversEveryProduct()
    {
        var task = new BotTask { Product = P("a", "https://a/1") };
        task.ExtraProducts.Add(P("b", "https://a/2"));
        task.ExtraProducts.Add(P("c", "https://a/3"));

        var products = task.AllProducts;
        var visited = new List<string>();

        // mirror TaskEngine's indexing
        for (var i = 0; i < 7; i++)
            visited.Add(products[i % products.Count].Name);

        _out.WriteLine("visits: " + string.Join(",", visited));

        Assert.Equal(new[] { "a", "b", "c", "a", "b", "c", "a" }, visited);
    }
}
