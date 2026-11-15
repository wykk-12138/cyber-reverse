import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\ChromiumBridge.cs"
t = io.open(p, encoding="utf-8").read()

old = '''                surfaceBody += NavPrune.BodyJs();
                surfaceBody += NavPrune.AudioSessionBodyJs();'''

new = '''                surfaceBody += NavPrune.BodyJs();
                surfaceBody += NavPrune.AudioSessionBodyJs();

                // R170: the two Web Share operations, appended as data properties; and the credentials container as an
                // own non-enumerable property of the instance. Both forward rather than simulate.
                surfaceBody += ForwardingShims.WebShareBodyJs();
                surfaceBody += ForwardingShims.CredentialsBodyJs();'''

if old not in t:
    raise SystemExit("prune anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("forwarding shims spliced")
