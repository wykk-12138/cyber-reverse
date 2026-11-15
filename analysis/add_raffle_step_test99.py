import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\DemandwareRaffleTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>The raffle controllers are part of the confirmed Demandware vocabulary.</summary>"
add = '''    /// <summary>
    /// The step exists on the flow and uses the image's three pieces. Source-level, because reaching
    /// it needs a live store running a draw.
    ///
    /// <para>
    /// The property worth pinning is the <b>absent</b> branch: a store with no draw must succeed with
    /// <c>raffle=absent</c> rather than fail, so that every ordinary checkout keeps working.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFlowHasTheRaffleStepAndItToleratesNoDraw()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;

        var source = File.ReadAllText(Path.Combine(dir!.FullName, "src", "Cybersole.Stores",
            "Flows", "DemandwareFlow.cs"));

        Assert.Contains("EnterRaffleAsync", source);
        Assert.Contains("DemandwareRaffle.EntryPage", source);
        Assert.Contains("DemandwareRaffle.ExtractData", source);
        Assert.Contains("DemandwareControllers.SaleConfig", source);
        Assert.Contains("DemandwareControllers.SaleSignupSubmit", source);
        Assert.Contains("DemandwareRaffle.IsAlreadyEntered", source);

        // the no-draw branch succeeds instead of failing
        Assert.Contains("raffle\\"] = \\"absent\\"", source.Replace("\\\\", "\\\\"));

        _out.WriteLine("raffle step present, absent branch tolerated");
    }

'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheFlowHasTheRaffleStep" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add + anchor, 1))
    print("raffle step test added")
