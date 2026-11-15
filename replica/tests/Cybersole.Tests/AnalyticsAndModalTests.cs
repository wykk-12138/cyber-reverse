using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Ui.Views.Analytics;
using Cybersole.Ui.Views.Modals;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Analytics + shared-modal parity. Type names below are the recovered XAML files under
/// <c>/Views/Analytics/</c> and <c>/Views/Modals/</c>.
/// </summary>
public class AnalyticsAndModalTests
{
    private static readonly string[] AnalyticsViews =
    {
        "AnalyticsView", "CheckoutList", "CheckoutView",
        "ReleaseView", "ReleaseSitelistView", "ReleaseGuideView",
    };

    private static readonly string[] SharedModals =
    {
        "DropdownModal", "InputModal", "MessageBoxDialog",
        "NotificationView", "DesktopNotification", "UserView",
    };

    [Fact]
    public void AllRecoveredAnalyticsViewsExist()
    {
        var names = typeof(AnalyticsView).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in AnalyticsViews) Assert.Contains(n, names);
    }

    [Fact]
    public void AllRecoveredSharedModalsExist()
    {
        var names = typeof(MessageBoxDialog).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in SharedModals) Assert.Contains(n, names);
    }

    [Fact]
    public void AnalyticsUserControlsConstruct()
    {
        using var services = TestServices.Create();
        var release = new Release
        {
            Product = "Test drop",
            Price = "180.00",
            Drops = new List<Drop>
            {
                new() { Time = DateTime.UtcNow.AddHours(1), Type = "raffle", Stores = new List<string> { "nike", "footlocker" } },
            },
        };

        Assert.IsAssignableFrom<UserControl>(new AnalyticsView(services));
        Assert.IsAssignableFrom<UserControl>(new CheckoutList(services));
        Assert.IsAssignableFrom<UserControl>(new CheckoutView(services));
        Assert.IsAssignableFrom<UserControl>(new ReleaseView(services, release));
        Assert.IsAssignableFrom<UserControl>(new ReleaseSitelistView(services, release));
        Assert.IsAssignableFrom<UserControl>(new ReleaseGuideView(services, release));
    }

    [Fact]
    public void SharedModalsDeriveFromWindow()
    {
        foreach (var name in SharedModals)
        {
            var type = typeof(MessageBoxDialog).Assembly.GetTypes().First(t => t.Name == name);
            Assert.True(typeof(Window).IsAssignableFrom(type), $"{name} is not a Window");
        }
    }

    [Fact]
    public void MessageBoxTypesMatchTheRecoveredEnum()
    {
        Assert.Equal(4, Enum.GetValues<MessageBoxType>().Length);
        Assert.Contains(MessageBoxType.Info, Enum.GetValues<MessageBoxType>());
        Assert.Contains(MessageBoxType.Warning, Enum.GetValues<MessageBoxType>());
        Assert.Contains(MessageBoxType.Error, Enum.GetValues<MessageBoxType>());
        Assert.Contains(MessageBoxType.Question, Enum.GetValues<MessageBoxType>());
    }

    [Fact]
    public void UserViewPinsTheDashboardUrl()
    {
        Assert.Equal("https://cybersole.io/dashboard", UserView.DashboardUrl);
    }

    [Fact]
    public void CheckoutEventCarriesATimestamp()
    {
        var before = DateTime.UtcNow.AddSeconds(-1);
        var evt = new CheckoutEvent("nike", "Air Max", "10", "150.00", true, "A123", "profile-1");
        var after = DateTime.UtcNow.AddSeconds(1);

        Assert.InRange(evt.At, before, after);
    }

    [Fact]
    public void CheckoutEventTimestampIsOverridable()
    {
        var when = new DateTime(2026, 1, 2, 3, 4, 5, DateTimeKind.Utc);
        var evt = new CheckoutEvent("nike", "Air Max", "10", "150.00", true, "A123", "p")
        {
            At = when,
        };
        Assert.Equal(when, evt.At);
    }
}
