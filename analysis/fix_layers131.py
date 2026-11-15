import io

p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Scripts\FingerprintLayers.cs"
t = io.open(p, encoding="utf-8").read()

old = '''        "browser (8 fields, per profile)",
        "payload (fingerprint-v1, with or without UA)",
        "dlpa (3-D Secure device profile, from Fingerprint.template.json)",'''

new = '''        "browser: 8 fields, one per profile",
        "payload: fingerprint-v1, with or without UA",
        "dlpa: 3-D Secure device profile from Fingerprint.template.json",'''

if old not in t:
    raise SystemExit("layers anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("layer names simplified")
