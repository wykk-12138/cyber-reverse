import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

print("=== every literal containing 'cart/'")
for line in lines:
    if "cart/" in line:
        body = line.split("  ", 1)[-1]
        print("  ", body[:120])

print("\n=== every literal containing 'cart.'")
for line in lines:
    if "cart." in line:
        body = line.split("  ", 1)[-1]
        print("  ", body[:120])
