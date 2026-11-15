import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ServiceHostTests.cs"
t = io.open(p, encoding="utf-8").read()

# R127: the invented Scheels order endpoint is gone; the tests that referenced it now record the
# correction instead.
old1 = '''    [Fact]
    public void TheMobileApiHasThreeEndpoints()
    {
        Assert.Equal(3, ServiceHosts.ScheelsMobile.All.Count);
        Assert.Equal("https://mobile-api.scheels.com/v5/Order/", ServiceHosts.ScheelsMobile.Orders);

        _out.WriteLine(string.Join(", ", ServiceHosts.ScheelsMobile.All));
    }'''

new1 = '''    /// <summary>
    /// Two endpoints, not three: R115's third was Nike's <c>/v5/Order/</c> appended to the Scheels
    /// base, and R127 removed it.
    /// </summary>
    [Fact]
    public void TheMobileApiHasTwoEndpoints()
    {
        Assert.Equal(2, ServiceHosts.ScheelsMobile.All.Count);
        Assert.Equal("https://mobile-api.scheels.com/v5/auth/guest", ServiceHosts.ScheelsMobile.GuestAuth);
        Assert.Equal("https://mobile-api.scheels.com/v5/products/", ServiceHosts.ScheelsMobile.Products);

        _out.WriteLine(string.Join(", ", ServiceHosts.ScheelsMobile.All));
    }

    /// <summary>The path that was misattributed belongs to Nike, and Nike now carries it.</summary>
    [Fact]
    public void TheOrderPathBelongsToNikeNotScheels()
    {
        Assert.Contains("nike.com", NikeEndpoints.OrderV5);
        Assert.Contains("/v5/Order/", NikeEndpoints.OrderV5);
        Assert.DoesNotContain("scheels", NikeEndpoints.OrderV5);

        // and nothing in the Scheels family mentions it any more
        Assert.All(ServiceHosts.ScheelsMobile.All,
            u => Assert.DoesNotContain("Order", u, System.StringComparison.OrdinalIgnoreCase));

        _out.WriteLine(NikeEndpoints.OrderV5);
    }'''

if old1 not in t:
    raise SystemExit("three-endpoint test not found")
t = t.replace(old1, new1, 1)

# the app-step map no longer claims SubmitOrderApp
old2 = '''        Assert.Equal(ServiceHosts.ScheelsMobile.Orders,
            ServiceHosts.DualApi.AppSteps["SubmitOrderApp"]);'''
new2 = '''        // SubmitOrderApp is unmapped: its R115 target was Nike's path, so the step waits for a capture
        Assert.False(ServiceHosts.DualApi.AppSteps.ContainsKey("SubmitOrderApp"));'''
if old2 in t:
    t = t.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("service-host tests updated for the correction")
