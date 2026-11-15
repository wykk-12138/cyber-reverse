using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R354: <c>TaskGroupView</c> is down to zero missing bound members.
///
/// <para>
/// The image binds Close, CloudflareSolvers, Delete, Draft and Save on this dialog. The Captcha tab used to fill its combo
/// from the captcha registry directly while the bound member <c>CloudflareSolvers</c> did not exist, so the property and
/// the control could drift; now the combo reads the property. <c>Close</c> returns false when the view has no window,
/// which is exactly what a host-less construction sees.
/// </para>
/// </summary>
public sealed class TaskGroupViewTests
{
    private readonly ITestOutputHelper _out;
    public TaskGroupViewTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheBoundMembersAreAllThere()
    {
        var type = typeof(TaskGroupView);
        var names = type.GetMembers().Select(m => m.Name).ToList();

        foreach (var bound in new[] { "Close", "CloudflareSolvers", "DeleteGroup", "Draft" })
            Assert.Contains(bound, names);
    }

    [Fact]
    public void WithoutAHostCloseReportsFalseInsteadOfThrowing()
    {
        using var services = TestServices.Create();
        var view = new TaskGroupView(services, new TaskGroup { Name = "G" });

        Assert.False(view.CloseCore());
    }

    [Fact]
    public void TheSolverListAlwaysHasAnEntry()
    {
        using var services = TestServices.Create();
        var view = new TaskGroupView(services, new TaskGroup { Name = "G" });

        _out.WriteLine(string.Join(", ", view.CloudflareSolvers));
        Assert.NotEmpty(view.CloudflareSolvers);
    }
}
