import io, re
t = io.open(r'D:\projects\cyber-reverse\replica\tools\mutation-check.py', encoding='utf-8').read()
names = re.findall(r'"name":\s*"([^"]+)"', t)
print('mutations:', len(names))
for n in names:
    print('  -', n.replace('—', '-'))
