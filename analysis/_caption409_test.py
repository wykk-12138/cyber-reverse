import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheTwoRemainingCountersAreTheImagesWords()
    {
        // R409: ProfileCsv.Menu.SelectedCells and Utilities.StoreGroups.CountFormat were the last caption keys with no
        // counterpart anywhere in the source.
        Assert.Equal("{0} CELLS SELECTED", ProfileCsvEditorView.SelectedCellsFormat);
        Assert.Equal("3 CELLS SELECTED", ProfileCsvEditorView.SelectedCells(3));
        Assert.Equal("{0} stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCountFormat);
        Assert.Equal("2 stores", Cybersole.Ui.Views.Utilities.UtilitiesView.StoresCount(2));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('caption test appended')
