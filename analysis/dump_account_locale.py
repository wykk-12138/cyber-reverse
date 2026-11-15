import io, re

raw = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\embedded_locale.json",
              encoding="utf-8", errors="replace").read()

pairs = dict(re.findall(r'"([A-Za-z0-9_.]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw))
print("pairs:", len(pairs))

for prefix in ("Settings.Google.", "Settings.PayPal.", "Settings.Email.", "Settings.Imap.",
               "Settings.Aycd.", "Settings.Accounts."):
    hits = {k: v for k, v in pairs.items() if k.startswith(prefix)}
    if not hits:
        continue
    print("\n== " + prefix)
    for k in sorted(hits):
        print("  %-42s = %r" % (k, hits[k]))
