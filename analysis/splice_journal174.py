import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                // R165: the recorded order, applied last among the value writers.'''

new = '''                // R174: the journal, so a same-origin child realm can be patched by path. Last of the installers and
                // before the reseat: it records what exists, it does not create it.
                surfaceBody += PatchJournal.BodyJs();

                // R165: the recorded order, applied last among the value writers.'''

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("journal spliced")
