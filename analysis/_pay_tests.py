import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PaymentViewTests.cs"
code = '''using System.Collections.Generic;
using System.Linq;
using Avalonia.Controls;
using Avalonia.VisualTree;
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
        view.GetVisualDescendants()
            .OfType<TextBlock>()
            .Where(t => t.IsVisible && t.Text is { Length: > 0 })
            .Select(t => t.Text!)
            .ToList();

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
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('PaymentViewTests written')
