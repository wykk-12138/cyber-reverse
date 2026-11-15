import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\ServiceHostTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    /// <summary>Parallax is a captcha service, and the property names prove it.</summary>"
add = '''    /// <summary>
    /// Round 115: the mobile API has three endpoints, and the app-side step names line up with them.
    ///
    /// <para>
    /// The mapping is a <b>name correlation</b> — <c>FindProductApp</c> ↔ <c>/v5/products/</c>,
    /// <c>SubmitOrderApp</c> ↔ <c>/v5/Order/</c>, <c>StartAppFast</c> ↔ <c>/v5/auth/guest</c> — and the
    /// code says so in <c>DualApi.Evidence</c>. It is recorded because it is the only bridge available
    /// between a step list and a host until a capture exists; it is labelled so nobody mistakes it for
    /// one.
    /// </para>
    /// </summary>
    [Fact]
    public void TheMobileApiHasThreeEndpoints()
    {
        Assert.Equal(3, ServiceHosts.ScheelsMobile.All.Count);
        Assert.Equal("https://mobile-api.scheels.com/v5/Order/", ServiceHosts.ScheelsMobile.Orders);

        _out.WriteLine(string.Join(", ", ServiceHosts.ScheelsMobile.All));
    }

    /// <summary>Every app-side step maps onto one of the three, and every target is a real endpoint.</summary>
    [Fact]
    public void TheAppStepsMapOntoTheMobileEndpoints()
    {
        Assert.Equal(5, ServiceHosts.DualApi.AppSteps.Count);

        foreach (var (step, host) in ServiceHosts.DualApi.AppSteps)
        {
            _out.WriteLine($"{step,-18} → {host}");
            Assert.Contains(host, ServiceHosts.ScheelsMobile.All);
        }

        Assert.Equal(ServiceHosts.ScheelsMobile.GuestAuth,
            ServiceHosts.DualApi.AppSteps["StartAppFast"]);
        Assert.Equal(ServiceHosts.ScheelsMobile.Products,
            ServiceHosts.DualApi.AppSteps["FindProductApp"]);
        Assert.Equal(ServiceHosts.ScheelsMobile.Orders,
            ServiceHosts.DualApi.AppSteps["SubmitOrderApp"]);
    }

    /// <summary>The web-side steps map onto the Frontastic hub from R103.</summary>
    [Fact]
    public void TheWebStepsMapOntoTheHub()
    {
        Assert.Equal(7, ServiceHosts.DualApi.WebSteps.Count);

        foreach (var (step, host) in ServiceHosts.DualApi.WebSteps)
        {
            _out.WriteLine($"{step,-24} → {host}");
            Assert.Contains(host, RetailApiFamilies.ScheelsFrontastic.All);
        }
    }

    /// <summary>The map is labelled as a correlation, not a capture.</summary>
    [Fact]
    public void TheMapSaysWhatItIs()
    {
        var evidence = ServiceHosts.DualApi.Evidence;

        Assert.Contains("name correlation", evidence);
        Assert.Contains("no request capture", evidence);

        _out.WriteLine(evidence);
    }

    /// <summary>Parallax is a captcha service, and the property names prove it.</summary>'''

if anchor not in t:
    raise SystemExit("anchor missing")
if "TheMobileApiHasThreeEndpoints" in t:
    print("already present")
else:
    io.open(p, "w", encoding="utf-8", newline="").write(t.replace(anchor, add, 1))
    print("dual-API tests added")
