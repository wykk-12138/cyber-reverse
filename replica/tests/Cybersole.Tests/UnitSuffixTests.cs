using System.Linq;
using Avalonia.Controls;
using Cybersole.Ui.Views;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Pins the unit suffix beside a field, which the live General pane prints and the replica did not.
///
/// The catalogue carried Settings.General.SuffixMs, Settings.General.SuffixSec and
/// Settings.General.MonitorConcurrency.Max all along, and the comment above ConcurrencyRow quoted "[Maximum ▾] [3 max]"
/// while the code drew two boxes and no suffix at all. So the copy existed, the intent was written down, and nothing
/// rendered it — the same shape of gap as the earlier count labels.
///
/// These construct the controls rather than reading source text, because R756 established that UiKit controls build
/// fine in a test; asserting behaviour is stronger than asserting the call is written somewhere.
/// </summary>
public class UnitSuffixTests
{
    private readonly ITestOutputHelper _out;

    public UnitSuffixTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheUnitSitsBesideTheFieldRatherThanInsideIt()
    {
        var box = UiKit.Number(2500);
        var wrapped = UiKit.WithUnit(box, "ms");

        var panel = Assert.IsType<StackPanel>(wrapped);
        Assert.Equal(2, panel.Children.Count);
        // the field keeps the number and its separator -- "2,500" is what R755 read off the live field -- and the
        // unit is separate, so the control's value never contains "ms".
        Assert.Same(box, panel.Children[0]);
        Assert.Equal("2,500", box.Text);

        var unit = Assert.IsType<TextBlock>(panel.Children[1]);
        Assert.Equal("ms", unit.Text);
        _out.WriteLine(box.Text + " " + unit.Text);
    }

    [Theory]
    [InlineData("ms")]
    [InlineData("sec")]
    [InlineData("max")]
    public void TheThreeUnitsTheWindowPrintsAreAllRenderable(string unit)
    {
        var wrapped = UiKit.WithUnit(UiKit.Text("1"), unit);
        var panel = Assert.IsType<StackPanel>(wrapped);
        Assert.Equal(unit, ((TextBlock)panel.Children[1]).Text);
    }

    [Fact]
    // A missing unit must not silently disappear into an empty label; it is passed through as given.
    public void AnEmptyUnitStillAddsALabel()
    {
        var panel = Assert.IsType<StackPanel>(UiKit.WithUnit(UiKit.Text("1"), string.Empty));
        Assert.Equal(2, panel.Children.Count);
        Assert.Equal(string.Empty, ((TextBlock)panel.Children[1]).Text);
    }
}
