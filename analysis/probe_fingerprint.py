"""Read the request and fingerprint layer's actual state: real implementation or placeholder. (R809)

Priority three of the goal is BouncyHttpClient / Http2 / Tls12Client / BrowserIdentity. Before adding anything, check
whether the layer computes a genuine JA3 from a real ClientHello, or merely records a string, and whether any test
proves the two agree.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"

HTTP = os.path.join(ROOT, "src", "Cybersole.Http")
print("  === Cybersole.Http files ===")
for f in sorted(os.listdir(HTTP)):
    if f.endswith(".cs"):
        p = os.path.join(HTTP, f)
        t = io.open(p, encoding="utf-8", errors="replace").read()
        lines = t.splitlines()
        stubby = any(w in t for w in ("NotImplementedException", "TODO", "throw new NotSupported"))
        print("    %-26s %5d lines%s" % (f, len(lines), "   <-- stub marker" if stubby else ""))

print()
for f in ("Ja3.cs", "BouncyTls.cs"):
    p = os.path.join(HTTP, f)
    if not os.path.exists(p):
        print("  %s: missing" % f)
        continue
    t = io.open(p, encoding="utf-8", errors="replace").read()
    print("  === %s: public surface ===" % f)
    for line in t.splitlines():
        s = line.strip()
        if re.match(r"(public|internal)\s+", s) and "(" in s or re.match(r"(public|internal)\s+.*=>", s):
            print("    " + s[:104])
    print()

print("  === tests mentioning ja3 or ClientHello ===")
TESTS = os.path.join(ROOT, "tests")
for base, _d, files in os.walk(TESTS):
    if os.sep + "obj" in base or os.sep + "bin" in base:
        continue
    for f in files:
        if not f.endswith(".cs"):
            continue
        p = os.path.join(base, f)
        t = io.open(p, encoding="utf-8", errors="replace").read()
        if re.search(r"ja3|ClientHello|client_hello", t, re.I):
            n = len(re.findall(r"\[Fact\]|\[Theory\]", t))
            print("    %-46s facts=%d" % (os.path.relpath(p, TESTS), n))
