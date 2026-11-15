import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

for needle in ("AdyenSession", "AdyenPayPalPatchOrder"):
    print("===", needle)
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if needle in body and ">d__" in body:
            steps = re.findall(r"<([A-Za-z][A-Za-z0-9_]*)>d__(\d+)", body)
            if steps:
                print("   " + "  ".join("%s:%s" % (o, n) for n, o in steps))
            else:
                print("   ", body[:160])
            break
    print()
