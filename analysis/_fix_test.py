import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GeneralSettingsLayoutTests.cs'
t = io.open(p, encoding='utf-8').read()
old = t[t.index('    [Fact]\n    public void TheLabelsComeFromLocaleKeysThatExist()'):]
new = '''    [Fact]
    public void TheLabelsComeFromLocaleKeysThatExist()
    {
        var locale = File.ReadAllText(Path.Combine(Root(),
            "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json"));

        // these four are the ones this round added UI for; they were already in the locale, which is why the
        // missing section was a UI gap and not a translation gap
        foreach (var key in new[]
                 {
                     "Settings.General.QuicktaskSettings",
                     "Settings.General.DefaultProfiles",
                     "Settings.General.DefaultProxies",
                     "Settings.General.ShopifySettings",
                 })
        {
            Assert.Contains(key, locale, System.StringComparison.Ordinal);
        }
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
print('cleaned test')
