import io
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointEvidenceRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '''            var users = lines.Where(l => l.Contains(path, StringComparison.Ordinal)).ToList();'''
new = '''            // R305: prose is allowed to discuss a path without a marker (BstnFlow's doc comment explains what a live
            // capture showed); what must be marked is every line that actually *uses* it.
            var users = lines.Where(l => l.Contains(path, StringComparison.Ordinal)
                                         && !l.TrimStart().StartsWith("//", StringComparison.Ordinal)).ToList();'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('rule limited to code lines')
