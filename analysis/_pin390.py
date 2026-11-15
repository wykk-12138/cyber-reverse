import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
start = t.index('    [Fact]\n    public void TheSettingsFileFieldsAllExist()')
end = t.index('    [Fact]', start + 10)
new = '''    [Fact]
    public void TheSettingsFileFieldsAllExist()
    {
        // R390: 44 keys, read from a backup the ORIGINAL wrote (compact camelCase; this replica wrote indented files until
        // R388, so the compact backup cannot be ours). The earlier version of this test used a settings.json the replica
        // itself had written — that file listed 43 keys and was missing the five credential-ish ones below.
        var names = new[]
        {
            "bearer", "license", "quickTaskProxies", "quickTaskProfiles", "monitorDelay", "retryDelay", "timeout",
            "shopifyBrowserProxy", "autoOpen3DS", "autoOpen3DSLimit", "browserPath", "browserLimit",
            "browserWindowMode", "browserProfiles", "browserProfileAssignment", "pinGroups", "startup", "keybinds",
            "notifications", "clock", "currency", "concurrency", "maxLogRetention", "maxLogSize", "backupInterval",
            "maxBackups", "smartactions", "betaUpdates", "taskGroupOrder", "proxyGroupOrder", "profileGroupOrder",
            "queuePresentation", "captchaProviders", "cloudflareSolvers", "webhooks", "notificationOptions",
            "keyBinds", "customStores", "customSizes", "monitorFilters", "scrollbarWidth", "scrollbarColor",
            "scrollbarCornerRadius", "language",
        };

        var props = typeof(GlobalSettings).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var missing = names.Where(n => !props.Contains(n.ToLowerInvariant())).ToList();

        _out.WriteLine($"{names.Length} live keys, missing: {missing.Count}");
        Assert.Empty(missing);
    }

'''
t = t[:start] + new + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('settings pin replaced with the trusted 44')
