import io, re

p = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# The Fingerprint model's own fields sit in one cluster; find it by the fields we already saw.
targets = ("ColorDepth", "DeviceMemory", "HardwareConcurrency", "PixelRatio", "ScreenWidth")
for line in text.split("\n"):
    body = line.split("  ", 1)[-1]
    if sum(1 for t in targets if t in body) >= 3:
        names = re.findall(r"<([A-Z][A-Za-z0-9]+)>k__BackingField", body)
        print("cluster fields:", " ".join(names))
        print()
        print("raw:", body[:600])
        break
