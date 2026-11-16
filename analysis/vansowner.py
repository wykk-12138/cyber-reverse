import idautils
import re

# Which literals hold both a vans token and something that would establish ownership -- a host or one of the
# cart paths. Co-occurrence inside one string is the criterion R893 used and R898 could not satisfy at path
# level, so this asks it directly rather than by proximity.
host = re.compile(r"(www\.vans\.com|vans\.com)")
path = re.compile(r"/(cart|products)/v\d+/")
token = re.compile(r"vans", re.I)

for s in idautils.Strings():
    t = str(s)
    if not token.search(t):
        continue
    h = host.search(t)
    p = path.search(t)
    if not (h or p):
        continue
    print("HIT\t%x\t%d\thost=%s\tpath=%s\n    %s"
          % (s.ea, len(t), bool(h), bool(p), t[:300].replace("\t", " ").replace("\n", "\\n")))
print("done")
