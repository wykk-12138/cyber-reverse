import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlow.cs'
t = io.open(p, encoding='utf-8').read()
n = t.count('X-CSRF-Token')
t = t.replace('X-CSRF-Token', 'x-xsrf-token')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('replaced %d occurrence(s) of X-CSRF-Token -> x-xsrf-token (the form the image carries)' % n)
