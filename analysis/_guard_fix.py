import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\SettingsStorageLinkTests.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        var read = text.IndexOf("_services.Captcha.Registry.Configs", StringComparison.Ordinal);
        Assert.True(read >= 0,
            "the Cloudflare solver dropdown changed its source; update "
            + "AddingACloudflareProviderAlsoRegistersItAsACaptchaProvider to match");

        var line = text[..read].Count(c => c == '\\n') + 1;
        _out.WriteLine($"dropdown reads the captcha registry at TasksViews.cs:{line}");

        // the assignment must land on the group's CloudflareSolver field
        var window = text[read..Math.Min(text.Length, read + 600)];
        Assert.Contains("CloudflareSolver", window, StringComparison.Ordinal);'''
new = '''        // R354: the dropdown now reads the bound property instead of the registry directly, so the guard follows the
        // shape: the combo takes CloudflareSolvers, and that property is what reads the captcha registry.
        var read = text.IndexOf("UiKit.Combo(CloudflareSolvers)", StringComparison.Ordinal);
        Assert.True(read >= 0,
            "the Cloudflare solver dropdown changed its source; update "
            + "AddingACloudflareProviderAlsoRegistersItAsACaptchaProvider to match");

        var property = text.IndexOf("public IReadOnlyList<string> CloudflareSolvers", StringComparison.Ordinal);
        Assert.True(property >= 0, "the bound CloudflareSolvers property is gone");

        var propertyBody = text[property..Math.Min(text.Length, property + 400)];
        Assert.Contains("_services.Captcha.Registry.Configs", propertyBody, StringComparison.Ordinal);

        // and the assignment must still land on the group's CloudflareSolver field
        var window = text[read..Math.Min(text.Length, read + 600)];
        Assert.Contains("CloudflareSolver", window, StringComparison.Ordinal);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('guard follows the new shape')
