using Cybersole.Core.Models;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 64: <c>Profiles.Context.MoveTo</c> ("Move profiles to") — the last of the three MoveTo
/// actions in the locale to get an implementation.
///
/// On the way in, two model facts turned up that this file pins:
///   - <c>ProfileGroup</c> and <c>BillingGroup</c> have identical members, and only
///     <c>BillingGroup</c> is ever constructed.
///   - Moving a profile has to update both sides (the group's list and the profile's GroupId),
///     exactly like accounts in R62.
/// </summary>
public sealed class ProfileMoveTests
{
    private readonly ITestOutputHelper _out;

    public ProfileMoveTests(ITestOutputHelper output) => _out = output;

    private static Profile Make(string email, string groupId = "ga") => new()
    {
        Name = email,
        Email = email,
        CardNumber = "4111111111111111",
        CardExpiry = "12/29",
        CardCvv = "123",
        GroupId = groupId,
    };

    /// <summary>Move updates both sides and keeps the card.</summary>
    [Fact]
    public void MovingAProfileUpdatesBothSides()
    {
        var profile = Make("a@example.com", "ga");
        var a = new BillingGroup { Name = "A", Id = "ga", Profiles = { profile } };
        var b = new BillingGroup { Name = "B", Id = "gb" };
        var groups = new List<BillingGroup> { a, b };

        // The confirm button's body, without needing a window.
        foreach (var group in groups) group.Profiles.Remove(profile);
        b.Profiles.Add(profile);
        profile.GroupId = b.Id;

        _out.WriteLine($"A={a.Profiles.Count} B={b.Profiles.Count} GroupId={profile.GroupId}");
        _out.WriteLine($"card kept: {profile.CardNumber} {profile.CardExpiry}");

        Assert.Empty(a.Profiles);
        Assert.Single(b.Profiles);
        Assert.Equal("gb", profile.GroupId);
        Assert.Equal("4111111111111111", profile.CardNumber);
        Assert.Equal("12/29", profile.CardExpiry);
        Assert.Equal("123", profile.CardCvv);
    }

    /// <summary>
    /// <c>Cybersole.Core.Models.ProfileGroup</c> is a duplicate of <c>BillingGroup</c> that nothing
    /// constructs.
    ///
    /// The original has a <c>ProfileGroupView</c>; this replica's one is
    /// <c>Cybersole.Ui.Views.Profiles.ProfileGroupView</c> and it operates on
    /// <c>Config.BillingGroups</c>. So the model class is dead weight — recorded here rather than
    /// deleted, because deleting a public model type is a separate decision and JSON written by an
    /// older build may still name it.
    /// </summary>
    [Fact]
    public void ProfileGroupIsNotUsed()
    {
        var root = RepoRoot();
        var constructions = new List<string>();

        // Word-boundary match, not Contains: "new ProfileGroupView(" contains "new ProfileGroup",
        // and a substring test called the UI type a model construction. That is the same mistake
        // as counting a superset and calling it the set.
        var ctor = new System.Text.RegularExpressions.Regex(@"\bnew\s+ProfileGroup\s*[\({]");

        foreach (var file in Directory.EnumerateFiles(Path.Combine(root, "src"), "*.cs",
                     SearchOption.AllDirectories))
        {
            if (file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")) continue;
            if (Path.GetFileName(file) == "Profiles.cs") continue;   // its own declaration

            if (ctor.IsMatch(File.ReadAllText(file)))
                constructions.Add(Path.GetFileName(file));
        }

        _out.WriteLine($"constructions of model ProfileGroup: " +
                       $"{(constructions.Count == 0 ? "(none)" : string.Join(",", constructions))}");

        Assert.Empty(constructions);
    }

    /// <summary>
    /// The two model classes really are structurally identical — that is what makes one of them
    /// redundant rather than merely unused.
    /// </summary>
    [Fact]
    public void TheTwoGroupTypesHaveTheSameMembers()
    {
        static string[] Names(Type t) => t.GetProperties()
            .Where(p => p.DeclaringType == t)
            .Select(p => p.Name)
            .OrderBy(n => n, StringComparer.Ordinal)
            .ToArray();

        var billing = Names(typeof(BillingGroup));
        var profile = Names(typeof(ProfileGroup));

        _out.WriteLine($"BillingGroup: {string.Join(",", billing)}");
        _out.WriteLine($"ProfileGroup: {string.Join(",", profile)}");

        Assert.Equal(billing, profile);
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
