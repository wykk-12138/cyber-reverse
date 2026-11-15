import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\StoreFlowStepsTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>Lookup by step name returns the flow it belongs to.</summary>"
add = '''    /// <summary>
    /// Round 113: three more flows, named for their evidence rather than for a brand.
    ///
    /// <para>
    /// The pool names no store for these three, so neither does the code. What it does record is what
    /// identifies them: a UK click-and-collect pair (<c>GetCollectPlusLocations</c> /
    /// <c>SubmitCollectPlus</c>) and an engine that issues a <b>structure token</b> before taking a
    /// payment, in two shapes (multi-variant and single).
    /// </para>
    /// </summary>
    [Fact]
    public void TheThreeUnnamedFlowsHaveTheirCounts()
    {
        Assert.Equal(17, StoreFlowSteps.CollectPlusApp.Count);
        Assert.Equal(15, StoreFlowSteps.StructureTokenMulti.Count);
        Assert.Equal(12, StoreFlowSteps.StructureTokenSingle.Count);

        foreach (var flow in new[]
                 {
                     StoreFlowSteps.CollectPlusApp, StoreFlowSteps.StructureTokenMulti,
                     StoreFlowSteps.StructureTokenSingle,
                 })
            _out.WriteLine($"{flow.Store,-24} {flow.Count} steps");
    }

    /// <summary>Eight flows in total now, all distinct.</summary>
    [Fact]
    public void ThereAreEightFlows()
    {
        Assert.Equal(8, StoreFlowSteps.All.Count);
        Assert.Equal(8, StoreFlowSteps.All.Select(f => f.Store).Distinct().Count());

        foreach (var flow in StoreFlowSteps.All)
        {
            var ordinals = flow.Steps.Select(s => s.Ordinal).ToList();
            Assert.Equal(ordinals.OrderBy(o => o), ordinals);
            Assert.Equal(flow.Count, flow.Names.Distinct().Count());
        }
    }

    /// <summary>The CollectPlus flow is the one with a click-and-collect pair, and it keeps App steps.</summary>
    [Fact]
    public void TheCollectPlusFlowIsRecognisableByItsPair()
    {
        var names = StoreFlowSteps.CollectPlusApp.Names;

        Assert.Contains("GetCollectPlusLocations", names);
        Assert.Contains("SubmitCollectPlus", names);
        Assert.Contains("GetPaymentUrl", names);

        // it keeps an app path beside the web steps
        Assert.Contains("FindProductApp", names);
        Assert.Contains("CreateCheckoutApp", names);

        // the pair appears in this flow only
        Assert.Equal("collectplus-app", StoreFlowSteps.FlowFor("SubmitCollectPlus")?.Store);
    }

    /// <summary>
    /// The two structure-token flows are one engine in two shapes: nine shared step names, different
    /// totals.
    /// </summary>
    [Fact]
    public void TheStructureTokenFlowsShareNineSteps()
    {
        var multi = StoreFlowSteps.StructureTokenMulti.Names.ToHashSet();
        var single = StoreFlowSteps.StructureTokenSingle.Names.ToHashSet();
        var shared = multi.Intersect(single).OrderBy(n => n).ToList();

        _out.WriteLine($"shared: {string.Join(", ", shared)}");

        Assert.Equal(9, shared.Count);
        Assert.Contains("GetStructureToken", shared);
        Assert.Contains("GetMerchantCode", shared);
        Assert.Contains("ProcessPayment", shared);

        // the difference is the multi-variant opening and the tax step
        Assert.Contains("FindProductMulti", multi);
        Assert.DoesNotContain("FindProductMulti", single);
        Assert.Contains("CalculateTaxes", multi);
        Assert.DoesNotContain("CalculateTaxes", single);

        // and they are distinct flows, not one
        Assert.NotEqual(StoreFlowSteps.StructureTokenMulti.Count,
            StoreFlowSteps.StructureTokenSingle.Count);
    }

    /// <summary>Every unnamed flow carries its identity evidence, and none claims a brand.</summary>
    [Fact]
    public void TheUnnamedFlowsCarryEvidenceNotBrands()
    {
        Assert.Equal(3, StoreFlowSteps.IdentityEvidence.Count);

        foreach (var (flow, evidence) in StoreFlowSteps.IdentityEvidence)
        {
            _out.WriteLine($"{flow}: {evidence}");
            Assert.False(string.IsNullOrWhiteSpace(evidence));
            Assert.DoesNotContain("is ", evidence, System.StringComparison.OrdinalIgnoreCase);
        }

        Assert.Contains("collectplus-app", StoreFlowSteps.IdentityEvidence.Keys);
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheThreeUnnamedFlowsHaveTheirCounts" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("tests added")
