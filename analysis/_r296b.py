import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs'
t = io.open(p, encoding='utf-8').read()
old = '///   * every call carries X-CSRF-TOKEN, lifted from the cookie jar'
new = '///   * every call carries the CSRF header, lifted from the cookie jar (R296: sent as <c>x-xsrf-token</c>,\n///     the form the image carries — the earlier X-CSRF-TOKEN spelling was not in the pool)'
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('GoatFlow comment aligned with the evidence')
