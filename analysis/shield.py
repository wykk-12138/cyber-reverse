import idautils
import re

# Everything carrying the word shield, plus the literals adjacent to the OTP path. Adjacency is not evidence --
# R876 and R878 established that -- so the adjacency output is a map for orientation, and the co-occurrence
# output (same literal) is the part that can support a claim.
coincide = []
shield_only = []
for s in idautils.Strings():
    t = str(s)
    low = t.lower()
    if "shield" not in low:
        continue
    if "/shield/" in low or "verify_otp" in low:
        coincide.append((s.ea, t))
    else:
        shield_only.append((s.ea, t))

print("with /shield/ or verify_otp: " + str(len(coincide)))
for ea, t in coincide[:12]:
    print("C\t%x\t%s" % (ea, t.replace("\t", " ").replace("\n", "\\n")[:180]))

print("other shield strings: " + str(len(shield_only)))
for ea, t in shield_only[:24]:
    print("S\t%x\t%s" % (ea, t.replace("\t", " ").replace("\n", "\\n")[:140]))
