import io, json, re

paths = [
    r"C:\Users\wykk\AppData\Local\Cybersole\analysis\strings_full.txt",
]
blob = ""
for p in paths:
    try:
        blob += io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        pass

try:
    dump = json.load(io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\strings_dump.json",
                             encoding="utf-8", errors="replace"))
    if isinstance(dump, dict):
        values = list(dump.values())
    else:
        values = dump
    blob += "\n" + "\n".join(str(v) for v in values if isinstance(v, str))
except Exception as ex:
    print("json:", ex)

print("blob chars:", len(blob))

needles = [
    "Connection Error", "Target website unreachable", "Error Submitting Shipping",
    "Getting Shipping Rates", "Invalid Credit Card", "Rate Limit / 429",
    "Tasks hanging", "Payment Error", "Connection Errors", "Task failed",
]
for n in needles:
    hits = [m.start() for m in re.finditer(re.escape(n), blob)]
    print("\n== %s  (%d hits)" % (n, len(hits)))
    for h in hits[:2]:
        print("   ..." + blob[max(0, h - 200):h + 400].replace("\n", " | ") + "...")
