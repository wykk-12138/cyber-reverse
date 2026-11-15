import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

rows = []
for line in text:
    m = re.match(r"\s*0x([0-9a-f]+)\s{2}(.*)$", line)
    if not m:
        continue
    addr = int(m.group(1), 16)
    if 0x03d29000 <= addr <= 0x03d2c800:
        rows.append((addr, m.group(2)))

print("entries in the stealth-script region:", len(rows))
for addr, body in rows:
    print("%08x  %s" % (addr, body[:150]))
