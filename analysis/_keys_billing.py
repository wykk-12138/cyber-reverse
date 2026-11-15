import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\KeyBindChordTests.cs"
t = io.open(p, encoding='utf-8').read()
anchor = '''}
'''
add = '''
    /// <summary>
    /// The four Billing chords. R338 re-read "New Group Ctrl+G" and "Add Profile Ctrl+N" off the live page; the last two
    /// rows were below the fold and come from R76's table, so they are pinned here rather than claimed as re-measured.
    /// </summary>
    [Fact]
    public void TheFourBillingChordsReadAsThePagePrintsThem()
    {
        var binds = new BillingKeyBinds();
        var actual = new[]
        {
            KeyBindMatcher.Describe(binds.New), KeyBindMatcher.Describe(binds.AddProfile),
            KeyBindMatcher.Describe(binds.Clone), KeyBindMatcher.Describe(binds.Delete),
        };

        _out.WriteLine(string.Join(" | ", actual));

        Assert.Equal(new[] { "Ctrl+G", "Ctrl+N", "Ctrl+D", "Delete" }, actual);
    }
'''
idx = t.rindex('}')
t = t[:idx] + add.lstrip('\n') + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('billing chord test appended')
