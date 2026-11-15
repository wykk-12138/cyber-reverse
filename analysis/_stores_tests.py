import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CustomStoresRowsTests.cs"
code = '''using Cybersole.Core.Models;
using Cybersole.Ui.Views.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R347: <c>CustomStoresView.Rows</c> and <c>.Delete</c>, the two of its four bound members whose meaning is not in doubt.
///
/// <para>
/// The image binds Add, Clear, Delete, Rows and View on this page. Rows is the preset list and Delete removes one by
/// position — both are decided here. <c>View</c> is bound as well and still means nothing to me (view the URL? open the
/// editor?), so it stays in docs/BINDING_BACKLOG.md rather than being guessed.
/// </para>
/// </summary>
public sealed class CustomStoresRowsTests
{
    private readonly ITestOutputHelper _out;
    public CustomStoresRowsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void RowsAreTheConfiguredPresets()
    {
        using var services = TestServices.Create();
        services.Config.Settings.CustomStores = new List<CustomStore> { new() { Name = "one" }, new() { Name = "two" } };

        var page = new CustomStoresView(services);

        _out.WriteLine("rows: " + string.Join(", ", page.Rows.Select(r => r.Name)));
        Assert.Equal(2, page.Rows.Count);
    }

    [Fact]
    public void DeleteRemovesOneByPositionAndRefusesOutOfRange()
    {
        using var services = TestServices.Create();
        services.Config.Settings.CustomStores = new List<CustomStore> { new() { Name = "one" }, new() { Name = "two" } };

        var page = new CustomStoresView(services);

        Assert.True(page.Delete(0));
        Assert.Single(page.Rows);
        Assert.False(page.Delete(5));
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(code)
print('tests written')
