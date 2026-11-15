namespace Cybersole.Core.Models;

/// <summary>
/// The size chips shown in the task editor: a standard US/EU ladder plus whatever the user
/// added under settings.customSizes. Kept out of the UI so it can be unit-tested.
/// </summary>
public static class SizePalette
{
    /// <summary>Standard US men's run used by every sneaker store module.</summary>
    public static readonly IReadOnlyList<string> Standard = new[]
    {
        "4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5",
        "9", "9.5", "10", "10.5", "11", "11.5", "12", "12.5", "13", "14",
    };

    /// <summary>Standard ladder followed by user sizes, de-duplicated, order preserved.</summary>
    public static IReadOnlyList<string> Build(IEnumerable<string>? customSizes)
    {
        var result = new List<string>(Standard);
        var seen = new HashSet<string>(Standard, StringComparer.OrdinalIgnoreCase);

        if (customSizes is null) return result;

        foreach (var raw in customSizes)
        {
            var size = Normalise(raw);
            if (size.Length == 0) continue;
            if (seen.Add(size)) result.Add(size);
        }

        return result;
    }

    /// <summary>Trims and drops a trailing ".0" so "10.0" and "10" are the same chip.</summary>
    public static string Normalise(string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) return string.Empty;

        var size = value.Trim();
        if (size.EndsWith(".0", StringComparison.Ordinal) && size.Length > 2)
            size = size[..^2];
        return size;
    }

    /// <summary>True when the value is a plausible shoe size (keeps typos out of custom sizes).</summary>
    public static bool IsValid(string? value)
    {
        var size = Normalise(value);
        if (size.Length == 0 || size.Length > 6) return false;
        return size.All(c => char.IsDigit(c) || c is '.' or '½' or '/');
    }
}
