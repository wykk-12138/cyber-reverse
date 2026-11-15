import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\NavPrune.cs"
t = io.open(p, encoding="utf-8").read()

for name in ("get", "create", "preventSilentAccess", "store"):
    old = 'new CredentialsShim("%s", ' % name
    new = 'new CredentialsShim("%s", ' % name
    # rewrite each entry to use the record's positional parameter names in order
    pass

replacements = [
    ('new CredentialsShim("get", 1, implemented: false)', 'new CredentialsShim("get", 1, false)'),
    ('new CredentialsShim("create", 1, implemented: false)', 'new CredentialsShim("create", 1, false)'),
    ('new CredentialsShim("preventSilentAccess", 0, implemented: false)',
     'new CredentialsShim("preventSilentAccess", 0, false)'),
    ('new CredentialsShim("store", 1, implemented: false)', 'new CredentialsShim("store", 1, false)'),
]

for old, new in replacements:
    if old not in t:
        raise SystemExit("entry missing: " + old[:40])
    t = t.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("the entries are positional")
