using System.Linq;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 158: the guard that would have caught three rounds of the same mistake.
///
/// <para>
/// Three syntax errors survived to a red test because the browser swallows a broken injected script without
/// telling anyone: a shadowed <c>W</c>, a call spliced outside its function, a doubled escape. Each was found by a
/// runtime measurement that reported "nothing applied" — which is a slow and indirect way to learn that a script
/// did not parse.
/// </para>
/// </summary>
public sealed class JsGuardTests
{
    private readonly ITestOutputHelper _out;

    public JsGuardTests(ITestOutputHelper output) => _out = output;

    /// <summary>Every generated body in the workspace is clean.</summary>
    [Fact]
    public void EveryBodyIsClean()
    {
        foreach (var (name, body) in JsGuard.AllBodies())
        {
            var problems = JsGuard.Inspect(body);
            _out.WriteLine($"{name,-22} {body.Length,6} chars  " +
                           (problems.Count == 0 ? "clean" : string.Join("; ", problems.Select(p => p.Kind))));

            Assert.True(problems.Count == 0,
                name + ": " + string.Join("; ", problems.Select(p => p.Kind + " " + p.Detail)));
        }
    }

    /// <summary>Every body the guard covers, so a new one cannot be added silently.</summary>
    [Fact]
    public void TheGuardCoversFiveBodies()
    {
        var names = JsGuard.AllBodies().Select(b => b.Name).ToArray();

        Assert.Equal(30, names.Length);
        Assert.Equal(new[]
        {
            "NativeRefs", "Mask", "Parity", "WebAssembly", "Mobile", "Engine", "Touches", "Prune", "AudioSession",
            "Share", "Credentials", "Reseat", "WindowNames", "WindowOrder", "GlobalPrune", "DocumentPrune",
            "WindowOrderWrap", "NavigatorLocks", "BrandCheck", "PatchJournal", "CssProperties", "CanvasSurface", "WebGlSurface", "GlobalSurface", "HandlerSurface", "MediaQuerySurface", "FontMediaSurface", "MaskTargets", "BaselineSnapshot", "WebAssembly wrapper",
        }, names);
    }

    /// <summary>Each check fires on the mistake it was written for.</summary>
    [Fact]
    public void TheChecksFire()
    {
        // the R157 shape: a literal escape outside a string
        var escaped = "  try {\\n    x();\\n  } catch (e) {}";
        Assert.Contains(JsGuard.Inspect(escaped), p => p.Kind == "literal-\\n");

        // the R156 shape: an extra closing brace
        var unbalanced = "  try { a(); }\n  }\n  b();";
        Assert.Contains(JsGuard.Inspect(unbalanced), p => p.Kind == "braces");

        // a body collapsed onto one line is what escaping twice produces
        var oneLine = "  try { a(); } catch (e) {}";
        Assert.Contains(JsGuard.Inspect(oneLine), p => p.Kind == "one-line");

        // a stub means the composition dropped something
        Assert.Contains(JsGuard.Inspect("  ;"), p => p.Kind == "empty");

        // and a '{' inside a string is not counted
        Assert.DoesNotContain(JsGuard.Inspect("  a('{');\n  b('}');\n  c('(');"),
            p => p.Kind is "braces" or "parens");
    }

    /// <summary>No body builds its JavaScript by escaping a newline.</summary>
    [Fact]
    public void NoBodyUsesEscapedNewlines()
    {
        // R172: escapes inside string literals are ordinary JavaScript, so the check is the guard's scan, not a
        // Contains — a body may legitimately answer "{\n    [native code]\n}".
        foreach (var (name, body) in JsGuard.AllBodies())
        {
            var problems = JsGuard.Inspect(body);
            Assert.DoesNotContain(problems, p => p.Kind.StartsWith("literal-", System.StringComparison.Ordinal));

            // a body that is mostly one line has the same cause
            Assert.True(body.Split('\n').Length > 3, name);
        }
    }
}
