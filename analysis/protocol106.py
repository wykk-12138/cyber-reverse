import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

print("=== x-kpsdk-* / kpsdk tokens")
for tok in sorted(set(re.findall(r"[A-Za-z0-9_\-]*kpsdk[A-Za-z0-9_\-]*", text))):
    print("   ", tok)

print()
print("=== queue-it tokens")
for tok in sorted(set(re.findall(r"[A-Za-z0-9_\-\.]*(?:queue-it|Queue-it)[A-Za-z0-9_\-\./]*", text))):
    print("   ", tok[:90])

print()
print("=== trustdevice / tdfp tokens")
for tok in sorted(set(re.findall(r"[A-Za-z0-9_\-]*(?:trustdevice|tdfp|TDID)[A-Za-z0-9_\-\./]*", text))):
    print("   ", tok[:90])
