import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\analysis\pe_strings.txt"
lines = io.open(p, encoding="utf-8", errors="replace").read().split("\n")

# Only the documents that look like cart operations: the mutation/query text itself.
for line in lines:
    body = line.split("  ", 1)[-1]
    low = body.lower()
    if "cart" in low and ("mutation" in low or "query" in low) and len(body) > 60:
        print("LEN", len(body))
        print(repr(body))
        print()
