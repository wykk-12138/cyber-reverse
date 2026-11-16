using System.Collections.Generic;
using System.Linq;

namespace Cybersole.Stores.Scripts;

/// <summary>
/// The checks that would have caught three rounds of the same mistake (R158).
///
/// <para>
/// R149: a parameter named <c>W</c> collided with a <c>const W</c> inside the body, and the browser swallowed the
/// SyntaxError. R156: the surface call was spliced after <c>apply</c>'s closing brace, and the browser swallowed it
/// again. R157: escaped concatenation left literal <c>\n</c> outside a string, and the browser swallowed it a third
/// time. Three different mistakes, one reason they each survived to a red test: <b>a syntax error in an injected
/// script is invisible</b>.
/// </para>
///
/// <para>
/// So the checks live here, in one place, and run over every generated body: no literal escape sequences, balanced
/// delimiters, and — in the browser — an actual parse. The static half is cheap enough to run on every build; the
/// parse half belongs with the other slow tests.
/// </para>
/// </summary>
public static class JsGuard
{
    /// <summary>One problem with a generated body.</summary>
    public sealed record Problem(string Kind, string Detail);

    /// <summary>
    /// Everything wrong with <paramref name="js"/> that can be found without running it.
    /// </summary>
    public static IReadOnlyList<Problem> Inspect(string js)
    {
        var problems = new List<Problem>();

        // 1. A literal backslash-n OUTSIDE a string literal means someone escaped a newline twice; inside one it is
        //    ordinary JavaScript. The distinction is why this is a scan and not a Contains (R172).
        foreach (var escape in EscapesOutsideStrings(js))
            problems.Add(new Problem("literal-" + escape, "an escape survived into code position: " + escape));

        // 2. delimiters, counted outside string literals
        var (braces, parens, brackets) = CountDelimiters(js);
        if (braces != 0) problems.Add(new Problem("braces", $"unbalanced: {braces}"));
        if (parens != 0) problems.Add(new Problem("parens", $"unbalanced: {parens}"));
        if (brackets != 0) problems.Add(new Problem("brackets", $"unbalanced: {brackets}"));

        // 3. a body that is one long line is the shape the escaping bug produces
        var lines = js.Split('\n').Count(l => l.Trim().Length > 0);
        if (lines < 3)
            problems.Add(new Problem("one-line", $"only {lines} statement line(s): the escaping bug's shape"));

        // 4. an empty body is a stub, and a stub in this file has always meant a dropped composition
        if (js.Trim().Length < 40)
            problems.Add(new Problem("empty", "the body is empty or nearly so"));

        return problems;
    }

    /// <summary>True when nothing is wrong.</summary>
    public static bool IsClean(string js) => Inspect(js).Count == 0;

    /// <summary>
    /// Backslash escapes that appear in code position rather than inside a string or comment.
    /// </summary>
    private static IReadOnlyList<string> EscapesOutsideStrings(string js)
    {
        var found = new List<string>();
        char quote = '\0';

        for (var i = 0; i < js.Length - 1; i++)
        {
            var c = js[i];

            if (quote != '\0')
            {
                if (c == '\\') { i++; continue; }
                if (c == quote) quote = '\0';
                continue;
            }

            if (c == '/' && js[i + 1] == '/')
            {
                while (i < js.Length && js[i] != '\n') i++;
                continue;
            }

            if (c == '\'' || c == '"' || c == '`') { quote = c; continue; }

            if (c == '\\' && js[i + 1] is 'n' or 't')
            {
                var name = "\\" + js[i + 1];
                if (!found.Contains(name)) found.Add(name);
                i++;
            }
        }

        return found;
    }

    /// <summary>
    /// True when the <c>/</c> at <paramref name="index"/> starts a regular expression rather than a division: the
    /// character before it, ignoring spaces, is one of the tokens a regex can follow (R172).
    /// </summary>
    private static bool StartsRegex(string js, int index)
    {
        for (var i = index - 1; i >= 0; i--)
        {
            var c = js[i];
            if (char.IsWhiteSpace(c)) continue;
            return c is '=' or '(' or ',' or ':' or '[' or '!' or '&' or '|' or '?' or '{' or '}'
                or ';' or '>' or '+';
        }

        return false;
    }

    /// <summary>
    /// Net delimiter balance, skipping string literals and comments so a <c>'{'</c> inside a string does not count.
    /// </summary>
    private static (int Braces, int Parens, int Brackets) CountDelimiters(string js)
    {
        int braces = 0, parens = 0, brackets = 0;
        char quote = '\0';

        for (var i = 0; i < js.Length; i++)
        {
            var c = js[i];

            if (quote != '\0')
            {
                if (c == '\\') { i++; continue; }
                if (c == quote) quote = '\0';
                continue;
            }

            // R164: comments are skipped before quoting, because an apostrophe in prose ("browser's own
            // accessor") opened a string that never closed and swallowed the rest of the body. A guard that
            // miscounts is worse than no guard: it fails a correct body.
            if (c == '/' && i + 1 < js.Length && js[i + 1] == '/')
            {
                while (i < js.Length && js[i] != '\n') i++;
                continue;
            }

            if (c == '/' && i + 1 < js.Length && js[i + 1] == '*')
            {
                i += 2;
                while (i + 1 < js.Length && !(js[i] == '*' && js[i + 1] == '/')) i++;
                i++;
                continue;
            }

            if (c == '\'' || c == '"' || c == '`') { quote = c; continue; }

            // R172: a regex literal's brackets are not code — `[^(]` and `\(\)` are one character class and one
            // escaped pair, and counting them made a correct body look unbalanced.
            if (c == '/' && StartsRegex(js, i))
            {
                i++;
                while (i < js.Length && js[i] != '/')
                {
                    if (js[i] == '\\') i++;
                    i++;
                }
                continue;
            }

            switch (c)
            {
                case '{': braces++; break;
                case '}': braces--; break;
                case '(': parens++; break;
                case ')': parens--; break;
                case '[': brackets++; break;
                case ']': brackets--; break;
            }
        }

        return (braces, parens, brackets);
    }

    /// <summary>
    /// The agent the phone body needs, so the guard exercises the same code the bridge does rather than a stub.
    /// </summary>
    public const string SampleAgent =
        "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0_1 like Mac OS X) AppleWebKit/605.1.15 " +
        "(KHTML, like Gecko) CriOS/156.0.8078.54 Mobile/15E148 Safari/604.1";

    /// <summary>Every generated body in the workspace, with the name a failure should report.</summary>
    public static IReadOnlyList<(string Name, string Body)> AllBodies() => new[]
    {
        ("NativeRefs", NativeRefs.BodyJs()),
        ("Mask", NativeMask.BodyJs()),
        ("Parity", EngineParity.BodyJs()),
        ("WebAssembly", WebAssemblySurface.BodyJs()),
        ("Mobile", MobileSurface.BodyJs()),
        ("Engine", MobileSurface.EngineBodyJs()),
        ("Touches", MobileNavigator.BodyJs(SampleAgent)),
        ("Prune", NavPrune.BodyJs()),
        ("AudioSession", NavPrune.AudioSessionBodyJs()),
        ("Share", ForwardingShims.WebShareBodyJs()),
        ("Credentials", ForwardingShims.CredentialsBodyJs()),
        ("Reseat", NavOrder.ReseatBodyJs(NavOrder.Navigator)),
        ("WindowNames", WindowBaseline.BodyJs()),
        ("WindowOrder", WindowOrder.BodyJs()),
        ("GlobalPrune", GlobalPrune.GlobalBodyJs()),
        ("DocumentPrune", GlobalPrune.DocumentBodyJs()),
        ("WindowOrderWrap", WindowOrderWrap.BodyJs()),
        ("NavigatorLocks", NavigatorLocks.BodyJs()),
        ("BrandCheck", AccessorBrandCheck.BodyJs(AccessorBrandCheck.Guarded)),
        ("PatchJournal", PatchJournal.BodyJs()),
        ("CssProperties", CssStyleProperties.BodyJs()),
        ("CanvasSurface", CanvasSurface.BodyJs()),
        ("WebGlSurface", WebGlSurface.BodyJs()),
        ("GlobalSurface", GlobalSurface.BodyJs()),
        ("HandlerSurface", HandlerSurface.BodyJs()),
        ("MediaQuerySurface", MediaQuerySurface.BodyJs()),
        ("FontMediaSurface", FontMediaSurface.BodyJs()),
        ("MaskTargets", MaskTargets.ApplyJs()),
        ("BaselineSnapshot", WindowBaselineSnapshot.BodyJs()),
        ("WebAssembly wrapper", WebAssemblySurface.ToJavaScript()),
    };
}
