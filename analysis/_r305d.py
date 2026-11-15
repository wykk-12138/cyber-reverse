import io, os
# restore the file first
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
io.open(p, 'w', encoding='utf-8', newline='').write(
    io.open(r'D:\projects\cyber-reverse\analysis\_goat_backup.cs', encoding='utf-8').read())
print('GoatFlow restored')

# tighten the test: EVERY line that uses an unbacked path must carry the marker
p2 = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\EndpointEvidenceRatchetTests.cs'
t = io.open(p2, encoding='utf-8').read()
old = '''            var bound = lines.Any(l => l.Contains(path, StringComparison.Ordinal)
                                       && l.Contains("inferred: no image evidence", StringComparison.Ordinal));

            _out.WriteLine($"{path} in {file}: bound={bound}");
            Assert.True(bound, $"no 'inferred: no image evidence' marker on the line that uses {path} in {file}");'''
new = '''            // R305: "any line" was still too loose — GoatFlow sends /v1/buys from two places, and one marked line
            // satisfied the check for both. Every line that names an unbacked path now has to be marked.
            var users = lines.Where(l => l.Contains(path, StringComparison.Ordinal)).ToList();
            var unmarked = users.Where(l => !l.Contains("inferred: no image evidence", StringComparison.Ordinal)).ToList();

            _out.WriteLine($"{path} in {file}: {users.Count} line(s) use it, {unmarked.Count} unmarked");
            Assert.True(users.Count > 0, $"the path is gone from {file}: {path}");
            Assert.True(unmarked.Count == 0,
                $"unmarked use of {path} in {file}: " + string.Join(" | ", unmarked.Select(l => l.Trim())));'''
assert old in t
io.open(p2, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('test tightened to every-using-line')
