import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    private static List<string> WrittenKeys(object document) =>
        Newtonsoft.Json.Linq.JObject
            .Parse(Newtonsoft.Json.JsonConvert.SerializeObject(document, Cybersole.Core.Store.Json.Default))
            .Properties().Select(p => p.Name).OrderBy(n => n).ToList();

    [Fact]
    public void TheSmallerDocumentsAlsoUseTheImagesKeyNames()
    {
        // each pair is (live top-level keys, a fresh instance of the replica's document type)
        var pairs = new (string[] Live, object Doc)[]
        {
            (new[] { "accountGroups", "payPal", "google", "imap", "aycdInbox" },
                new Cybersole.Core.Models.AccountsDocument()),
            (new[] { "proxies" }, new Cybersole.Core.Models.AnalyticsDocument()),
            (new[] { "actions", "templates" }, new Cybersole.Core.Models.SmartActionsDocument()),
            (new[] { "groups" }, new Cybersole.Core.Models.SmartActionUtilitiesDocument()),
        };

        foreach (var (live, doc) in pairs)
        {
            var written = WrittenKeys(doc);
            _out.WriteLine(doc.GetType().Name + ": " + string.Join(", ", written));
            Assert.Equal(live.OrderBy(x => x), written);
        }
    }

    [Fact]
    public void TheGroupFilesCarryAtLeastTheImagesFields()
    {
        // billing.json and proxies.json are arrays of groups; the image writes a subset of what the replica models, so the
        // test asks that every image field is present and leaves the replica's extras (order, maxUsage, …) alone.
        var billing = new[] { "id", "name", "profiles" };
        var proxies = new[] { "id", "name", "order", "behaviour", "proxies", "totalDownload", "totalUpload" };

        var billingKeys = WrittenKeys(new Cybersole.Core.Models.BillingGroup());
        var proxyKeys = WrittenKeys(new Cybersole.Core.Models.ProxyGroup());

        _out.WriteLine("BillingGroup: " + string.Join(", ", billingKeys));
        _out.WriteLine("ProxyGroup:   " + string.Join(", ", proxyKeys));

        Assert.Empty(billing.Except(billingKeys));
        Assert.Empty(proxies.Except(proxyKeys));
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('two more parity tests appended')
