using System.Reflection;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 63: <c>Profile</c> has 37 properties. The Clone button in <c>ProfileViews</c> listed 13
/// of them by hand, and the 24 it dropped included CardNumber, CardExpiry, CardCvv and CardName —
/// so a cloned profile looked complete in the grid and then could not check out.
///
/// Two other hand-listed copies (BillingView, ProfileViews.Clone) were more complete but were
/// still hand-listed, which means the next field added to the model would have been dropped there
/// too. All three now call <c>Profile.Clone()</c>.
///
/// These tests do not check a list of names. They reflect over every settable property, so a field
/// added to Profile later is covered without touching this file.
/// </summary>
public sealed class ProfileCloneTests
{
    private readonly ITestOutputHelper _out;

    public ProfileCloneTests(ITestOutputHelper output) => _out = output;

    /// <summary>A profile with a distinct value in every string property.</summary>
    private static Profile Filled()
    {
        var p = new Profile();
        foreach (var prop in typeof(Profile).GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            if (prop.PropertyType != typeof(string) || !prop.CanWrite) continue;
            prop.SetValue(p, "v-" + prop.Name);
        }

        p.CardNumber = "4111111111111111";
        p.CardExpiry = "12/29";
        p.CardCvv = "123";
        p.CardName = "A Name";
        p.Phone = "+44 7700 900000";
        p.OneCheckout = true;
        p.CheckoutType = "PayPal";
        return p;
    }

    /// <summary>
    /// Every writable property arrives at the clone unchanged, except Id.
    ///
    /// Reflected rather than listed: the defect this replaces was a list that could not stay
    /// complete.
    /// </summary>
    [Fact]
    public void EveryPropertyIsCopied()
    {
        var source = Filled();
        var clone = source.Clone();

        var mismatched = new List<string>();
        var compared = 0;

        foreach (var prop in typeof(Profile).GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            if (!prop.CanWrite) continue;
            if (prop.Name == nameof(Profile.Id)) continue;
            // R511: Card is a view that builds a fresh object on every get, so reference equality can
            // never hold. The four flat fields it reads IS copied, and the test below checks those.
            if (prop.Name == nameof(Profile.Card)) continue;

            compared++;
            var a = prop.GetValue(source);
            var b = prop.GetValue(clone);
            if (!Equals(a, b)) mismatched.Add($"{prop.Name}: {a} -> {b}");
        }

        _out.WriteLine($"compared {compared} writable properties, {mismatched.Count} differ");
        foreach (var line in mismatched.Take(8)) _out.WriteLine("  " + line);

        Assert.Empty(mismatched);
    }

    /// <summary>The four card fields specifically — the ones a checkout cannot run without.</summary>
    [Fact]
    public void TheCardFieldsSurvive()
    {
        var source = Filled();
        var clone = source.Clone();

        _out.WriteLine($"card: {clone.CardNumber} {clone.CardExpiry} {clone.CardCvv} {clone.CardName}");

        Assert.Equal("4111111111111111", clone.CardNumber);
        Assert.Equal("12/29", clone.CardExpiry);
        Assert.Equal("123", clone.CardCvv);
        Assert.Equal("A Name", clone.CardName);
        // 4111111111111111 ends in 1111, not 4111 — the first four read like the brand prefix
        Assert.Equal("1111", clone.Last4);
    }

    /// <summary>A clone is a new record, not the same one under a second name.</summary>
    [Fact]
    public void TheCloneHasItsOwnId()
    {
        var source = Filled();
        var clone = source.Clone();

        _out.WriteLine($"id: {source.Id} -> {clone.Id}");

        Assert.NotEqual(source.Id, clone.Id);
        Assert.False(string.IsNullOrWhiteSpace(clone.Id));
    }

    /// <summary>
    /// Editing the clone must not touch the original. Every member is a string, bool or enum, so
    /// there is nothing shared to guard against — but this asserts it rather than assuming it.
    /// </summary>
    [Fact]
    public void TheCloneIsIndependent()
    {
        var source = Filled();
        var clone = source.Clone();

        clone.Email = "other@example.com";
        clone.CardNumber = "5500000000000004";

        _out.WriteLine($"source email={source.Email} card={source.CardNumber}");
        Assert.Equal("v-Email", source.Email);
        Assert.Equal("4111111111111111", source.CardNumber);
    }

    /// <summary>
    /// No hand-listed Profile copy remains. A future edit that reintroduces one fails here rather
    /// than at a checkout two rounds later.
    /// </summary>
    [Fact]
    public void NoHandListedProfileCopyRemains()
    {
        var root = RepoRoot();
        var offenders = new List<string>();

        foreach (var file in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs",
                     SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            var text = File.ReadAllText(file);
            // A hand-listed copy is one that builds a Profile with an object initialiser instead
            // of delegating to Clone(). R68 changed the shape of the delegating version from an
            // expression body to a block (to add the " copy" suffix), so matching on "=> p.Clone()"
            // would now fail on correct code — assert the delegation, not its syntax.
            if (text.Contains("private static Profile Clone(Profile", StringComparison.Ordinal)
                && !System.Text.RegularExpressions.Regex.IsMatch(text, @"\bp\.Clone\(\)"))
            {
                offenders.Add(Path.GetFileName(file));
            }
        }

        _out.WriteLine($"hand-listed copies: {(offenders.Count == 0 ? "(none)" : string.Join(",", offenders))}");
        Assert.Empty(offenders);
    }

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }
}
