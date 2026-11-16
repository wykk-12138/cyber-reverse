using System.Collections.Generic;
using Cybersole.Core.Localization;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Behaviour probes for the CSV country/state validation, with every expectation derived from the ORIGINAL's
/// decompiled code rather than from this replica's behaviour.
///
/// WHY THIS EXISTS (AGENTS.md §1.2): criterion C7c — "every function behaves the same" — is `unknown` because the
/// original has no symbols to diff pseudocode against. The route recorded for it is behaviour probes: same input,
/// compare outputs. Those need the original to run, which needs credentials and is out of reach. What IS available is
/// the next best thing: read the decompiled guards, derive what they must return for a given input, and assert the
/// replica agrees. The expectation then comes from the binary, not from my own code — which is the whole point,
/// because an assertion that copies the implementation only tests that the implementation is itself.
///
/// Sources, all re-read at R703 and stored under analysis/:
///   sub_140F752D0  the guard's common front section (trim, then look up)
///   sub_141CFA390  string_normalise: trims ONLY when the first or last character is whitespace, and the whitespace
///                  test dispatches to sub_141D073A0 (&lt; 0x100) or sub_141D45100 (&gt;= 0x100) — the two halves of
///                  char.IsWhiteSpace, so System.String.Trim() is the equivalent operation
///   sub_140F77350  the country guard  (empty -> pass; trim; single-argument message)
///   sub_140F777E0  the state guard    (empty -> pass; country row [+96] state list; empty list -> pass;
///                                      two-argument message, second = [country+72] the country's own name)
///   sub_141DC1950  the comparison chain: ordinal first, then a case-folding retry
/// </summary>
public class DecompilationDerivedValidationProbes
{
    private readonly ITestOutputHelper _out;

    public DecompilationDerivedValidationProbes(ITestOutputHelper output) => _out = output;

    private const string Usa = "United States of America";

    [Theory]
    // sub_141CFA390: leading/trailing whitespace removed, interior whitespace preserved.
    [InlineData("  " + Usa + "  ", true, "surrounding whitespace is trimmed")]
    [InlineData("\t" + Usa + "\r\n", true, "tab / CR / LF are all char.IsWhiteSpace")]
    [InlineData("United  States of America", false, "interior runs are NOT collapsed — Trim only touches the ends")]
    [InlineData("UnitedStateofAmerica", false, "removing spaces is not trimming")]
    public void TrimmingTouchesOnlyTheEnds(string value, bool accepted, string why)
    {
        _out.WriteLine("case: " + why);
        Assert.Equal(accepted, ProfileValidationLists.ContainsCountry(value));
    }

    [Theory]
    // sub_141DC1950: ordinal comparison first, then a case-folding retry when the target carries a fold table.
    [InlineData("UNITED STATES OF AMERICA", true)]
    [InlineData("united states of america", true)]
    [InlineData("UnItEd StAtEs Of AmErIcA", true)]
    public void TheComparisonIgnoresCase(string value, bool accepted)
    {
        Assert.Equal(accepted, ProfileValidationLists.ContainsCountry(value));
    }

    [Theory]
    // The decompiled chain has no branch for abbreviations and none for prefix matching: it is equality after trim.
    [InlineData("US", false, "no abbreviation expansion anywhere in the chain")]
    [InlineData("U.S.", false, "punctuation is not stripped")]
    [InlineData("USA", false, "the ISO three-letter form is not in the country list either")]
    [InlineData("united states", false, "a strict prefix is not equal, so it is rejected")]
    public void AbbreviationsAndPrefixesAreNotAccepted(string value, bool accepted, string why)
    {
        _out.WriteLine("case: " + why);
        Assert.Equal(accepted, ProfileValidationLists.ContainsCountry(value));
    }

    [Fact]
    // sub_140F77350 opens with `if (!length || guard-front(value)) return 0` — an empty or all-whitespace value
    // returns success before any lookup happens. The replica must not be stricter than that.
    public void AnEmptyOrWhitespaceCountryPassesWithoutALookup()
    {
        Assert.True(ProfileValidationLists.ContainsCountry(string.Empty));
        Assert.True(ProfileValidationLists.ContainsCountry("   "));
        Assert.True(ProfileValidationLists.ContainsCountry("\t\n"));
    }

    [Fact]
    // sub_140F777E0: `v7 = country_row ? *(country_row + 96) : 0` then
    // `if (!v7 || *(int*)(v7+16) <= 0 || contains(country_row, state)) return 0`.
    // A country whose state list is null or empty therefore accepts anything — including nonsense.
    public void ACountryWithoutAStateListAcceptsAnyState()
    {
        Assert.Empty(ProfileValidationLists.StatesFor("Germany"));
        Assert.True(ProfileValidationLists.ContainsState("Germany", "Not a German state"));
        Assert.True(ProfileValidationLists.ContainsState("Germany", string.Empty));
    }

    [Fact]
    // The same guard compares against [country_row + 96]'s entries when the list is non-empty.
    public void ACountryWithAStateListRejectsAnythingOutsideIt()
    {
        Assert.NotEmpty(ProfileValidationLists.StatesFor(Usa));
        Assert.True(ProfileValidationLists.ContainsState(Usa, "Alabama"));
        Assert.True(ProfileValidationLists.ContainsState(Usa, "  alabama  "));
        Assert.False(ProfileValidationLists.ContainsState(Usa, "Bavaria"));
        Assert.False(ProfileValidationLists.ContainsState(Usa, "AL"),
            "the state comparison does not consult state_abbr — the guard only looks at [+96]");
    }

    [Fact]
    // The state message takes two arguments; the second is [country_row + 72], the row's own name rather than
    // whatever the user typed. CanonicalCountryName is that lookup.
    public void TheStateMessageUsesTheRowsOwnSpelling()
    {
        Assert.Equal(Usa, ProfileValidationLists.CanonicalCountryName("  united states of america  "));
        Assert.Equal(Usa, ProfileValidationLists.CanonicalCountryName("UNITED STATES OF AMERICA"));
    }
}
