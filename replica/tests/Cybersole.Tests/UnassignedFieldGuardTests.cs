using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R244: a field that is read but never written is how a command becomes a dead button.
///
/// <para>
/// R243 wrote <c>AppearanceView.ResetDefaults()</c> against <c>_appearanceServices</c>, a field nothing ever assigned —
/// so the method compiled, the tests passed, and clicking did nothing. The compiler cannot see it (a field is always
/// "assigned" as far as it is concerned) and no behaviour test covers a button nobody presses.
/// </para>
///
/// <para>
/// This guard reads every source file and fails on a private field that has <b>no initialiser and no assignment
/// anywhere in its file</b>. Fields assigned by a builder method (<c>WithTester(…)</c>) still count as assigned,
/// because the assignment is in the same file.
/// </para>
/// </summary>
public sealed class UnassignedFieldGuardTests
{
    private readonly ITestOutputHelper _out;
    public UnassignedFieldGuardTests(ITestOutputHelper output) => _out = output;

    private static readonly Regex FieldDecl = new(
        @"^\s*(?:private|internal|protected)\s+(?:readonly\s+)?(?:static\s+)?[\w<>,\?\[\]\.]+\s+_(?<name>\w+)\s*(?<tail>[;=])",
        RegexOptions.Compiled | RegexOptions.Multiline);

    [Fact]
    public void EveryPrivateFieldIsAssignedSomewhere()
    {
        var offenders = new List<string>();

        foreach (var file in Directory.EnumerateFiles(Path.Combine(Root(), "src"), "*.cs", SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            if (file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}")) continue;

            var text = File.ReadAllText(file);

            foreach (Match m in FieldDecl.Matches(text))
            {
                // "= value" is an initialiser, which is an assignment too
                if (m.Groups["tail"].Value == "=") continue;

                var name = "_" + m.Groups["name"].Value;
                if (Assigned(text, name)) continue;

                offenders.Add($"{Path.GetFileName(file)}: {name}");
            }
        }

        foreach (var offender in offenders) _out.WriteLine(offender);
        Assert.Empty(offenders);
    }

    [Fact]
    public void TheGuardWouldHaveCaughtTheOneFromR243()
    {
        // a miniature of the shape: a field declared, read in a method, never assigned
        const string sample = """
            private AppServices? _services;

            public void Reset()
            {
                var s = _services?.Config.Settings;
                if (s is null) return;
            }
            """;

        var declared = FieldDecl.Match(sample);
        Assert.True(declared.Success);

        var name = "_" + declared.Groups["name"].Value;
        Assert.False(Assigned(sample, name), "the guard's rule must flag an unassigned field");
    }

    /// <summary>
    /// Every way a field can be written in this codebase: plain assignment, compound assignment, an increment, a
    /// <c>ref</c> passed to <c>SetProperty</c> (the observable pattern), or an <c>out</c> argument.
    /// </summary>
    private static bool Assigned(string text, string name)
    {
        var n = Regex.Escape(name);
        return Regex.IsMatch(text, @"\b" + n + @"\s*(=[^=]|\+=|-=|\?\?=)")
               || Regex.IsMatch(text, @"\bref\s+" + n + @"\b")
               || Regex.IsMatch(text, @"\bout\s+" + n + @"\b")
               || Regex.IsMatch(text, @"(\+\+|--)\s*" + n + @"\b")
               || Regex.IsMatch(text, @"\b" + n + @"\s*(\+\+|--)");
    }

    private static string Root()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln"))) dir = dir.Parent;
        return dir!.FullName;
    }
}
