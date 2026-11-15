import io
# C#: do not eat "https://..." as a comment
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = t.replace('return Regex.Replace(text, @"//[^\\n]*", " ");',
              'return Regex.Replace(text, @"(?<!:)//[^\\n]*", " ");   // not "https://..."')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('C# stripper keeps URLs')

# python tool: same rule
p2 = r'D:\projects\cyber-reverse\replica\tools\bind_diff.py'
t2 = io.open(p2, encoding='utf-8').read()
if 'def strip_comments' not in t2:
    t2 = t2.replace("blob = '\\n'.join(t for _, t in texts)", '''def strip_comments(s):
    s = re.sub(r'/\\*.*?\\*/', ' ', s, flags=re.S)
    return re.sub(r'(?<!:)//[^\\n]*', ' ', s)

blob = '\\n'.join(strip_comments(t) for _, t in texts)''', 1)
    io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
    print('python tool strips comments too')
