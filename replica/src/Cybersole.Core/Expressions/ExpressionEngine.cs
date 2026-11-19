using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

namespace Cybersole.Core.Expressions;

/// <summary>
/// Tiny template/expression engine for bulk profile generation and CSV columns
/// (Cybersole.Ui.Views.Profiles.Modals.ExpressionView + ExpressionExample).
///
/// Syntax: <c>{name}</c> for variables, <c>{func(args)}</c> for built-ins. A leading
/// <c>{{</c> escapes a literal brace. Unknown names are left untouched so a partially filled
/// row is visible instead of silently blank.
/// </summary>
public static class ExpressionEngine
{
    private static readonly Regex Token = new(@"\{([^{}]+)\}", RegexOptions.Compiled);

    /// <summary>Built-in functions with their arity and implementation.</summary>
    public static IReadOnlyList<ExpressionExample> Examples { get; } = new[]
    {
        new ExpressionExample { Key = "random(min,max)", Description = "Random integer in [min, max)." },
        new ExpressionExample { Key = "randomInt(digits)", Description = "Random integer with N digits." },
        new ExpressionExample { Key = "alnum(length)", Description = "Random alphanumeric string." },
        new ExpressionExample { Key = "alpha(length)", Description = "Random letters." },
        new ExpressionExample { Key = "uuid()", Description = "A fresh GUID (no dashes)." },
        new ExpressionExample { Key = "email(domain)", Description = "Random local part @ domain." },
        new ExpressionExample { Key = "now(format)", Description = "UTC now in the given format." },
        new ExpressionExample { Key = "sequence(start)", Description = "Incrementing counter from start." },
        new ExpressionExample { Key = "upper(v)", Description = "Uppercase a value." },
        new ExpressionExample { Key = "lower(v)", Description = "Lowercase a value." },
        new ExpressionExample { Key = "pad(value,width)", Description = "Left-pad with zeroes." },
        new ExpressionExample { Key = "pick(a|b|c)", Description = "Pick one of the options." },
    };

    private static readonly Dictionary<int, int> SequenceCounters = new();

    /// <summary>Evaluate a template against a variable bag. Deterministic when <paramref name="seed"/> is set.</summary>
    public static string Evaluate(string template, IReadOnlyDictionary<string, string>? vars = null,
        int? seed = null)
    {
        if (string.IsNullOrEmpty(template)) return string.Empty;

        var rng = seed is { } s ? new Random(s) : Random.Shared;

        // Protect escaped braces with a sentinel, then restore at the end.
        var work = template.Replace("{{", "\u0001").Replace("}}", "\u0002");

        var result = Token.Replace(work, m =>
        {
            var body = m.Groups[1].Value.Trim();

            if (vars is not null && vars.TryGetValue(body, out var v)) return v;

            var call = ParseCall(body);
            if (call is not null) return Apply(call.Value.Name, call.Value.Args, rng);

            return string.Empty;
        });

        return result.Replace("\u0001", "{").Replace("\u0002", "}");
    }

    private static (string Name, string[] Args)? ParseCall(string body)
    {
        var open = body.IndexOf('(');
        if (open <= 0 || !body.EndsWith(")", StringComparison.Ordinal)) return null;

        var name = body[..open].Trim();
        var inner = body[(open + 1)..^1];
        var args = inner.Length == 0
            ? Array.Empty<string>()
            : inner.Split(',').Select(a => a.Trim()).ToArray();
        return (name, args);
    }

    private static string Apply(string name, string[] args, Random rng)
    {
        static int IntArg(string[] a, int i, int fallback) =>
            i < a.Length && int.TryParse(a[i], CultureInfo.InvariantCulture, out var v) ? v : fallback;

        switch (name.ToLowerInvariant())
        {
            case "random":
            {
                var min = IntArg(args, 0, 0);
                var max = IntArg(args, 1, 100);
                if (max <= min) max = min + 1;
                return rng.Next(min, max).ToString(CultureInfo.InvariantCulture);
            }
            case "randomint":
            {
                var digits = Math.Clamp(IntArg(args, 0, 6), 1, 12);
                var sb = new StringBuilder(digits);
                for (var i = 0; i < digits; i++) sb.Append((char)('0' + rng.Next(10)));
                return sb.ToString();
            }
            case "alnum":
                return RandomString(rng, Math.Clamp(IntArg(args, 0, 8), 1, 64), AlphaNumeric);
            case "alpha":
                return RandomString(rng, Math.Clamp(IntArg(args, 0, 8), 1, 64), Letters);
            case "uuid":
                return Guid.NewGuid().ToString("N");
            case "email":
            {
                var domain = args.Length > 0 && args[0].Length > 0 ? args[0] : "example.com";
                var local = RandomString(rng, 10, AlphaNumeric).ToLowerInvariant();
                return $"{local}@{domain}";
            }
            case "now":
            {
                var format = args.Length > 0 && args[0].Length > 0 ? args[0] : "yyyy-MM-dd";
                return DateTime.UtcNow.ToString(format, CultureInfo.InvariantCulture);
            }
            case "sequence":
            {
                var start = IntArg(args, 0, 1);
                var bucket = start * 31 + args.Length;
                SequenceCounters.TryGetValue(bucket, out var current);
                SequenceCounters[bucket] = current + 1;
                return (start + current).ToString(CultureInfo.InvariantCulture);
            }
            case "upper":
                return args.Length > 0 ? args[0].ToUpperInvariant() : string.Empty;
            case "lower":
                return args.Length > 0 ? args[0].ToLowerInvariant() : string.Empty;
            case "pad":
            {
                var value = args.Length > 0 ? args[0] : "0";
                var width = Math.Clamp(IntArg(args, 1, 4), 1, 32);
                return value.PadLeft(width, '0');
            }
            case "pick":
                return args.Length == 0
                    ? string.Empty
                    : args[rng.Next(args.Length)];
            default:
                return string.Format(CultureInfo.InvariantCulture, "{{{0}}}",
                    string.Join(",", new[] { name }.Concat(args)));
        }
    }

    private const string Letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private const string AlphaNumeric = Letters + "0123456789";

    private static string RandomString(Random rng, int length, string alphabet)
    {
        var sb = new StringBuilder(length);
        for (var i = 0; i < length; i++) sb.Append(alphabet[rng.Next(alphabet.Length)]);
        return sb.ToString();
    }

    /// <summary>Variables referenced by a template, in order of appearance.</summary>
    public static IReadOnlyList<string> Variables(string template)
    {
        if (string.IsNullOrEmpty(template)) return Array.Empty<string>();
        return Token.Matches(template.Replace("{{", "\u0001"))
            .Select(m => m.Groups[1].Value.Trim())
            .Where(body => body.Length > 0 && !body.Contains('('))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    /// <summary>True when every variable in the template has a value.</summary>
    public static bool IsSatisfied(string template, IReadOnlyDictionary<string, string> vars)
        => Variables(template).All(v => vars.ContainsKey(v));

    public static void ResetSequence() => SequenceCounters.Clear();
}

/// <summary>One documented expression (Cybersole.Ui.Views.Profiles.Modals.ExpressionExample).</summary>
public sealed class ExpressionExample
{
    public string Key { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;

    /// <summary>Sample output rendered in the expression panel.</summary>
    /// <remarks>
    /// R1193: the original binds ExpressionExample.Output with a Getter and a Setter. The rendered sample stays the
    /// default reading - the override is consulted only after a binding writes to it - so the panel shows exactly
    /// what it showed before unless something assigns. What the original stores on assignment is Unknown.
    /// </remarks>
    private string? _outputOverride;

    public string Output
    {
        get => _outputOverride ?? ExpressionEngine.Evaluate(
            "{" + Key + "}",
            new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase));
        set => _outputOverride = value;
    }
}
