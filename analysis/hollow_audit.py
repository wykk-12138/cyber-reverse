"""Sample the hollow-step list: for each, is the behaviour already done somewhere else?"""

import io
import os
import re

ROOT = r"D:\projects\cyber-reverse\replica"
SRC = os.path.join(ROOT, "src")

HOLLOW = [
    "GetSession", "VerifySession", "ScrapeVariantAvailability", "CheckPriceLimit",
    "CreateCart", "EditLine", "InitiateCheckout", "SubmitEmail", "SubmitShippingMethod",
    "GetShippingRates", "SubmitBilling", "Login", "CheckLogin", "Register",
    "CompleteRegistration", "SendTwoFactor", "GetScript", "SubmitSensor", "GetCaptcha",
    "EnterRaffle", "GetRaffleData", "ScrapeRaffleForm", "PollRelease", "PollRestock",
    "WaitForRelease", "FindSlot", "GetReleaseFeed", "LoadCountryData", "ProcessResponse",
    "Fill", "GetStructureToken", "BuildDestination", "GetCsrf",
]

files = []
for dp, _d, fs in os.walk(SRC):
    if os.sep + "obj" in dp or os.sep + "bin" in dp:
        continue
    for fn in fs:
        if fn.endswith(".cs"):
            files.append(os.path.join(dp, fn))

texts = {p: io.open(p, encoding="utf-8", errors="replace").read() for p in files}

print("  %-28s %-8s %s" % ("step", "overrides", "other references (files)"))
print("  " + "-" * 78)

for step in HOLLOW:
    overrides = 0
    refs = set()
    for p, t in texts.items():
        base = os.path.basename(p)
        if base == "StoreFlow.cs":
            continue
        if re.search(r"override\s+(?:async\s+)?Task<StepOutcome>\s+" + step + r"Async", t):
            overrides += 1
        # the bare name used anywhere else (not as the definition)
        if re.search(r"\b" + step + r"\b", t):
            refs.add(base)
    print("  %-28s %-8d %s" % (step, overrides, ", ".join(sorted(refs)[:4]) or "-"))