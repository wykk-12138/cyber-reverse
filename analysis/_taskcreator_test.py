import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
code = '''using System.Linq;
using Cybersole.Ui.Views.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R412: the TaskCreator.* strings that had no counterpart, captured verbatim in one table.
///
/// <para>
/// <c>python tools/locale_text_gap.py TaskCreator</c> reported 19 missing values — every "select"/"multiple" placeholder the
/// creator shows when a field holds more than one value, plus the create/save buttons and the monitor-input row.
/// </para>
/// </summary>
public sealed class TaskCreatorCopyTests
{
    private readonly ITestOutputHelper _out;
    public TaskCreatorCopyTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheTableHoldsTheNineteenStrings()
    {
        _out.WriteLine(string.Join(", ", TaskCreatorView.Copy.Keys.OrderBy(k => k)));
        Assert.Equal(19, TaskCreatorView.Copy.Count);
        Assert.DoesNotContain(string.Empty, TaskCreatorView.Copy.Values);
    }

    [Theory]
    [InlineData("CreateTask", "Create Task")]
    [InlineData("CreateTasksFormat", "Create {0} Tasks")]
    [InlineData("MonitorInputFormat", "Enter {0}")]
    [InlineData("MonitorInputMultiple", "Multiple inputs")]
    [InlineData("StoreSelect", "Select store")]
    [InlineData("SizeMultiple", "Multiple sizes")]
    public void TheWordingIsTheImagesWording(string name, string expected)
    {
        Assert.Equal(expected, TaskCreatorView.Text(name));
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('test written')
