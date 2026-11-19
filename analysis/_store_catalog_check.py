"""R1172b: does the replica's store catalogue know Jacquemus and Maison Margiela?

The image carries https://www.jacquemus.com/ (0x14709486c), the Jacquemus-Preload controller and the
Maison Margiela regional family (MargielaEU/EU2/APAC/AU/CA) plus Margiela-Preload, and it has full
checkout machines that talk to both. where_is says the string Jacquemus appears nowhere in src, which
would make this a whole-store gap rather than a missing endpoint, so this checks the catalogue itself.
"""
import glob
import io
import os
import re

ROOT = r"D:\projects\cyber-reverse"
hits = []
for pattern in ("**/store_catalog*.py", "**/*store*catalog*.py", "**/stores*.json"):
    hits.extend(glob.glob(os.path.join(ROOT, pattern), recursive=True))
print("catalogue candidates:", len(hits))
for path in sorted(set(hits))[:6]:
    text = io.open(path, encoding="utf-8", errors="replace").read()
    print("=", os.path.relpath(path, ROOT), len(text), "bytes")
    print("   jacquemus:", "acquemus" in text, " margiela:", "argiela" in text)
    # rough entry count: quoted names in a list-of-tuples/dicts
    names = re.findall(r'"([A-Za-z][A-Za-z0-9&.\- ]{2,29})"', text)
    print("   quoted names:", len(names), "sample:", names[:8])
