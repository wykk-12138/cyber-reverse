"""R1331: make "a document constant must have a production caller" a suite invariant."""

import io

PATH = 'replica/tests/Cybersole.Tests/GeneratedDocumentTests.cs'
text = io.open(PATH, encoding='utf-8').read()

if 'EveryDocumentConstantHasAProductionCaller' in text:
    raise SystemExit('guard already present')

block = '''
    /// <summary>
    /// A document with no caller is a document the replica cannot send.
    ///
    /// <para>
    /// R1329 found one by accident — CustomerCartDocument, declared in R1320 and referenced only from tests —
    /// and R1330 found two more of the same kind, one of which had been hiding a dropped shipping rate id.
    /// The scan now runs in the suite so the next one is caught when it is written rather than three rounds
    /// later.
    /// </para>
    ///
    /// <para>
    /// A name belongs in <see cref="AllowedWithoutCaller"/> only with a reason: a document kept as evidence for
    /// a path that has no endpoint yet is legitimate, an unfinished step is not.
    /// </para>
    /// </summary>
    [Fact]
    public void EveryDocumentConstantHasAProductionCaller()
    {
        var allowed = AllowedWithoutCaller();
        var offenders = new List<string>();

        foreach (var (file, name, body) in DocumentConstants())
        {
            if (allowed.Contains(name)) continue;

            var uses = CountReferences(name) - 1;      // the declaration itself
            if (uses == 0) offenders.Add($"{file}:{name} ({body.Length} chars)");
        }

        Assert.True(offenders.Count == 0,
            "document constants nothing in src sends: " + string.Join(", ", offenders) +
            " — wire each to a step, or add it to AllowedWithoutCaller with a reason");
    }

    /// <summary>Documents kept on purpose without a caller. Empty, and a name here needs a reason.</summary>
    private static HashSet<string> AllowedWithoutCaller() => new(StringComparer.Ordinal);

    /// <summary>Every document-shaped constant in src: 60+ characters carrying a GraphQL or JSON signal.</summary>
    private static IEnumerable<(string File, string Name, string Body)> DocumentConstants()
    {
        var root = RepoRoot();
        if (string.IsNullOrEmpty(root)) yield break;

        foreach (var path in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar) ||
                path.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar))
                continue;

            var text = File.ReadAllText(path);
            foreach (Match match in Verbatim.Matches(text))
            {
                var body = match.Groups[2].Value.Replace("\\"\\"", "\\"");
                if (body.Length < 60) continue;
                if (!new[] { "mutation", "query", "fragment", "{" }.Any(s => body.Contains(s, StringComparison.Ordinal)))
                    continue;

                yield return (Path.GetFileName(path), match.Groups[1].Value, body);
            }
        }
    }

    /// <summary>How many times a name appears across src, declaration included.</summary>
    private static int CountReferences(string name)
    {
        var root = RepoRoot();
        if (string.IsNullOrEmpty(root)) return 0;

        var pattern = new Regex("\\\\b" + Regex.Escape(name) + "\\\\b", RegexOptions.Compiled);
        var total = 0;
        foreach (var path in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (path.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar) ||
                path.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar))
                continue;
            total += pattern.Matches(File.ReadAllText(path)).Count;
        }

        return total;
    }
}
'''

text = text.rstrip()
text = text[:text.rfind('}')].rstrip('\n') + '\n' + block
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('added the caller guard')
