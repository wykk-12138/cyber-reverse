"""Reconcile the real vendor inventory against the image, name by name. (R807)

Declared: DataDome, PerimeterX, Akamai, Kasada, TrustDecision, Cloudflare, Forter, plus Queue-it in the protocol layer
and five captcha kinds. The image names those and more. What matters is which of the extras belong to the same class as
what is declared -- a fraud-decision vendor is comparable to Forter, a payment gateway is not.
"""

import json
import os
import subprocess
import sys

IDA = r"D:\projects\cyber-reverse\analysis\ida.py"

DECLARED = {
    "DataDome": "datadome",
    "PerimeterX": "perimeterx",
    "Akamai": "akamai",
    "Kasada": "kasada",
    "TrustDecision": "trustdecision",
    "Cloudflare": "cloudflare",
    "Forter": "forter",
    "Queue-it": "queueit",
    "ReCaptcha": "recaptcha",
    "HCaptcha": "hcaptcha",
    "Turnstile": "turnstile",
    "Geetest": "geetest",
}

# Same class as something declared, so a missing one is a real gap.
SAME_CLASS = {
    "Shape": "shape",
    "Signifyd": "signifyd",
    "Riskified": "riskified",
    "AWS WAF": "aws-waf",
    "Datadog RUM": "datadog",
    "Kasada header": "kpsdk",
    "Akamai cookie": "_abck",
}

EXTRA_OUT_OF_CLASS = {
    "Adyen": "adyen",
    "Stripe": "stripe",
    "Braintree": "braintree",
    "Cybersource": "cybersource",
}


def count(pattern):
    out = subprocess.run([sys.executable, IDA, "str", pattern], capture_output=True, text=True)
    i = out.stdout.find("{")
    if i < 0:
        return -1
    try:
        d, _ = json.JSONDecoder().raw_decode(out.stdout[i:])
    except Exception:
        return -1
    return len(d.get("matches", []))


print("  declared vendors against the image:")
for name, pat in DECLARED.items():
    n = count(pat)
    note = "   image: NONE" if n == 0 else ""
    print("    %-16s image=%-4d%s" % (name, n, note))

print()
print("  same class, not declared:")
for name, pat in SAME_CLASS.items():
    n = count(pat)
    print("    %-16s image=%-4d" % (name, n))

print()
print("  out of class (payment gateways), listed for completeness:")
for name, pat in EXTRA_OUT_OF_CLASS.items():
    n = count(pat)
    print("    %-16s image=%-4d" % (name, n))
