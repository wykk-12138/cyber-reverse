import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

needles = ["mobile-api.scheels.com", "api.parallaxsystems.io", "inbox-api.aycd.io",
           "api2.endclothing.com", "maps.googleapis.com/maps/api"]

for n in needles:
    print("===", n)
    seen = set()
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if n in body:
            key = body.strip()
            if key in seen:
                continue
            seen.add(key)
            print("   ", key[:120])
    print()
