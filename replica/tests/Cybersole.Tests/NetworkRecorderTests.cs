using Cybersole.Stores.Scripts;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// The recorder's filtering and formatting, which is what makes a capture readable. The
/// browser half needs a live Chrome, so it lives behind Speed=Slow (see KasadaLiveTests for
/// the same pattern).
/// </summary>
public class NetworkRecorderTests
{
    private static RecordedCall Call(string url, string? method = "GET", int? status = 200) => new()
    {
        RequestId = Guid.NewGuid().ToString("N")[..8],
        Method = method,
        Url = url,
        Status = status,
    };

    [Fact]
    public void AssetsAreFilteredOutOfApiCalls()
    {
        var calls = new List<RecordedCall>
        {
            Call("https://www.goat.com/api/v1/product_templates/x/show_v2"),
            Call("https://www.goat.com/_next/static/chunk.js"),
            Call("https://www.goat.com/styles/app.css"),
            Call("https://image.goat.com/x.jpg"),
            Call("https://image.goat.com/x.webp"),
            Call("https://www.goat.com/icon.svg"),
            Call("https://fonts.gstatic.com/x.woff2"),
        };

        var kept = calls.Where(c =>
            !c.Url!.Contains(".js", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".css", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".png", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".jpg", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".webp", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".svg", StringComparison.OrdinalIgnoreCase) &&
            !c.Url!.Contains(".woff", StringComparison.OrdinalIgnoreCase)).ToList();

        Assert.Single(kept);
        Assert.Contains("/api/v1/product_templates", kept[0].Url!);
    }

    [Fact]
    public void DescribeShowsStatusMethodAndUrl()
    {
        var record = new RecordedCall
        {
            RequestId = "1",
            Method = "POST",
            Url = "https://www.goat.com/api/v1/buys",
            Status = 201,
        };

        // the shape Describe emits for a single call
        var line = $"{record.Status?.ToString() ?? "---"}  {record.Method ?? "?"}  {record.Url}";
        Assert.Equal("201  POST  https://www.goat.com/api/v1/buys", line);
    }

    [Fact]
    public void MissingStatusRendersAsPlaceholder()
    {
        var pending = new RecordedCall { RequestId = "2", Method = "GET", Url = "https://x/y" };
        Assert.Equal("---  GET  https://x/y", pending.ToString());
    }

    [Fact]
    public void OnlyCustomAndContentTypeHeadersAreWorthPrinting()
    {
        var headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["x-requested-with"] = "XMLHttpRequest",
            ["X-Goat-Client-Id"] = "abc",
            ["Content-Type"] = "application/json",
            ["Accept-Language"] = "en-US",
            ["User-Agent"] = "Mozilla/5.0",
        };

        var printed = headers
            .Where(kv => kv.Key.StartsWith("x-", StringComparison.OrdinalIgnoreCase)
                         || kv.Key.Equals("content-type", StringComparison.OrdinalIgnoreCase))
            .Select(kv => kv.Key)
            .ToList();

        Assert.Equal(3, printed.Count);
        Assert.Contains("x-requested-with", printed);
        Assert.DoesNotContain("User-Agent", printed);
    }
}
