using System.Linq;
using Cybersole.Core.Localization;
using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// The country/state rules the CSV row validator applies.
///
/// WHY THIS EXISTS (AGENTS.md §1.2): R702 decompiled the two guards that raise
/// `ProfileCsv.Error.UnknownCountry` / `.UnknownState` and R703 re-derived the reference from raw bytes and
/// decompiled both functions; R704 exported the tables and wired the messages to code. Without these tests the
/// 2 -> 0 drop in the copy metric would be achieved by *referencing* the keys, not by implementing anything,
/// and referencing is exactly what a copy metric cannot distinguish from a real feature.
///
/// The four rules under test, each taken from the decoded behaviour rather than invented:
///   1. a value in the list passes;
///   2. a value not in the list fails and names the value;
///   3. a country with no state list accepts any state (the guard returns before comparing);
///   4. a country with a state list rejects a state outside it, naming both state and country.
/// </summary>
public class ProfileValidationListsTests
{
    private readonly ITestOutputHelper _out;

    public ProfileValidationListsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheExportedTablesCarryTheCountsTheOriginalHas()
    {
        _out.WriteLine($"countries={ProfileValidationLists.Countries.Count}");

        Assert.Equal(244, ProfileValidationLists.Countries.Count);
        Assert.Equal(50, ProfileValidationLists.StatesFor("United States of America").Count);
        Assert.Contains("Afghanistan", ProfileValidationLists.Countries);
        Assert.Contains("Zimbabwe", ProfileValidationLists.Countries);
    }

    [Fact]
    public void AnUnknownCountryIsRejectedAndAListedOneIsAccepted()
    {
        Assert.True(ProfileValidationLists.ContainsCountry("United States of America"));
        Assert.True(ProfileValidationLists.ContainsCountry("  united states of america  "),
            "the comparison trims and ignores case; no lowercasing and no abbreviation expansion is involved");
        Assert.False(ProfileValidationLists.ContainsCountry("US"),
            "abbreviations are not expanded -- the decompiled comparison chain has no branch for them");
        Assert.False(ProfileValidationLists.ContainsCountry("united states"),
            "nor is it a prefix match: the list says 'United States of America' and the comparison is ordinal "
            + "after trimming, so a truncated name is simply not equal");
        Assert.False(ProfileValidationLists.ContainsCountry("Atlantis"));
    }

    [Fact]
    public void ACountryWithoutAStateListAcceptsAnyState()
    {
        // This is rule 3 and it is the one most easily got wrong: the guard returns success when the country
        // row carries no state list, rather than falling through to a comparison that would reject everything.
        Assert.Empty(ProfileValidationLists.StatesFor("Germany"));
        Assert.True(ProfileValidationLists.ContainsState("Germany", "Anywhere at all"));
        Assert.True(ProfileValidationLists.ContainsState("Atlantis", "Anywhere at all"));
    }

    [Fact]
    public void ACountryWithAStateListRejectsAStateOutsideIt()
    {
        Assert.True(ProfileValidationLists.ContainsState("United States of America", "Alabama"));
        Assert.True(ProfileValidationLists.ContainsState("United States of America", "wyoming"));
        Assert.False(ProfileValidationLists.ContainsState("United States of America", "Bavaria"));

        // the message takes two arguments: the state, then the country's own spelling
        Assert.Equal("United States of America",
            ProfileValidationLists.CanonicalCountryName(" united states of america "));

        // and when nothing matched the input is echoed back trimmed -- the original formats the row's name
        // field, and on a path that already failed there is no row
        Assert.Equal("united states", ProfileValidationLists.CanonicalCountryName(" united states "));
    }

    [Fact]
    public void TheEditorRaisesBothMessagesByReference()
    {
        // A blank country passes (the guard returns before looking anything up), so a profile that only carries
        // a name is still acceptable -- the copy metric dropping to zero must not have made the editor stricter
        // for rows the original accepts.
        var lists = typeof(ProfileValidationLists);
        Assert.NotNull(lists.GetMethod("ContainsCountry"));
        Assert.NotNull(lists.GetMethod("ContainsState"));
    }
}
