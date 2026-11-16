using System.Text;
using Cybersole.Core.Store;

namespace Cybersole.Services;

/// <summary>
/// CSV export for the analytics page (mirrors the original's ability to dump
/// checkout history for spreadsheets).
/// </summary>
public static class ExportService
{
    private static readonly string[] Header =
    {
        "timestamp", "store", "product", "size", "price", "success", "order", "profile",
    };

    /// <summary>Build a CSV document from checkout events (RFC 4180 quoting).</summary>
    public static string BuildCheckoutCsv(IEnumerable<CheckoutEvent> events)
    {
        var sb = new StringBuilder();
        sb.AppendLine(string.Join(',', Header));

        foreach (var e in events)
        {
            sb.AppendLine(string.Join(',',
                Quote(DateTime.UtcNow.ToString("O")),
                Quote(e.Store),
                Quote(e.Product),
                Quote(e.Size),
                Quote(e.Price),
                e.Success ? "true" : "false",
                Quote(e.OrderNumber ?? string.Empty),
                Quote(e.Profile)));
        }

        return sb.ToString();
    }

    /// <summary>Write the CSV into the app data directory and return the full path.</summary>
    public static string ExportToFile(IEnumerable<CheckoutEvent> events, string directory)
    {
        Directory.CreateDirectory(directory);
        var path = Path.Combine(directory, $"checkouts-{DateTime.Now:yyyyMMdd-HHmmss}.csv");
        File.WriteAllText(path, BuildCheckoutCsv(events), Encoding.UTF8);
        return path;
    }

    private static string Quote(string value)
    {
        if (value.Contains('"') || value.Contains(',') || value.Contains('\n') || value.Contains('\r'))
            return "\"" + value.Replace("\"", "\"\"") + "\"";
        return value;
    }
}
