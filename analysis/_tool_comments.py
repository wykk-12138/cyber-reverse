import io
p = r'D:\projects\cyber-reverse\replica\tools\bind_diff.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''def', '''def', 1) if False else t
if 'def strip_comments' not in t:
    t = t.replace("blob = '\\n'.join(t for _, t in texts)",
'''def strip_comments(s):
    s = re.sub(r'/\\*.*?\\*/', ' ', s, flags=re.S)
    return re.sub(r'//[^\\n]*', ' ', s)

blob = '\\n'.join(strip_comments(t) for _, t in texts)''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('bind_diff.py now strips comments too')
