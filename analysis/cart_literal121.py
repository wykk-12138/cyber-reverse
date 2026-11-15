import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

# The literal that carries CartApiObjectCreate is one class's own run.
for needle in ("CartApiObjectCreate", "AddToCartGraphQL", "GetCartAvailabilityGraphql",
               "CompletePayPalGuestPayment", "AddToCartStoreFront"):
    print("===", needle)
    seen = set()
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if needle in body:
            if body in seen:
                continue
            seen.add(body)
            steps = re.findall(r"<([A-Za-z][A-Za-z0-9_]*)>d__(\d+)", body)
            if steps:
                print("   run:", "  ".join("%s:%s" % (o, n) for n, o in steps))
            else:
                print("   plain:", body[:120])
    print()
