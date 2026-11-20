using System.Linq;
using System.Reflection;
using Cybersole.Services.Captcha;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// R1285: the image's captcha provider gives <c>Type</c> and <c>BalanceSupported</c> a getter and no setter.
///
/// <para>
/// Evidence: 1432159DC is <c>CaptchaProvider,Cybersole.Core.Type!Getter</c> and its <c>!Property</c> twin sits at
/// 14363E134 — no <c>!Setter</c> beside either — while Name, ApiKey, Balance, Count, Concurrency, Priority and
/// IsFetchingBalance all carry one (1432158BC…143215DF5). Init-only is how a C# record expresses "settable at
/// construction, not after": the setter still exists but carries the IsExternalInit modreq, and that modreq is what the
/// compiler refuses an assignment on.
/// </para>
/// </summary>
public sealed class CaptchaProviderTypeContractTests
{
    private static readonly string[] ReadOnlyMembers = { "Type", "BalanceSupported" };

    private static readonly string[] WritableMembers =
        { "Name", "ApiKey", "Balance", "Count", "Concurrency", "Priority", "IsFetchingBalance" };

    [Fact]
    public void TheTwoReadOnlyMembersAreInitOnly()
    {
        foreach (var name in ReadOnlyMembers)
        {
            var prop = typeof(CaptchaProviderConfig).GetProperty(name)!;
            Assert.True(prop.CanRead, name + " must be readable");

            var setter = prop.GetSetMethod(nonPublic: false);
            Assert.NotNull(setter);
            Assert.Contains(setter!.ReturnParameter.GetRequiredCustomModifiers(),
                m => m.Name == "IsExternalInit");
        }
    }

    [Fact]
    public void TheMembersTheImageLeavesWritableAreStillPlainlyWritable()
    {
        foreach (var name in WritableMembers)
        {
            var setter = typeof(CaptchaProviderConfig).GetProperty(name)!.GetSetMethod(nonPublic: false);
            Assert.NotNull(setter);
            Assert.DoesNotContain(setter!.ReturnParameter.GetRequiredCustomModifiers(),
                m => m.Name == "IsExternalInit");
        }
    }

    [Fact]
    public void CreationStillPicksASource()
    {
        var row = new CaptchaProviderConfig { Type = "capsolver", BalanceSupported = true,
            Name = "CapSolver", ApiKey = "k", Concurrency = 5, Priority = 2 };

        Assert.Equal("capsolver", row.Type);
        Assert.True(row.BalanceSupported);
        Assert.Equal("CapSolver", row.Name);
        Assert.Equal("humanpresence", new CaptchaProviderConfig().Type);
    }
}
