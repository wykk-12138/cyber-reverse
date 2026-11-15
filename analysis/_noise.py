import io
p = r'D:\projects\cyber-reverse\replica\tools\bind_diff.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace("NOISE = re.compile(r'^HasMultiple_\\d+$')", "NOISE = re.compile(r'^(HasMultiple|Value)_\\d+$')")
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('noise pattern widened to Value_NN too')
