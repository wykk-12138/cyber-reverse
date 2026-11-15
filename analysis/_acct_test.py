import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\PageCopyTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheAccountGroupDeleteConfirmationIsTheImagesWords()
    {
        // R430: the last Accounts.* value with no counterpart (the consolidated report caught it; the per-area tool had
        // counted "the {0} account group" as present because a similar sentence existed elsewhere).
        Assert.Equal("Are you sure you want to delete the {0} account group?\\nYou cannot undo this action.",
            Cybersole.Ui.Views.Accounts.AccountView.DeleteGroupConfirmFormat);
        Assert.Contains("delete the Family account group?", Cybersole.Ui.Views.Accounts.AccountView.DeleteGroupConfirm("Family"));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('test appended')
