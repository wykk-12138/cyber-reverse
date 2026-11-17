"""Check whether step method names reach the artifact, which is the check that does not depend on body strings.

R966 left the string check unable to answer the question: a retained method keeps only some of its literals, so the absence
of a body string says nothing (R964 established this with www.bstn.com present while its own URL string was absent).

Method names are a different question. StepActionRunner.Build walks typeof(StoreFlow).GetMethods, so the trimming tool must
keep method metadata for StoreFlow -- names included -- or that reflection returns nothing and no step can ever be
dispatched. So if a step name is present as a string in the image, its metadata survived, and that is independent of
whether any of its literals did.
"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(ROOT, "src")
ART = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")

art = io.open(ART, "rb").read()
print("  artifact %d bytes" % len(art))

# every step the base class declares
base = io.open(os.path.join(SRC, "Cybersole.Stores", "Flows", "StoreFlow.cs"),
               encoding="utf-8", errors="replace").read()
steps = sorted(set(re.findall(r"public\s+virtual\s+(?:async\s+)?Task<StepOutcome>\s+(\w+)Async", base)))
print("  steps declared on StoreFlow: %d" % len(steps))

present = []
absent = []
for s in steps:
    name = s + "Async"
    if art.find(name.encode("utf-16-le")) >= 0:
        present.append(s)
    else:
        absent.append(s)

print("  step method name present in artifact: %d" % len(present))
print("  step method name absent: %d" % len(absent))
print()

print("  present (first 20): " + ", ".join(present[:20]))
print()
print("  absent  (first 20): " + ", ".join(absent[:20]))
print()

# a control: names that certainly are not in the image
for control in ("NoSuchStepNameAtAll", "ZzzQqqWww"):
    print("  control %-22s present=%s" % (control, art.find(control.encode("utf-16-le")) >= 0))