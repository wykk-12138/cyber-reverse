import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheDataPageTableHoldsItsStrings()
    {
        // R414: the Data.* family — backup / import / restore / reset, all in the image's words.
        var copy = Cybersole.Ui.Views.Settings.DataView.Copy;
        _out.WriteLine(string.Join(", ", copy.Keys.OrderBy(k => k)));

        Assert.Equal(14, copy.Count);
        Assert.Equal("Backup Success", Cybersole.Ui.Views.Settings.DataView.Text("BackupTitle"));
        Assert.Equal("This file type is unsupported. Please import a JSON file.",
            Cybersole.Ui.Views.Settings.DataView.Text("ImportUnsupportedJson"));
        Assert.Equal("Restored Successfully", Cybersole.Ui.Views.Settings.DataView.Text("RestoreSuccessTitle"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Settings.DataView.Text("nope"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('data test appended')
