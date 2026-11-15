import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CloseAndOpenFamilyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheAccountGridReportsItsGroupAndWhetherItCanEdit()
    {
        // R418: AccountGrid.AccountGroup / Edit — both read-only in the image (Getter,Property).
        var accounts = new List<Cybersole.Core.Models.Account>
        {
            new() { Email = "a@example.com", GroupId = "grp-1" },
        };
        var grid = new Cybersole.Ui.Views.Accounts.AccountGrid(accounts);

        _out.WriteLine($"{grid.AccountGroup} / {grid.Edit}");
        Assert.Equal("grp-1", grid.AccountGroup);
        Assert.True(grid.Edit);

        var empty = new Cybersole.Ui.Views.Accounts.AccountGrid(new List<Cybersole.Core.Models.Account>());
        Assert.Equal(string.Empty, empty.AccountGroup);
        Assert.False(empty.Edit);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test appended')
