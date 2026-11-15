using Avalonia.Controls;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 77: the Payment page, read off the live build.
///
/// <para>
/// Three sections and <b>six</b> controls at rest:
/// </para>
///
/// <code>
/// 3D Secure         Auto Open 3DS          [No]
/// External Browser  Browser Path           [None] [Configure]
///                   Maximum Browser Tabs   [10]
///                   Open Link As           [Tab]
/// Browser Profiles  Checkout Profiles      [Browser default] [Refresh]
///                   Profile Assignment     [Round robin]
/// </code>
///
/// <para>
/// The replica renders a seventh — "Max Open", from <c>Settings.Payment.AutoOpen3DSLimit</c> — which
/// the live page does not show. That difference is deliberately <b>kept and pinned</b> rather than
/// resolved by guessing: the property is real and <c>MainWindow</c> reads it, so removing the control
/// would strand the value, and deciding it is conditional needs evidence the live build would not
/// give up (its combos have no accessibility peer and a click does not open their popup).
/// </para>
/// </summary>
[Collection(UiControlsCollection.Name)]
public sealed class PaymentPageTests
{
    private readonly ITestOutputHelper _out;

    public PaymentPageTests(ITestOutputHelper output) => _out = output;

    /// <summary>The six controls the live page shows, in its order, word for word.</summary>
    [Fact]
    public void TheLivePageShowsSixControlsInThreeSections()
    {
        _out.WriteLine("sections: " + string.Join(" | ", PaymentView.LiveSections));
        _out.WriteLine("controls: " + string.Join(" | ", PaymentView.LiveControls));

        Assert.Equal(new[] { "3D Secure", "External Browser", "Browser Profiles" },
            PaymentView.LiveSections);

        Assert.Equal(new[]
        {
            "Auto Open 3DS", "Browser Path", "Maximum Browser Tabs", "Open Link As",
            "Checkout Profiles", "Profile Assignment",
        }, PaymentView.LiveControls);
    }

    /// <summary>
    /// The replica shows every live label, plus "Max Open" — and the extra one is asserted so the
    /// difference cannot quietly grow or quietly disappear.
    /// </summary>
    [Fact]
    public void TheReplicaShowsTheLiveLabelsAndOneExtra()
    {
        var services = TestServices.Create();
        var view = new PaymentView(services);
        var texts = Descendants(view).OfType<TextBlock>().Select(t => t.Text ?? "").ToList();

        foreach (var label in PaymentView.LiveControls)
        {
            _out.WriteLine($"{label}: {texts.Contains(label)}");
            Assert.Contains(label, texts);
        }

        foreach (var heading in PaymentView.LiveSections)
            Assert.Contains(heading, texts);

        // the seventh, and its reason for existing
        Assert.Contains("Max Open", texts);
    }

    /// <summary>
    /// The two buttons beside a field — Configure next to Browser Path, Refresh next to Checkout
    /// Profiles — are the live page's shape; both have to actually do something.
    /// </summary>
    [Fact]
    public void ConfigureAndRefreshAreRealButtons()
    {
        var services = TestServices.Create();
        var view = new PaymentView(services);
        var buttons = Descendants(view).OfType<Button>().ToList();

        var configure = buttons.Where(b => (b.Content?.ToString() ?? "") == "Configure").ToList();
        var refresh = buttons.Where(b => (b.Content?.ToString() ?? "") == "Refresh").ToList();

        _out.WriteLine($"configure={configure.Count} refresh={refresh.Count}");

        Assert.Single(configure);
        Assert.Single(refresh);
        Assert.True(configure[0].IsEffectivelyEnabled);
        Assert.True(refresh[0].IsEffectivelyEnabled);
    }

    /// <summary>
    /// The dropdown prints words, not enum names. R77 caught "RoundRobin" on screen where the live
    /// page prints "Round robin".
    /// </summary>
    [Fact]
    public void ProfileAssignmentPrintsWordsNotEnumNames()
    {
        _out.WriteLine(string.Join(" | ", PaymentView.AssignmentChoices));

        Assert.Equal(new[] { "Round robin", "Random", "Least used" }, PaymentView.AssignmentChoices);
        Assert.DoesNotContain("RoundRobin", PaymentView.AssignmentChoices);
    }

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
