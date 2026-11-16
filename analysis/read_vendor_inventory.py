"""Read the replica's real vendor inventory: Vendor records, protocol lists, captcha kinds. (R807)

The previous attempt compared the image against nine string literals inside AntiBotVendors and reported eighteen
missing vendors. That was wrong: those literals are specific token keys, while the vendor inventory lives in Vendor
records and in the protocol layer's per-vendor header and cookie lists. Read the actual inventory.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows"

for fname in ("AntiBotVendors.cs", "AntiBotProtocol.cs"):
    p = os.path.join(ROOT, fname)
    t = io.open(p, encoding="utf-8", errors="replace").read()
    print("  === %s (%d lines) ===" % (fname, len(t.splitlines())))
    for line in t.splitlines():
        s = line.strip()
        if re.search(r'new Vendor\(|^\s*\["[^"]+"\]\s*=|public static readonly IReadOnlyList', s):
            print("    " + s[:110])
    print()

cap = r"D:\projects\cyber-reverse\replica\src\Cybersole.Services\Captcha\CaptchaSolverService.cs"
t = io.open(cap, encoding="utf-8", errors="replace").read()
for line in t.splitlines():
    if "enum CaptchaKind" in line:
        print("  === CaptchaKind ===")
        print("    " + line.strip()[:110])
