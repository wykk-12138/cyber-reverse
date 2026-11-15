import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# candidates for the app-side / mobile API the *App and *Dw steps imply
families = {
    "api/app":      r"/api/[a-z0-9_\-/]*app[a-z0-9_\-/]*",
    "mobile":       r"[a-z0-9_\-/\.]*(?:mobile|mapi|/m/)[a-z0-9_\-/\.]*",
    "v1/app":       r"/v\d/[a-z0-9_\-/]*(?:basket|checkout|cart)[a-z0-9_\-/]*",
    "app-api host": r"[a-z0-9\-\.]*(?:app|api)[a-z0-9\-\.]*\.[a-z]{2,}/[a-z0-9_\-/]{4,}",
}

for label, pat in families.items():
    hits = collections.Counter(re.findall(pat, text))
    print("=== %s (%d)" % (label, len(hits)))
    for name, n in hits.most_common(12):
        if len(name) > 70:
            continue
        print("   %-64s %d" % (name, n))
    print()
