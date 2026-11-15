import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\ProfileCsvCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheUtilitiesTableHoldsItsStringsToo()
    {
        // R411: same pattern, the Utilities.StoreGroups.* family.
        var copy = Cybersole.Ui.Views.Utilities.UtilitiesView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(18, copy.Count);
        Assert.Equal("Utilities", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("Title"));
        Assert.Equal("Store Groups", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("StoreGroupsTitle"));
        Assert.Equal("Add a store", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("ModalStoresPlaceholder"));
        Assert.Equal("Enter a group name", Cybersole.Ui.Views.Utilities.UtilitiesView.Text("ModalErrorNoName"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Utilities.UtilitiesView.Text("nope"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('utilities test appended')
