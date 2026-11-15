using Avalonia.Controls;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Services;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 78: the Notifications page is one formula printed five times, and the sound it configures
/// is now actually played.
///
/// <para>
/// Driving all five tabs of the live build showed the same panel every time, with only the first
/// caption varying:
/// </para>
///
/// <code>
/// Enable Notifications                     [switch]   page level  -> settings.notifications
/// Checkout | Decline | Captcha | Smart Actions | Other   tab bar
///   Allow {Tab} Notifications              [switch]   -> options.enabled
///   In-Bot Notifications                   [switch]   -> options.centre
///   Desktop Notifications                  [switch]   -> options.desktop
///   Sounds                                 [switch]   -> options.sound
///   [ Default ]                                       -> options.path
///   [ Reset ]  [ Play ]
/// </code>
///
/// <para>
/// Both ends of that chain were dead before this round: <c>settings.notifications</c> was read by
/// nobody, and <c>options.sound</c> / <c>options.path</c> were written by the page and read by
/// nobody, so the Sounds switch and its file had no effect on anything.
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class NotificationsPageTests
{
    private readonly ITestOutputHelper _out;

    public NotificationsPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>The five tabs and the five first captions, as the live page words them.</summary>
    [Fact]
    public void EachTabNamesItsOwnAllowSwitch()
    {
        var labels = NotificationsView.Tabs.Select(NotificationsView.AllowLabel).ToList();

        _out.WriteLine(string.Join(" | ", labels));

        Assert.Equal(new[]
        {
            "Allow Checkout Notifications",
            "Allow Decline Notifications",
            "Allow Captcha Notifications",
            "Allow Smart Actions Notifications",
            "Allow Other Notifications",
        }, labels);
    }

    /// <summary>Each tab is backed by its own options object, not a shared one.</summary>
    [Fact]
    public void EachTabHasItsOwnOptions()
    {
        var settings = new GlobalSettings();
        var seen = NotificationsView.Tabs.Select(tab => NotificationsView.OptionsFor(settings, tab)).ToList();

        _out.WriteLine($"{seen.Count} distinct objects: {seen.Distinct().Count()}");

        Assert.Equal(5, seen.Count);
        Assert.Equal(5, seen.Distinct().Count());
        Assert.Same(settings.NotificationOptions.Checkout, seen[0]);
        Assert.Same(settings.NotificationOptions.SmartAction, seen[3]);
        Assert.Same(settings.NotificationOptions.Other, seen[4]);
    }

    /// <summary>Every tab prints the same four switches and the same two buttons.</summary>
    [Fact]
    public void EveryTabPrintsTheSameFourSwitches()
    {
        var services = TestServices.Create();
        var view = new NotificationsView(services);
        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();
        var buttons = Descendants(view).OfType<Button>().Select(b => b.Content?.ToString() ?? "").ToList();

        foreach (var label in new[]
                 {
                     "Enable Notifications", "Allow Checkout Notifications",
                     "In-Bot Notifications", "Desktop Notifications", "Sounds",
                 })
        {
            _out.WriteLine($"{label}: {texts.Contains(label)}");
            Assert.Contains(label, texts);
        }

        Assert.Contains("Reset", buttons);
        Assert.Contains("Play", buttons);
        Assert.Contains("Default", buttons);
    }

    /// <summary>
    /// The Sounds switch and the sound file now reach a player. Before R78 the fan-out never played
    /// anything, so this asserts the whole chain: settings.notifications, then options.enabled, then
    /// options.sound, then the path.
    /// </summary>
    [Fact]
    public async Task TheFanOutPlaysTheConfiguredSound()
    {
        var player = new RecordingSoundPlayer();
        var settings = new GlobalSettings();
        settings.NotificationOptions.Checkout.Sound = true;
        settings.NotificationOptions.Checkout.Path = @"C:\sounds\cash.wav";

        var notify = new NotificationService(new EventBus(), settings, TestNet(), player);

        await notify.PublishAsync(NotificationKind.Checkout, "Checked out", "1 item");
        _out.WriteLine("played: " + string.Join(",", player.Plays.Select(p => p ?? "<default>")));
        Assert.Equal(new[] { @"C:\sounds\cash.wav" }, player.Plays);

        // the master switch silences everything
        player.Plays.Clear();
        settings.Notifications = false;
        await notify.PublishAsync(NotificationKind.Checkout, "Checked out", "1 item");
        Assert.Empty(player.Plays);

        // the per-category switch silences that category
        player.Plays.Clear();
        settings.Notifications = true;
        settings.NotificationOptions.Checkout.Enabled = false;
        await notify.PublishAsync(NotificationKind.Checkout, "Checked out", "1 item");
        Assert.Empty(player.Plays);

        // the Sounds switch silences just the sound
        player.Plays.Clear();
        settings.NotificationOptions.Checkout.Enabled = true;
        settings.NotificationOptions.Checkout.Sound = false;
        await notify.PublishAsync(NotificationKind.Checkout, "Checked out", "1 item");
        Assert.Empty(player.Plays);
    }

    /// <summary>An empty path means the platform default — that is what the "Default" button shows.</summary>
    [Fact]
    public async Task AnEmptyPathPlaysThePlatformDefault()
    {
        var player = new RecordingSoundPlayer();
        var settings = new GlobalSettings();
        settings.NotificationOptions.Other.Sound = true;
        settings.NotificationOptions.Other.Path = string.Empty;

        var notify = new NotificationService(new EventBus(), settings, TestNet(), player);
        await notify.PublishAsync(NotificationKind.Other, "Something", "happened");

        _out.WriteLine($"plays = {player.Plays.Count}, value = '{player.Plays[0] ?? "<null>"}'");

        Assert.Single(player.Plays);
        Assert.True(string.IsNullOrEmpty(player.Plays[0]));
    }

    /// <summary>Play on the page routes through the same player, not a second one.</summary>
    [Fact]
    public void PlayRoutesThroughTheServicesPlayer()
    {
        var player = new RecordingSoundPlayer();
        var services = TestServices.Create();
        var notify = new NotificationService(new EventBus(), services.Config.Settings, TestNet(), player);

        notify.PlaySound(@"C:\sounds\ding.wav");

        Assert.Equal(new[] { @"C:\sounds\ding.wav" }, player.Plays);
    }

    // ---------------------------------------------------------------- helpers

    private static NetClient TestNet() => new();

    private static IEnumerable<Control> Descendants(Control root)
    {
        var queue = new Queue<Control>();
        queue.Enqueue(root);
        while (queue.Count > 0)
        {
            var current = queue.Dequeue();
            if (!ReferenceEquals(current, root)) yield return current;

            foreach (var child in Avalonia.LogicalTree.LogicalExtensions
                         .GetLogicalChildren(current).OfType<Control>())
                queue.Enqueue(child);
        }
    }
}
