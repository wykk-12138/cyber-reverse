import io, re, collections

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()
lines = text.split("\n")

cookies = ["_abck", "bm_sz", "bm_so", "ak_bmsc", "datadome", "px3", "_px3", "pxhd",
           "__cf_bm", "cf_clearance", "kpsdk", "x-kpsdk", "queue-it", "Queue-it",
           "TDID", "tdfp", "trustdevice", "smid", "smidv2"]

print("=== cookie / header names")
for c in cookies:
    n = text.count(c)
    if n:
        print("   %-16s %d" % (c, n))

print()
print("=== window around the tdfp literal")
idx = text.find("static.trustdecision.com/tdfp")
if idx > 0:
    seg = text[max(0, idx - 1500): idx + 3000]
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9_\-\.]{5,60}", seg):
        pass
    seen = set()
    for line in seg.split("\n"):
        body = line.split("  ", 1)[-1].strip()
        if 6 <= len(body) <= 90 and body not in seen:
            seen.add(body)
            print("   ", body)
