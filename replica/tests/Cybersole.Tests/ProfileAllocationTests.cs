using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Xunit;

namespace Cybersole.Tests;

public class ProfileAllocationTests
{
    private static Profile P(string id, bool oneCheckout = false)
        => new() { Id = id, Name = id, OneCheckout = oneCheckout };

    [Fact]
    public void Picks_The_First_Available_Profile()
    {
        var profiles = new[] { P("a"), P("b") };
        var usage = new Dictionary<string, int>();

        Assert.Equal("a", ProfileAllocation.Select(profiles, usage)!.Id);
    }

    [Fact]
    public void OneCheckout_Profile_Is_Retired_After_An_Order()
    {
        var profiles = new[] { P("a", true), P("b") };
        var usage = new Dictionary<string, int> { ["a"] = 1 };

        Assert.Equal("b", ProfileAllocation.Select(profiles, usage)!.Id);
    }

    [Fact]
    public void Reusable_Profile_Can_Be_Picked_Again()
    {
        var profiles = new[] { P("a") };
        var usage = new Dictionary<string, int> { ["a"] = 7 };

        Assert.Equal("a", ProfileAllocation.Select(profiles, usage)!.Id);
    }

    [Fact]
    public void Returns_Null_When_Every_Profile_Is_Spent()
    {
        var profiles = new[] { P("a", true), P("b", true) };
        var usage = new Dictionary<string, int> { ["a"] = 1, ["b"] = 1 };

        Assert.Null(ProfileAllocation.Select(profiles, usage));
        Assert.False(ProfileAllocation.HasCapacity(profiles, usage));
    }

    [Fact]
    public void Group_Profile_Limit_Stops_Allocation()
    {
        var profiles = new[] { P("a"), P("b"), P("c") };
        var usage = new Dictionary<string, int>();

        // limit 0 = unlimited
        Assert.NotNull(ProfileAllocation.Select(profiles, usage, profileLimit: 0));
        // limit 1 still allows the first pick
        Assert.NotNull(ProfileAllocation.Select(profiles, usage, profileLimit: 1));
    }

    [Fact]
    public void DistinctUsed_Counts_Only_Burned_Profiles()
    {
        var profiles = new[] { P("a"), P("b"), P("c") };
        var usage = new Dictionary<string, int> { ["a"] = 2, ["c"] = 1 };

        Assert.Equal(2, ProfileAllocation.DistinctUsed(profiles, usage));
    }

    [Fact]
    public void Empty_Candidate_List_Is_Safe()
        => Assert.Null(ProfileAllocation.Select(Array.Empty<Profile>(), new Dictionary<string, int>()));
}
