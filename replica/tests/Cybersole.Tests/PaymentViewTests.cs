using System.Collections.Generic;
using System.Linq;
using Avalonia.Controls;
using Avalonia.LogicalTree;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R330: "Max Open" is conditional, measured on the running 5.18.32 build.
///
/// <para>
/// R77 recorded the caveat that the live page shows only "Auto Open 3DS" at rest and could not decide whether the second
/// row appears on demand or is an orphan label. This round drove the real combo: with Auto Open 3DS on <b>Yes</b> a
/// "Max Open" row appears beneath it (value 5), and switching back to <b>No</b> removes it. So the replica now builds the
/// row and toggles its visibility with the same combo.
/// </para>
/// </summary>
public sealed class PaymentViewTests
{
    private readonly ITestOutputHelper _out;
    public PaymentViewTests(ITestOutputHelper output) => _out = output;

    private static IEnumerable<string> VisibleRowLabels(Control view) =>
        view.GetLogicalDescendants()
            .OfType<TextBlock>()
            .Where(t => t.Text is { Length: > 0 } && IsShown(t))
            .Select(t => t.Text!)
            .ToList();

    /// <summary>True when the block and every ancestor is visible; a hidden row keeps its text blocks.</summary>
    private static bool IsShown(Control control)
    {
        for (var node = control; node is not null; node = node.Parent as Control)
            if (!node.IsVisible) return false;
        return true;
    }

    [Fact]
    public void MaxOpenIsHiddenWhileAutoOpenThreeDsIsOff()
    {
        using var services = TestServices.Create();
        services.Config.Settings.AutoOpen3DS = false;

        var view = new PaymentView(services);

        var labels = VisibleRowLabels(view).ToList();
        _out.WriteLine("visible: " + string.Join(" | ", labels));

        Assert.Contains("Auto Open 3DS", labels);
        Assert.DoesNotContain("Max Open", labels);
    }

    [Fact]
    public void MaxOpenAppearsWhenAutoOpenThreeDsIsOn()
    {
        using var services = TestServices.Create();
        services.Config.Settings.AutoOpen3DS = true;

        var view = new PaymentView(services);

        Assert.Contains("Max Open", VisibleRowLabels(view));
    }
}
