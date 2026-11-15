import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ServiceHostTests.cs"
t = io.open(p, encoding="utf-8").read()

old = """    /// <summary>Five services, fifteen host literals, all distinct.</summary>
    [Fact]
    public void TheImageCarriesFiveServices()
    {
        Assert.Equal(5, ServiceHosts.Services.Count);
        Assert.Equal(14, ServiceHosts.All.Count);
        Assert.Equal(14, ServiceHosts.All.Distinct().Count());

        foreach (var url in ServiceHosts.All) _out.WriteLine(url);
    }"""

new = """    /// <summary>
    /// Five services, and the total is the sum of the five lists — not a number typed here.
    ///
    /// <para>
    /// A hand-summed total was wrong twice in two rounds (eight, then nine, for a shared-step count;
    /// fourteen here, when the five lists add to thirteen). The assertion is therefore structural:
    /// the per-service counts are pinned, and the total has to agree with them.
    /// </para>
    /// </summary>
    [Fact]
    public void TheImageCarriesFiveServices()
    {
        Assert.Equal(5, ServiceHosts.Services.Count);

        Assert.Equal(2, ServiceHosts.ScheelsMobile.All.Count);
        Assert.Equal(3, ServiceHosts.EndClothing.All.Count);
        Assert.Equal(3, ServiceHosts.AycdInbox.All.Count);
        Assert.Equal(2, ServiceHosts.ParallaxSystems.All.Count);
        Assert.Equal(3, ServiceHosts.GoogleMaps.All.Count);

        var summed = ServiceHosts.ScheelsMobile.All.Count + ServiceHosts.EndClothing.All.Count
                     + ServiceHosts.AycdInbox.All.Count + ServiceHosts.ParallaxSystems.All.Count
                     + ServiceHosts.GoogleMaps.All.Count;

        _out.WriteLine($"{ServiceHosts.All.Count} literals across five services");
        Assert.Equal(summed, ServiceHosts.All.Count);
        Assert.Equal(ServiceHosts.All.Count, ServiceHosts.All.Distinct().Count());

        foreach (var url in ServiceHosts.All) _out.WriteLine(url);
    }"""

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("total is now structural, not hand-summed")
