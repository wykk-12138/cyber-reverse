import io
# 1) revert the section I wrongly added
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        // R300: the image names sixteen settings sections (Settings.Nav.*); the shell had fifteen — Advanced was
        // missing even though AdvancedView existed. Its position among the others is not evidenced, so it sits before
        // Need Help? as the least surprising place.
        new SettingsSection("advanced", "Advanced", s => new AdvancedView(s)),
'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, '', 1))
print('reverted: Advanced is a group caption, not a page (GUI evidence, guarded since earlier round)')

# 2) rewrite my nav test so it encodes the real knowledge: 16 Nav labels = 15 pages + 1 caption
p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SettingsNavTests.cs'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('''    /// <summary>The sixteen <c>Settings.Nav.*</c> leaves in the image, mapped to the replica's section ids.</summary>''',
'''    /// <summary>
    /// The sixteen <c>Settings.Nav.*</c> leaves in the image. Fifteen are pages; <c>Advanced</c> is the caption printed
    /// above Captcha Providers and is not navigable — R300 learned this the hard way when adding it as a page turned
    /// SettingsShellTests.AdvancedIsAGroupCaptionNotAPage red.
    /// </summary>''')
t2 = t2.replace('        ("Advanced", "advanced"),\n', '')
t2 = t2.replace('''        Assert.Equal(16, ids.Count);''', '''        Assert.Equal(15, ids.Count);
        // the sixteenth nav label is the caption, which lives on the section it heads
        Assert.Contains(SettingsShell.Sections, s => s.Group == "ADVANCED");''')
t2 = t2.replace('''        Assert.Equal(16, ids.Distinct().Count());''', '''        Assert.Equal(15, ids.Distinct().Count());''')
t2 = t2.replace('public void TheRailHasAllSixteenSectionsTheImageNames()', 'public void TheRailHasFifteenPagesAndTheAdvancedCaption()')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('nav test corrected')
