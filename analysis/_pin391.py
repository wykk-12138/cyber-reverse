import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    [Fact]
    public void TheOriginalBackupsNestedObjectsMatchToo()
    {
        // R391: also from the original's own backup. Two of these were only ever guessed before:
        //  - accounts.aycdInbox is a flat object of five fields, not a list;
        //  - a solver document carries window geometry and a "solvers" list whose entries are proxy/filter/account/settings
        //    (Solver.Name / View / Reload are BOUND in the markup but not persisted — binding and persistence differ).
        var aycd = new[] { "apiKey", "templateId", "appGroup", "timeoutSeconds", "enabled" };
        var solverEntry = new[] { "proxy", "filter", "account", "settings" };

        void Check(string what, Type type, string[] fields)
        {
            var props = type.GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
            var missing = fields.Where(f => !props.Contains(f.ToLowerInvariant())).ToList();
            _out.WriteLine($"{what}: {fields.Length} fields, missing: {missing.Count}");
            Assert.Empty(missing);
        }

        Check("AycdInbox", typeof(Cybersole.Core.Models.AycdInbox), aycd);
        Check("Solver", typeof(Solver), solverEntry);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('nested pins appended')
