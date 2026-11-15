import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DemandwareControllerTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>\n    /// The flow source no longer contains an invented controller."
add = '''    /// <summary>
    /// R95: the image spells four URLs out end to end, which fixes the path shape and proves it.
    ///
    /// <code>
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct
    /// https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Product-Variation?pid=
    /// https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/
    /// https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit
    /// </code>
    ///
    /// The locale is <c>default</c> on Marc Jacobs and <c>en_US</c> on Stone Island, so it is a
    /// parameter — hard-coding either one gets the other store wrong.
    /// </summary>
    [Fact]
    public void TheSitePathReproducesTheImagesUrls()
    {
        var marcJacobs = DemandwareControllers.SitePath(
            DemandwareControllers.Hosts["mjsfra"], "mjsfra", "default",
            DemandwareControllers.CartAddProduct);

        var stone = DemandwareControllers.SitePath(
            DemandwareControllers.Hosts["StoneNA"], "StoneNA", "en_US",
            DemandwareControllers.SaleSignupSubmit);

        var cpcompany = DemandwareControllers.SiteRoot(
            DemandwareControllers.Hosts["cpcompany"], "cpcompany");

        _out.WriteLine(marcJacobs);
        _out.WriteLine(stone);
        _out.WriteLine(cpcompany);

        Assert.Equal("https://www.marcjacobs.com/on/demandware.store/Sites-mjsfra-Site/default/Cart-AddProduct",
            marcJacobs);
        Assert.Equal("https://www.stoneisland.com/on/demandware.store/Sites-StoneNA-Site/en_US/SaleRegistration-SignupSubmit",
            stone);
        Assert.Equal("https://www.cpcompany.com/on/demandware.store/Sites-cpcompany-Site/", cpcompany);
    }

    /// <summary>The raffle chain is in the vocabulary; hosts are only the three the image pairs.</summary>
    [Fact]
    public void TheRaffleChainAndHostsAreRecorded()
    {
        Assert.True(DemandwareControllers.IsKnown("SaleRegistration-SignupSubmit"));
        Assert.True(DemandwareControllers.IsKnown("SaleRegistration-Config"));

        Assert.Equal(3, DemandwareControllers.Hosts.Count);
        Assert.Equal("www.marcjacobs.com", DemandwareControllers.Hosts["mjsfra"]);
        Assert.Equal("www.stoneisland.com", DemandwareControllers.Hosts["StoneNA"]);
        Assert.Equal("www.cpcompany.com", DemandwareControllers.Hosts["cpcompany"]);

        // asics / crocs / vans are site ids without a host in the same literal — not guessed
        Assert.False(DemandwareControllers.Hosts.ContainsKey("asics"));
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheSitePathReproducesTheImagesUrls" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("tests added")
