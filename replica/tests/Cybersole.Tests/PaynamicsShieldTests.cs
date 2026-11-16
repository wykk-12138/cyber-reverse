using Cybersole.Stores.Payments;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Paynamics's second shield surface, and the step the original has that this replica does not.
///
/// <para>
/// R905. The round began by asking what <c>/shield/v1/verify_otp</c> was, having filed it in R903 as an anti-bot
/// concern. It is not: nineteen literals name it as Paynamics Shield, a payment processor, including the host
/// <c>shield.paynamics.net</c>, the strings "Invalid Paynamics Shield URL" and "Paynamics Shield error (", and a
/// method name <c>RunShield</c> that appears in the image's async-method table.
/// </para>
///
/// <para>
/// So R903's classification was wrong and this file records the correction alongside the two facts the image does
/// support: a second shield host, and an OTP path on it.
/// </para>
/// </summary>
public class PaynamicsShieldTests
{
    /// <summary>
    /// Two hosts, not one. The device-profiling call already in this class talks to nodecde1; the OTP path lives on
    /// shield.paynamics.net, so the two are not interchangeable.
    /// </summary>
    [Fact]
    public void TheShieldSurfaceHasTwoHostsAndTheyDiffer()
    {
        var (host, path) = PaynamicsGateway.RecoveredShieldSurface;

        Assert.Equal("https://shield.paynamics.net", host);
        Assert.NotEqual("https://nodecde1.paynamics.net", host);
        Assert.Equal("/shield/v1/verify_otp", path);
    }

    /// <summary>
    /// The path begins with the shield segment, which is the whole reason R903 filed it under anti-bot. Pinned so the
    /// corrected reading — payment, not protection — is attached to the fact that made the old reading plausible.
    /// </summary>
    [Fact]
    public void ThePathStartsWithTheShieldSegmentThatCausedTheMisfiling()
    {
        var (_h, path) = PaynamicsGateway.RecoveredShieldSurface;
        Assert.StartsWith("/shield/", path);
        Assert.Contains("verify_otp", path);
    }

    /// <summary>
    /// The pair is a surface, not a call: nothing in the gateway posts to it. Asserted by checking the host does not
    /// appear in any call site, which is the honest state and would fail loudly if a later round wired it up without
    /// updating this test's intent.
    /// </summary>
    [Fact]
    public void TheRecoveredSurfaceIsNotYetCalled()
    {
        var (host, _path) = PaynamicsGateway.RecoveredShieldSurface;

        // the class exposes the pair through one property; a second occurrence of the host outside it would mean a
        // call site exists
        var source = System.IO.File.ReadAllText(SourcePath());
        var occurrences = source.Split(new[] { "https://shield.paynamics.net" }, System.StringSplitOptions.None).Length - 1;

        Assert.Equal(1, occurrences);
        Assert.DoesNotContain(host + " + ", source);
    }

    private static string SourcePath()
    {
        var dir = new System.IO.DirectoryInfo(System.AppContext.BaseDirectory);
        while (dir != null && !System.IO.Directory.Exists(System.IO.Path.Combine(dir.FullName, "src")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return System.IO.Path.Combine(dir!.FullName, "src", "Cybersole.Stores", "Payments", "Gateways.cs");
    }
}
