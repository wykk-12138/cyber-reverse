import io, os, re

POOL = r'D:\projects\cyber-reverse\analysis\pe_strings.txt'
raw = io.open(POOL, encoding='utf-8', errors='replace').read()
pairs = sorted(set(re.findall(r'"(Settings\.[\w.]+)":\s*"([^"\n]{1,120})"', raw)))

SRC = r'D:\projects\cyber-reverse\replica\src'
corpus = []
for dp, _d, fns in os.walk(SRC):
    for fn in fns:
        if fn.endswith('.cs'):
            corpus.append(io.open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read())
text = '\n'.join(corpus)

missing = [(k, v) for k, v in pairs if v not in text]
ok = [(k, v) for k, v in missing if not v.endswith('\\') and len(v) <= 100]
trunc = [(k, v) for k, v in missing if k not in dict(ok)]
print('missing:', len(missing), '| capturable:', len(ok), '| excluded (truncated/too long):', len(trunc))
for k, v in trunc[:6]:
    print('   excluded:', k, '=', v[-40:])

def short(k):
    parts = k.split('.')
    name = parts[-1]
    if parts[-2].lower() in ('tooltip', 'message', 'title'):
        name = parts[-2] + name
    return name

lines = ['', "    // ------------------------------------------------ copy from the image's locale (R416)", '    //',
         "    // The Settings.* values that had no counterpart in the source, captured verbatim. Keys whose pool value is",
         "    // truncated (they end with a backslash) or longer than 100 characters are left out on purpose.",
         "    public static readonly IReadOnlyDictionary<string, string> Copy = new Dictionary<string, string>(StringComparer.Ordinal)",
         '    {']
seen = {}
for k, v in ok:
    name = short(k)
    if name in seen:
        i = 2
        while '%s%d' % (name, i) in seen:
            i += 1
        name = '%s%d' % (name, i)
    seen[name] = k
    esc = v.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('        ["%s"] = "%s",   // %s' % (name, esc, k))
lines.append('    };')
lines.append('')
lines.append("    /// <summary>One of the image's settings strings, by the short name used in <see cref=\"Copy\"/>.</summary>")
lines.append('    public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;')
lines.append('')
block = '\n'.join(lines)

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\SettingsShell.cs"
t = io.open(p, encoding='utf-8').read()
i = t.index('public sealed class SettingsShell')
brace = t.index('{', i); line_end = t.index('\n', brace) + 1
assert 'IReadOnlyDictionary<string, string> Copy' not in t[line_end:line_end + 6000]
t = t[:line_end] + block + t[line_end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('captured', len(ok), 'settings strings;', len(trunc), 'excluded')
