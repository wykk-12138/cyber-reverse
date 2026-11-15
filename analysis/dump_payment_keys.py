import io
import re

raw = io.open(r"C:\Users\wykk\AppData\Local\Cybersole\analysis\embedded_locale.json",
              encoding="utf-8", errors="replace").read()

# The dump is truncated mid-string, so parse the "key": "value" pairs with a regex instead.
pairs = re.findall(r'"([A-Za-z0-9_.]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
print("pairs:", len(pairs))

for key, value in pairs:
    if "Payment" in key or "3DS" in key or "Browser" in key:
        print("%-48s = %r" % (key, value))
