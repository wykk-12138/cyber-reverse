using System;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R445: `checkoutHistory.json` is the one document in the original's data directory that is **PascalCase**,
/// while every other one (`settings`, `tasks`, `solvers`, `accounts`, `proxies`) is camelCase — measured by
/// reading `%APPDATA%\Cybersole` (read-only):
///
/// <code>
/// settings.json        keys: bearer, license, quickTaskProxies, ...
/// checkoutHistory.json keys: Store, Product, Size, Price, Success, OrderNumber, Profile, At, TrackingUrl
/// </code>
///
/// <para>
/// The replica matches by luck of implementation detail, not by design: `CheckoutStats` writes through
/// <c>JsonConvert.SerializeObject(events)</c> with **no settings**, which defaults to PascalCase, whereas the
/// shared <c>Json.Default</c> resolver applies <c>CamelCaseNamingStrategy</c>. If anyone "tidies" that call to
/// use <c>Json.Serialize</c>, the file silently changes shape and nothing today would notice.
/// </para>
/// <para>
/// So the pin is the key set, copied from the original's own file.
/// </para>
/// </summary>
public sealed class CheckoutHistoryShapeTests
{
    private readonly ITestOutputHelper _out;

    public CheckoutHistoryShapeTests(ITestOutputHelper output) => _out = output;

    /// <summary>The nine keys the original's own checkoutHistory.json carries, alphabetised.</summary>
    private static readonly string[] OriginalKeys =
    {
        "At", "OrderNumber", "Price", "Product", "Profile", "Size", "Store", "Success", "TrackingUrl",
    };

    private static Cybersole.Core.Store.CheckoutEvent Sample() =>
        new("Nike", "Air Max 90", "10.5", "150.00", true, "ORD-1", "Profile A")
        {
            At = new DateTime(2026, 11, 14, 9, 30, 0, DateTimeKind.Utc),
            TrackingUrl = "https://example.invalid/track",
        };

    [Fact]
    public void TheHistoryEntrySerialisesWithTheImagesKeyNames()
    {
        var json = JsonConvert.SerializeObject(new[] { Sample() });

        var keys = JArray.Parse(json)[0]
            .Children<JProperty>()
            .Select(p => p.Name)
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToArray();

        _out.WriteLine(string.Join(", ", keys));
        Assert.Equal(OriginalKeys, keys);
    }

    [Fact]
    public void TheWriterUsesTheDefaultResolver_NotTheCamelCaseOne()
    {
        // First attempt at this guard compared the two resolvers' *outputs* — which proves the shapes differ
        // but says nothing about which one CheckoutStats actually calls, so switching the writer to
        // `Json.Serialize` would have left the test green. This asserts the call site instead.
        var dir = new System.IO.DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !System.IO.File.Exists(System.IO.Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);

        var path = System.IO.Path.Combine(dir!.FullName, "src", "Cybersole.Services", "CheckoutStats.cs");
        Assert.True(System.IO.File.Exists(path), "CheckoutStats.cs moved — update this guard");
        var source = System.IO.File.ReadAllText(path);
        var code = System.Text.RegularExpressions.Regex.Replace(source, @"(?<!:)//[^\n]*", " ");

        Assert.Contains("JsonConvert.SerializeObject(_events)", code);
        Assert.DoesNotContain("Json.Serialize", code);   // the camelCase resolver must not be used here
        _out.WriteLine("CheckoutStats writes with the default (PascalCase) resolver");

        // and the shapes really are different, so the assertion above is worth making
        var camel = Cybersole.Core.Store.Json.Serialize(new[] { Sample() });
        var actual = JsonConvert.SerializeObject(new[] { Sample() });
        Assert.Contains("\"store\"", camel);
        Assert.Contains("\"Store\"", actual);
    }
}
