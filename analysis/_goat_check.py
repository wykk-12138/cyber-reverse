import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
t = io.open(p, encoding='utf-8').read()
print('GoatFlow still has X-CSRF-Token:', 'X-CSRF-Token' in t)
