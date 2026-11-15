import io
for p, cls in ((r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\CookieEvidenceRatchetTests.cs', 'cookie'),
               (r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\QueryParamEvidenceRatchetTests.cs', 'param')):
    t = io.open(p, encoding='utf-8').read()
    old = '''            Assert.Contains(name, text, StringComparison.Ordinal);
            Assert.Contains("inferred: no image evidence (R297)", text, StringComparison.Ordinal);''' if cls == 'cookie' else '''            Assert.Contains(name, text, StringComparison.Ordinal);
            Assert.Contains("inferred: no image evidence (R298)", text, StringComparison.Ordinal);'''
    marker = '(R297)' if cls == 'cookie' else '(R298)'
    new = '''            // R306: the R305 mutation pass proved that a file-level Contains is satisfied by any other marked line in
            // the same file. The binding is per line: every code line that names this one must carry the marker.
            var users = text.Split('\\n')
                .Where(l => l.Contains(%s, StringComparison.Ordinal)
                            && !l.TrimStart().StartsWith("//", StringComparison.Ordinal))
                .ToList();
            var unmarked = users.Where(l => !l.Contains("inferred: no image evidence", StringComparison.Ordinal)).ToList();
            _out.WriteLine($"{name}: {users.Count} code line(s), {unmarked.Count} unmarked");
            Assert.True(users.Count > 0, "the name is gone: " + %s);
            Assert.True(unmarked.Count == 0, "unmarked use of " + %s + ": " + string.Join(" | ", unmarked.Select(l => l.Trim())));''' % ('name', 'name', 'name')
    assert old in t, p
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
    print('strengthened', cls)
