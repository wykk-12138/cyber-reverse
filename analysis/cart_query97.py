import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

for line in lines:
    body = line.split("  ", 1)[-1]
    if "checkoutUrl,totalQuantity" in body or ("lines(first:250)" in body):
        print("LEN", len(body))
        print(repr(body))
        print()
