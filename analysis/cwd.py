import io

p = r"D:/projects/cyber-reverse/analysis/.near3.txt"
raw = io.open(p, encoding="utf-8", errors="replace").read()
print("has DrawStores: " + str("DrawStores" in raw))
idx = raw.find("DrawStores")
print(repr(raw[max(0, idx - 260):idx + 200]) if idx > 0 else "not found")

# Where does DrawStores sit relative to the backing-field run, and what kind of name is it?
print("")
print("--- lines around DrawStores in the dump ---")
for line in raw.splitlines():
    if "DrawStores" in line or "documentNumber" in line or "_drawid" in line or "_alias" in line:
        print("  " + line.strip()[:150])
