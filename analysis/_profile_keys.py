import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for pat in ("Profiles?\\.[\w.]*Card[\w.]*", "Profiles?\\.[\w.]*Username[\w.]*", "Usernames?"):
    hits = sorted(set(re.findall(r'"([\w.]*' + pat[3:] if False else '"([^"]{0,40})"', raw)))[:0]
for k in sorted(set(re.findall(r'"([A-Z][\w.]*(?:Card|Username)[\w.]*)"', raw)))[:10]:
    print('   ', k)
