import idautils
import re

# Print every literal that holds both a vans host and one of the REST paths, whole and unparsed, so the exact
# spelling including any prefix is read off the image rather than reconstructed.
pat = re.compile(r"vans\.com[^\s]*?/(cart|products)/v\d+/", re.I)

n = 0
for s in idautils.Strings():
    t = str(s)
    if not pat.search(t):
        continue
    n += 1
    print("U\t%x\t%s" % (s.ea, t.replace("\t", " ").replace("\n", "\\n")))
print("total " + str(n))
