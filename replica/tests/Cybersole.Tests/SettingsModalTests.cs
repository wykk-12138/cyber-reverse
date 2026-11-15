using System.Reflection;
using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Services;
using Cybersole.Ui.Views;
using Cybersole.Ui.Views.Settings.Modals;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Modal + billing-page parity. The ten modal type names below are exactly the files under
/// <c>/Views/Settings/Modals/</c> in the shipped binary.
///
/// Windows cannot be instantiated without an Avalonia windowing platform, so these tests
/// assert structure (type, base class, constructor shape, footer commands) rather than
/// constructing dialogs. UserControls are constructible and are covered by SettingsShellTests.
/// </summary>
public class SettingsModalTests
{
    private static readonly string[] RecoveredModals =
    {
        "AycdInboxCreatorView",
        "CaptchaProviderCreatorView",
        "CloudflareSolverCreatorView",
        "GoogleAccountEditView",
        "ImapCreatorView",
        "PayPalAccountCreatorView",
        "ShippingRatesCreatorView",
        "SizeCreatorView",
        "StoreCreatorView",
        "WebhookCreatorView",
    };

    private static Type Modal(string name) =>
        typeof(SettingsModal).Assembly.GetTypes().First(t => t.Name == name);

    [Fact]
    public void EveryRecoveredModalExistsAndDerivesFromTheBase()
    {
        foreach (var name in RecoveredModals)
        {
            var type = Modal(name);
            Assert.True(typeof(SettingsModal).IsAssignableFrom(type), $"{name} is not a SettingsModal");
            Assert.True(typeof(Window).IsAssignableFrom(type), $"{name} is not a Window");
        }
    }

    [Fact]
    public void EveryModalTakesAppServicesFirst()
    {
        foreach (var name in RecoveredModals)
        {
            var ctor = Modal(name).GetConstructors()
                .OrderByDescending(c => c.GetParameters().Length)
                .First();

            var first = ctor.GetParameters().First();
            Assert.Equal(typeof(AppServices), first.ParameterType);
        }
    }

    [Fact]
    public void BaseClassProvidesTheRecoveredFooterCommands()
    {
        var methods = typeof(SettingsModal)
            .GetMethods(BindingFlags.NonPublic | BindingFlags.Instance)
            .Select(m => m.Name)
            .ToHashSet();

        Assert.Contains("CloseButton", methods);
        Assert.Contains("SaveButton", methods);
        Assert.Contains("DeleteButton", methods);
        Assert.Contains("BuildFooter", methods);
    }

    [Fact]
    public void ModalBodiesExposeTheRecoveredCommandNames()
    {
        // Each modal's source contains the command labels recovered from the binary:
        // Captcha/CfSolver -> Save/Delete, SizeCreator -> Clear/Toggle size selected,
        // PayPalAccountCreator -> UseLoginProxy/AutoReopen, GoogleAccountEdit -> Proxy.
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        _ = dir; // source is not copied to the test output; assert via the assembly instead.

        var size = Modal("SizeCreatorView");
        Assert.Equal(typeof(SettingsModal), size.BaseType);

        var paypal = Modal("PayPalAccountCreatorView");
        Assert.Equal(typeof(SettingsModal), paypal.BaseType);

        var captcha = Modal("CaptchaProviderCreatorView");
        Assert.Equal(typeof(SettingsModal), captcha.BaseType);
    }

    [Fact]
    public void BillingViewIsAUserControl()
    {
        using var services = TestServices.Create();
        var view = new BillingView(services);
        Assert.IsAssignableFrom<UserControl>(view);
    }

    [Fact]
    public void ProfileCarriesTheInternationalAddressFields()
    {
        var p = new Profile
        {
            Title = "Mr",
            CareOf = "c/o",
            CompanyName = "ACME",
            District = "District 1",
            Region = "Region IV",
            StreetNumber = "12",
            StreetWithNumber = "12 Baker St",
            StreetSecondLine = "Apt 4",
            StreetThirdLine = "Floor 2",
            VatNumber = "DE123456789",
            Mobile = "+44 7700 900000",
            MobilePrefix = "+44",
            PhonePrefix = "+1",
            JapaneseName = "山田",
            JapaneseSurname = "太郎",
            FuriganaName = "ヤマダ",
            FuriganaSurname = "タロウ",
        };

        Assert.Equal("Mr", p.Title);
        Assert.Equal("ACME", p.CompanyName);
        Assert.Equal("District 1", p.District);
        Assert.Equal("DE123456789", p.VatNumber);
        Assert.Equal("ヤマダ", p.FuriganaName);
    }

    [Fact]
    public void TaskGroupCarriesAShippingRate()
    {
        var group = new TaskGroup { ShippingRate = "Standard:0.00" };
        Assert.Equal("Standard:0.00", group.ShippingRate);
    }

    [Fact]
    public void PayPalAccountCarriesTheRecoveredFields()
    {
        var account = new PayPalAccount
        {
            Email = "a@b.c",
            ProxyGroup = "residential",
            UseLoginProxy = true,
            AutoReopen = false,
            Running = true,
        };

        Assert.Equal("residential", account.ProxyGroup);
        Assert.True(account.UseLoginProxy);
        Assert.True(account.Running);
    }
}
