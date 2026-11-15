import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheOriginalBackupFieldsAllExistOnTheModels()
    {
        // R389: this list comes from a backup the ORIGINAL wrote (compact camelCase bytes — this replica wrote indented
        // files until R388, so a compact backup cannot be ours). Extras on the replica side are allowed; a missing image
        // field is not.
        var group = new[]
        {
            "id", "name", "order", "usagePeriod", "usageExpiry", "checkoutLimit", "profileLimit", "monitorDelay",
            "retryDelay", "timeout", "linkedDelays", "pinned", "captchaSource", "cloudflareSolver", "webhooks", "tasks",
        };

        var proxyGroup = new[]
        {
            "id", "name", "order", "maxUsage", "behaviour", "usagePeriod", "usageExpiry", "proxies",
        };

        var solverDoc = new[] { "left", "top", "width", "height", "solvers" };

        void Check(string what, Type type, string[] fields)
        {
            var props = type.GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
            var missing = fields.Where(f => !props.Contains(f)).ToList();
            _out.WriteLine($"{what}: {fields.Length} fields, missing: {missing.Count}");
            Assert.Empty(missing);
        }

        Check("TaskGroup", typeof(TaskGroup), group);
        Check("ProxyGroup", typeof(ProxyGroup), proxyGroup);
        Check("SolverView", typeof(SolverView), solverDoc);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('original-backup pins appended')
