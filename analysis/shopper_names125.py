import io, re

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
text = io.open(p, encoding="utf-8", errors="replace").read()

needles = ["ShopperDetails", "ShopperIp", "ShopperChallenge", "ShopperClearing",
           "ShopperInfo", "ShopperIpg", "ShopperAuthorize", "ShopperIdentify"]

for n in needles:
    print("===", n)
    seen = set()
    for line in text.split("\n"):
        body = line.split("  ", 1)[-1]
        if n in body and body not in seen:
            seen.add(body)
            print("   ", body[:150])
            if len(seen) >= 3:
                break
    print()
