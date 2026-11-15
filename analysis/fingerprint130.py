import io, re, collections

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

groups = {
    "profile dirs": [r"user-data-dir", r"chrome[-_ ]profile", r"browser[-_ ]profile", r"Profile\s*\d+",
                     r"profiles[/\\]", r"\.profile\b", r"profile_(?:dir|path|folder)"],
    "fingerprint": [r"fingerprint", r"canvas", r"WebGL", r"hardwareConcurrency", r"deviceScaleFactor",
                    r"navigator\.", r"screen\.", r"Intl\.", r"timezone", r"webdriver"],
    "kpsdk / kasada": [r"x-kpsdk-[a-z]+", r"kpsdk", r"Kasada", r"_kpsdk"],
    "profile switches": [r"--profile-directory", r"--user-data-dir", r"--no-first-run", r"--lang=",
                         r"--window-size", r"--disable-", r"--enable-"],
}

for label, pats in groups.items():
    print("=== " + label)
    seen = set()
    for pat in pats:
        hits = collections.Counter(re.findall(pat, text, re.I))
        for name, n in hits.most_common(8):
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            print("   %-46s %d" % (name[:46], n))
    print()
