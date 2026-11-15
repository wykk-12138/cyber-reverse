import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheAuthAndHistoryTablesHoldTheirStrings()
    {
        // R421: Auth (15 + the Back to login leftover) and HistoryWindow (8 + Clear History).
        var auth = Cybersole.Ui.Views.Auth.LoginControl.Copy;
        var history = Cybersole.Ui.Views.SmartActions.HistoryWindow.Copy;
        _out.WriteLine($"auth {auth.Count}, history {history.Count}");

        Assert.Equal(16, auth.Count);
        Assert.Equal(9, history.Count);
        Assert.Equal("License Selector", Cybersole.Ui.Views.Auth.LoginControl.CopyText("LicenseTitle"));
        Assert.Equal("Back to login", Cybersole.Ui.Views.Auth.LoginControl.CopyText("BackToLogin"));
        Assert.Equal("Search history", Cybersole.Ui.Views.SmartActions.HistoryWindow.Text("SearchPlaceholder"));
        Assert.Equal("Clear History", Cybersole.Ui.Views.SmartActions.HistoryWindow.Text("Clear"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test appended')
