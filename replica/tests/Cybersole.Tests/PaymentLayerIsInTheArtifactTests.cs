using System;
using System.IO;
using System.Linq;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1240: the payment layer has to be in the published artifact, not merely in the source tree.
///
/// <para>
/// Three rounds (R1236, R1237, R1239) used hand-run byte probes to decide whether decoded protocol reached the
/// product, and each of those probes got the shape wrong once: an ASCII-only search missed UTF-16 payloads, a host
/// belonging to a constant was read as a whole subsystem, and a path fragment that lives inside a concatenation was
/// searched for as a standalone string. A measurement that has been wrong three times belongs in a test.
/// </para>
///
/// <para>
/// The rule the artifact actually follows, measured in R1238, is per method: a method nothing calls has its body and
/// its literals trimmed away, even when its type is registered and instantiated. So what this asserts is the weaker,
/// checkable claim that the gateway entry points which <em>are</em> reached keep their hosts in the image. NativeAOT
/// stores frozen string payloads as UTF-16, so both encodings are searched and only a miss in both counts.
/// </para>
///
/// <para>
/// Skipped when the artifact is absent, because a source-only checkout should not fail on a build product it never
/// asked for.
/// </para>
/// </summary>
public sealed class PaymentLayerIsInTheArtifactTests
{
    private static string? Artifact()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        if (dir is null) return null;

        var exe = Path.Combine(dir.FullName, ".publish-aot", "Cybersole.Ui.exe");
        return File.Exists(exe) ? exe : null;
    }

    private static bool Contains(byte[] blob, string literal) =>
        blob.AsSpan().IndexOf(System.Text.Encoding.UTF8.GetBytes(literal)) >= 0 ||
        blob.AsSpan().IndexOf(System.Text.Encoding.Unicode.GetBytes(literal)) >= 0;

    [Theory]
    [InlineData("api.stripe.com")]
    [InlineData("api.unzer.com")]
    [InlineData("app.midtrans.com")]
    [InlineData("paypal.com/graphql")]
    [InlineData("checkoutshopper-live.adyen.com")]
    public void TheReachableGatewayHostsSurviveIntoTheArtifact(string literal)
    {
        var path = Artifact();
        if (path is null) return; // no artifact in this checkout: nothing to assert about a build product

        var blob = File.ReadAllBytes(path);
        Assert.True(Contains(blob, literal),
            $"'{literal}' is missing from {Path.GetFileName(path)}: the gateway entry point that carries it is not "
            + "reached by any call site, so the trimmer removed the method and its literals");
    }

    [Fact]
    public void TheArtifactIsLargerThanTheAppHostStub()
    {
        var path = Artifact();
        if (path is null) return;

        // A publish without -p:PublishAot=true silently produces a ~459 KB apphost, a failure mode recorded in R1209
        // that returned exit code zero.
        var size = new FileInfo(path).Length;
        Assert.True(size > 20_000_000, $"{Path.GetFileName(path)} is {size} bytes, which is an apphost, not a native image");
    }
}
