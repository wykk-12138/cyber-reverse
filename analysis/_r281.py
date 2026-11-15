import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()

old = '''def main():
    repair_leftovers()
    results = []

    for m in MUTATIONS:'''
new = '''def main():
    repair_leftovers()
    results = []

    # R281: --limit N (and --only TEXT) so the tool can be smoke-tested cheaply. A full pass takes about an hour
    # because each mutation rebuilds and reruns its guard, which is fine once a session but far too much to check that
    # the harness itself still works.
    limit = None
    only = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--limit" and i + 1 < len(sys.argv) - 1:
            limit = int(sys.argv[i + 2])
        if arg == "--only" and i + 1 < len(sys.argv) - 1:
            only = sys.argv[i + 2]

    selected = MUTATIONS
    if only:
        selected = [m for m in MUTATIONS if only.lower() in m["name"].lower()]
    if limit:
        selected = selected[:limit]

    print(f"running {len(selected)} of {len(MUTATIONS)} mutations")

    for m in selected:'''
assert old in t
t = t.replace(old, new, 1)

# and the summary should not claim a full pass when only part ran
old2 = '''    return results'''
if old2 in t:
    pass
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('mutation-check.py: --limit / --only added')
