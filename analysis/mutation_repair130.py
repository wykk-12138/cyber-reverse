import io

p = r"D:\projects\cyber-reverse\replica\tools\mutation-check.py"
t = io.open(p, encoding="utf-8").read()

# R130: a killed run leaves a mutation in place — that is exactly what happened (ChromiumBridge held
# "131.0.0.0" for several rounds of verification and the UA test read it as a regression). Write a
# backup before mutating and clear it after, so a later run can repair the tree first.
old = '''    original = io.open(path, encoding="utf-8").read()'''

new = '''    original = io.open(path, encoding="utf-8").read()

    # keep a crash-proof copy so an interrupted run can be repaired by the next one
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mutation-backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup = os.path.join(backup_dir, os.path.basename(path).replace(os.sep, "_"))
    with io.open(backup, "w", encoding="utf-8", newline="") as handle:
        handle.write(original)'''

if old not in t:
    raise SystemExit("original anchor missing")
t = t.replace(old, new, 1)

# repair pass at startup
anchor = "def main():"
repair = '''def repair_leftovers():
    """Restore any file a killed run left mutated.

    <para>
    The mutation is applied with a marker comment (<c>MUTATED</c>) so a leftover is visible from the
    file alone; this pass rewrites the affected files from the backup directory before anything runs.
    </para>
    """
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mutation-backup")
    if not os.path.isdir(backup_dir):
        return 0

    repaired = 0
    for name in os.listdir(backup_dir):
        target = os.path.join(REPO, "src", name.replace("_", os.sep))
        if not os.path.exists(target):
            continue
        current = io.open(target, encoding="utf-8").read()
        if "MUTATED" not in current:
            continue
        saved = io.open(os.path.join(backup_dir, name), encoding="utf-8").read()
        with io.open(target, "w", encoding="utf-8", newline="") as handle:
            handle.write(saved)
        repaired += 1
        print("repaired a leftover mutation: " + name)

    return repaired


def main():'''

if anchor not in t:
    raise SystemExit("main anchor missing")
t = t.replace(anchor, repair, 1)

# clear the backups once a run finishes green
old_tail = '''    print("restored tree: GREEN")'''
new_tail = '''    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mutation-backup")
    if os.path.isdir(backup_dir):
        for name in os.listdir(backup_dir):
            os.remove(os.path.join(backup_dir, name))

    print("restored tree: GREEN")'''
if old_tail in t:
    t = t.replace(old_tail, new_tail, 1)

if "import os" not in t.split("\n")[0:12]:
    t = t.replace("import io", "import io\nimport os", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("mutation-check can repair a leftover mutation")
