using Cybersole.Core.Models;

namespace Cybersole.Services;

/// <summary>
/// Parsing helpers shared by the import dialogs (accounts / proxies / sizes).
/// Kept out of the windows so the format rules are unit-tested.
/// </summary>
public static class ImportParser
{
    /// <summary>Parse "email:password" / "email,password" / "email|password" lines.</summary>
    public static IReadOnlyList<(string Email, string Password)> ParseAccounts(string? text)
    {
        var result = new List<(string, string)>();
        if (string.IsNullOrWhiteSpace(text)) return result;

        foreach (var raw in text.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            var line = raw.Trim();
            if (line.StartsWith('#') || line.StartsWith("//")) continue;

            var parts = line.Split(new[] { ':', ',', '|' }, 2, StringSplitOptions.TrimEntries);
            if (parts.Length != 2) continue;
            if (!parts[0].Contains('@')) continue;
            if (string.IsNullOrWhiteSpace(parts[1])) continue;

            result.Add((parts[0], parts[1]));
        }
        return result;
    }

    /// <summary>Parse proxy lines (host:port / host:port:user:pass / scheme://...).</summary>
    public static IReadOnlyList<Proxy> ParseProxies(string? text)
    {
        var result = new List<Proxy>();
        if (string.IsNullOrWhiteSpace(text)) return result;

        foreach (var raw in text.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            var line = raw.Trim();
            if (line.StartsWith('#') || line.StartsWith("//")) continue;

            if (!line.Contains(':')) continue;

            var proxy = Proxy.Parse(line);
            if (string.IsNullOrWhiteSpace(proxy.Host) || proxy.Port <= 0) continue;
            result.Add(proxy);
        }
        return result;
    }

    /// <summary>Parse a size list ("9, 10, 10.5" / "9;10;10.5" / whitespace separated).</summary>
    public static IReadOnlyList<string> ParseSizes(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return Array.Empty<string>();
        return text
            .Split(new[] { ',', ';', ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }
}
