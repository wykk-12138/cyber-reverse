"""Dump every (declaring type, property, accessor kinds) triple from the image.

Why this exists (AGENTS.md §1.2): the accessor shape <DeclaringType>,<Property>!Getter|Setter|Property
is the only surviving form of type-to-property structure in a NativeAOT image whose descriptors carry
no cross-references. `rea`'s managed tools need CLR metadata an AOT image does not carry; IDA's
decompiler sees the strings but not their meaning. So the strings are read directly.

R883 wrote a first version of this and compressed each property down to a name, dropping whether it
came from Getter, Setter or Property. shape_audit.py needs that field -- its setter check looks for
'Setter' in the kinds -- and with the field gone the check silently matched nothing and reported zero
mismatches instead of seventy-eight. R886 restores it: one row per (type, property), kinds preserved.

Output format, tab separated, one row per property:
    <DeclaringType>  <PropertyName>  <comma-separated kinds>

Run against the live IDA database:
    python analysis/ida.py py "exec(open(r'.../dump_accessors_v2.py').read(), {})"
"""

import idautils
import os
import re

pat = re.compile(r"([A-Za-z_][\w.<>`+\[\], ]*?),([A-Za-z_][\w.<>`]*?)!(Getter|Setter|Property)")

rows = {}
raw = 0
for s in idautils.Strings():
    t = str(s)
    if "!" not in t:
        continue
    for m in pat.finditer(t):
        raw += 1
        decl, prop, kind = m.group(1), m.group(2), m.group(3)
        decl = decl.split()[0] if " " in decl else decl
        if not decl or not prop:
            continue
        rows.setdefault((decl, prop), set()).add(kind)

types = set(d for d, _ in rows)
kinds = {}
for (_, _p), ks in rows.items():
    for k in ks:
        kinds[k] = kinds.get(k, 0) + 1

print("raw matches %d · distinct (type, prop) %d · distinct types %d" % (raw, len(rows), len(types)))
print("kind counts: %s" % kinds)

out = os.environ.get("OUT", r"D:/projects/cyber-reverse/replica/docs/baseline/recovered_accessors_by_type.txt")
header = """# accessors with declaring type AND accessor kind, recovered from the image (R886)
# format: <DeclaringType> TAB <PropertyName> TAB <comma-separated Getter/Setter/Property>
# source: strings of the shape <Type>,<Prop>!Getter|Setter|Property over idautils.Strings(), whole image
#
# R883 wrote this file with one row per type and a property-name list, dropping the kind. shape_audit.py
# checks for 'Setter' in the kinds, so against that file the check matched nothing and printed zero
# mismatches where the sampled pool gave seventy-eight. R886 restores one row per (type, property) so the
# kind survives; the file is larger and the check works.
#
# Boundary, unchanged from R883: this covers only members the runtime materialised for binding --
# Avalonia controls, view models, Models. Cybersole.Stores appears zero times, so this does not say which
# flow class owns a given Start-prefixed entry.

"""
with open(out, "w", encoding="utf-8", newline="") as f:
    f.write(header)
    for (decl, prop) in sorted(rows):
        f.write("%s\t%s\t%s\n" % (decl, prop, ",".join(sorted(rows[(decl, prop)]))))
print("wrote " + out)
