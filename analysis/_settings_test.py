import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\TaskCreatorCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheSettingsTableHoldsTheCapturedStrings()
    {
        // R416: 54 Settings.* values were missing; 52 were capturable in one pass and 2 long delete-confirm messages were
        // added by hand. The one key still absent is truncated in the pool ("…when using the \\").
        var copy = Cybersole.Ui.Views.Settings.SettingsShell.Copy;
        _out.WriteLine($"{copy.Count} strings");

        Assert.True(copy.Count >= 54, "expected at least 54 captured settings strings, got " + copy.Count);
        Assert.Equal("Add Source", Cybersole.Ui.Views.Settings.SettingsShell.Text("AddSource"));
        Assert.Equal("Balance ${0}", Cybersole.Ui.Views.Settings.SettingsShell.Text("BalanceFormat"));
        Assert.Equal("Disconnect AYCD Inbox", Cybersole.Ui.Views.Settings.SettingsShell.Text("Title"));
        Assert.Equal(string.Empty, Cybersole.Ui.Views.Settings.SettingsShell.Text("nope"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('settings copy test appended')
