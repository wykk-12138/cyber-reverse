import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CloseAndOpenFamilyTests.cs"
code = '''using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Modals;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R355: the "Close" and "OpenUrl" family the binding table names on dialogs, as members instead of click lambdas.
///
/// <para>
/// Close is bound on TaskCreatorView, TaskDetailsView, TaskGroupView, ProxyCreatorView, ProfileGroupView and others; the
/// panel behind the avatar binds OpenUrl. Each returns false when there is no window or no browser, which is what a
/// host-less construction — and a locked-down machine — actually sees.
/// </para>
/// </summary>
public sealed class CloseAndOpenFamilyTests
{
    private readonly ITestOutputHelper _out;
    public CloseAndOpenFamilyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheDialogsCarryClose()
    {
        foreach (var type in new[] { typeof(TaskCreatorView), typeof(TaskDetailsView), typeof(TaskGroupView) })
        {
            var has = type.GetMethods().Any(m => m.Name == "Close");
            _out.WriteLine(type.Name + ": " + has);
            Assert.True(has, type.Name + " has no Close()");
        }
    }

    [Fact]
    public void WithoutAHostCloseReportsFalse()
    {
        using var services = TestServices.Create();
        var details = new TaskDetailsView(services, new BotTask { Name = "t" });

        Assert.False(details.Close());
    }

    [Fact]
    public void OpeningSomethingUnopenableReportsFalse()
    {
        Assert.False(UserView.OpenUrl("not-a-url"));
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('tests written')
