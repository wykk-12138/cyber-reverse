"""Find a positive control: a method name that certainly survives into the artifact.

R966 concluded Invokers is empty in the artifact because none of the 179 step names appeared. But a negative control only
shows the search works; it cannot show the *set* being searched is stored in a form I am looking for. If NativeAOT keeps
method names in a compressed or hashed metadata table rather than as UTF-16 strings, then zero hits means nothing.

So: find a method that must be reflected on, and whose name therefore must be reachable, and check whether its name is
present. If its name is absent too, R966's conclusion is unproven and the whole check is invalid.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"
ART = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")
art = io.open(ART, "rb").read()
print("  artifact %d bytes" % len(art))

# Candidates: names that reflection must see for the app to start at all.
# 1. Avalonia/XAML binding targets: the app is an Avalonia UI, and bindings resolve by member name at runtime.
# 2. Entry points: Main is invoked by the runtime.
candidates = [
    "Main", "Initialize", "OnFrameworkInitializationCompleted",
    "CreateAll", "RegisterAll", "RegisterCustom",
    "GetCsrfAsync", "GetCartAsync", "SubmitOrderAsync",
    "StoreFlow", "StoreModuleCatalog", "StepActionRunner",
    "Cybersole", "bstn: cart endpoint unknown",
]

print("  %-38s %s" % ("candidate", "utf16 present"))
print("  " + "-" * 60)
for c in candidates:
    print("  %-38s %s" % (c[:36], art.find(c.encode("utf-16-le")) >= 0))

print()
print("  also check UTF-8 and ASCII (in case metadata is stored differently)")
for c in ("StoreFlow", "GetCsrfAsync", "Main"):
    print("  %-20s utf8=%s" % (c, art.find(c.encode("utf-8")) >= 0))