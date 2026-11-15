using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The UI layer must pin its continuations.
///
/// Round 121: a licence check reported "Call from invalid thread" — not its own failure, but a
/// different subscriber writing a ListBox from a pool thread and throwing back through the HTTP
/// call. Round 122: the sign-in dialog overwrote its own error message for the same reason.
///
/// Services deliberately await with ConfigureAwait(false) (73 occurrences) because they must not
/// care about a UI thread. Anything in Cybersole.Ui that awaits one of those without saying
/// ConfigureAwait(true) inherits a pool-thread continuation.
///
/// Two shapes are exempt:
///   * `someEvent += async (_, _) => await Handler();` — the lambda is an entry point; its
///     continuation context is the one it was invoked on, so it is already correct.
///   * awaits of methods declared in this same assembly that already pin internally.
/// </summary>
public class UiContinuationTests
{
    private readonly ITestOutputHelper _out;
    public UiContinuationTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir is not null && !Directory.Exists(Path.Combine(dir, "src")))
            dir = Path.GetDirectoryName(dir);

        Assert.NotNull(dir);
        return dir;
    }

    /// <summary>
    /// Returns every `await …` statement in <paramref name="source"/> that has no ConfigureAwait,
    /// as (line, text). A statement ends at the first `;` at the same paren depth.
    /// </summary>
    private static IEnumerable<(int Line, string Text)> BareAwaits(string source)
    {
        var i = 0;
        while ((i = source.IndexOf("await ", i, StringComparison.Ordinal)) >= 0)
        {
            var start = i;
            i += "await ".Length;

            // walk to the terminating semicolon, tracking parens/braces so an argument list
            // spanning several lines is not mistaken for the end of the statement
            var depth = 0;
            var j = i;
            while (j < source.Length)
            {
                var c = source[j];
                if (c is '(' or '[' or '{') depth++;
                else if (c is ')' or ']' or '}') { if (depth == 0) break; depth--; }
                else if (c == ';' && depth == 0) break;
                j++;
            }

            var text = source[start..Math.Min(j, source.Length)];
            var line = source[..start].Count(c => c == '\n') + 1;

            // an event handler entry point: `async (…) => await X();`
            var lineStart = source.LastIndexOf('\n', Math.Min(start, source.Length - 1)) + 1;
            var prefix = source[lineStart..start];
            var isEntryPoint = Regex.IsMatch(prefix, @"async\s*\([^)]*\)\s*=>\s*$");

            if (!isEntryPoint && !text.Contains("ConfigureAwait"))
                yield return (line, text.Replace('\n', ' ').Replace("  ", " ").Trim());
        }
    }

    [Fact]
    public void UiAwaitsPinTheirContinuation()
    {
        var root = Path.Combine(RepoRoot(), "src", "Cybersole.Ui");
        var hits = new List<string>();

        // Only cross-layer calls matter. Awaits of Task.CompletedTask, of Avalonia's ShowDialog
        // (which round 121 proved returns on the UI thread by observing "3DS code captured"), or
        // of a method in this same assembly all resume where they were invoked.
        var crossLayer = new Regex(@"await\s+(_?services|_services\.\w+|sp|Clipboard)\b");

        foreach (var file in Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
        {
            var rel = Path.GetRelativePath(root, file).Replace('\\', '/');
            if (rel.Contains("/obj/") || rel.Contains("/bin/")) continue;

            foreach (var (line, text) in BareAwaits(File.ReadAllText(file)))
            {
                if (!crossLayer.IsMatch(text)) continue;

                // this one pins internally and is called from two UI handlers
                if (text.Contains("ImportFromFileAsync")) continue;

                hits.Add($"{rel}:{line}  {text}");
            }
        }

        _out.WriteLine($"bare cross-layer awaits: {hits.Count}");
        foreach (var h in hits) _out.WriteLine("  " + h);

        Assert.Empty(hits);
    }
}
