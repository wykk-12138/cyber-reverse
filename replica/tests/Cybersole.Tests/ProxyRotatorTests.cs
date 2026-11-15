using Cybersole.Core.Models;
using Cybersole.Http;
using Xunit;

namespace Cybersole.Tests;

public class ProxyRotatorTests
{
    private static ProxyGroup Group(int maxUsage, params string[] hosts)
    {
        var group = new ProxyGroup { Name = "G", MaxUsage = maxUsage };
        for (var i = 0; i < hosts.Length; i++)
            group.Proxies.Add(new Proxy { Id = $"p{i}", Host = hosts[i], Port = 8080 });
        return group;
    }

    [Fact]
    public void Rotates_Through_All_Proxies()
    {
        var group = Group(0, "a", "b", "c");
        var rotator = new ProxyRotator(group);

        var seen = new HashSet<string>();
        for (var i = 0; i < 6; i++) seen.Add(rotator.Next()!.Host);

        Assert.Equal(3, seen.Count);
    }

    [Fact]
    public void Empty_Group_Returns_Null()
        => Assert.Null(new ProxyRotator(Group(0)).Next());

    [Fact]
    public void MarkUsed_Increments_The_Proxy_Counter()
    {
        var group = Group(0, "a");
        var rotator = new ProxyRotator(group);
        var proxy = rotator.Next()!;

        rotator.MarkUsed(proxy);
        rotator.MarkUsed(proxy);

        Assert.Equal(2, proxy.Usage);
    }

    [Fact]
    public void Exhausted_Proxies_Are_Skipped()
    {
        var group = Group(2, "a", "b");
        var rotator = new ProxyRotator(group);

        group.Proxies[0].Usage = 2;                  // "a" already at budget
        for (var i = 0; i < 4; i++)
            Assert.Equal("b", rotator.Next()!.Host);
    }

    [Fact]
    public void All_Exhausted_Returns_Null()
    {
        var group = Group(1, "a", "b");
        group.Proxies[0].Usage = 1;
        group.Proxies[1].Usage = 1;

        Assert.Null(new ProxyRotator(group).Next());
    }

    [Fact]
    public void Zero_Budget_Means_Unlimited()
    {
        var group = Group(0, "a");
        group.Proxies[0].Usage = 9999;

        Assert.NotNull(new ProxyRotator(group).Next());
    }

    [Fact]
    public void Available_Lists_Only_Proxies_Under_Budget()
    {
        var group = Group(3, "a", "b", "c");
        group.Proxies[1].Usage = 3;

        var available = new ProxyRotator(group).Available();
        Assert.Equal(new[] { "a", "c" }, available.Select(p => p.Host).ToArray());
    }

    [Fact]
    public void LeastUsed_Behaviour_Picks_The_Coldest_Proxy()
    {
        var group = Group(0, "hot", "cold");
        group.Behaviour = ProxyGroupBehaviour.LeastUsed;
        group.Proxies[0].Usage = 10;

        Assert.Equal("cold", new ProxyRotator(group).Next()!.Host);
    }
}
