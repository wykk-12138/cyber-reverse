"""Runs INSIDE IDA. Two leftover questions from R1148.

1. What is v9[9] at the notify-challenge join (line 1967 of sub_141113680)? If it is written from a
   challenge/transaction id field, the "challenge id" reading stops being an inference.
2. Is the callback fragment (0x147163128, "state=undefined&code=undefined&liability_shift=") appended
   whole, or used as a template with the values substituted? The difference decides whether the replica
   may send real state/code values or must send the literal "undefined".
"""
import ida_bytes
import ida_hexrays
import idautils

FRAG = 0x147163128
FRAG_OBJ = FRAG  # the off_ constant is already the object address, not chars_va


def frozen(va):
    head = ida_bytes.get_bytes(va, 12)
    if not head or len(head) < 12:
        return None
    ln = int.from_bytes(head[8:12], "little")
    if not (0 < ln < 200):
        return None
    raw = ida_bytes.get_bytes(va + 12, ln * 2)
    if not raw or len(raw) < ln * 2:
        return None
    try:
        s = raw.decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(ch) < 127 for ch in s) else None


print("== question 2: where the fragment is referenced")
refs = list(idautils.XrefsTo(FRAG_OBJ))
print("   xrefs:", [(hex(r.frm), r.type) for r in refs][:8])
import ida_funcs

for r in refs[:4]:
    fn = ida_funcs.get_func(r.frm)
    if not fn:
        continue
    try:
        code = str(ida_hexrays.decompile(fn.start_ea))
    except Exception as exc:  # noqa: BLE001
        print("   %#x decompile failed: %s" % (fn.start_ea, exc))
        continue
    lines = code.split("\n")
    hits = [i for i, ln in enumerate(lines) if "147163128" in ln]
    print("   fn %#x lines=%d, fragment at %s" % (fn.start_ea, len(lines), hits))
    for h in hits:
        for i in range(max(0, h - 6), min(len(lines), h + 4)):
            mark = ">>" if i == h else "  "
            print("   %s%5d %s" % (mark, i, lines[i].rstrip()[:140]))

print()
print("== question 1: v9[9] in the payment machine")
code = str(ida_hexrays.decompile(0x141113680))
lines = code.split("\n")
writes = [i for i, ln in enumerate(lines) if "v9[9]" in ln or "v9 + 9" in ln or "v9+72" in ln]
print("   lines mentioning v9[9]:", writes[:12])
for i in writes[:8]:
    print("   %5d %s" % (i, lines[i].rstrip()[:150]))
assigns = [i for i, ln in enumerate(lines) if ln.strip().startswith("v9 =") or "v9 =" in ln]
print("   v9 assigned at:", assigns[:8])
for i in assigns[:3]:
    print("   %5d %s" % (i, lines[i].rstrip()[:150]))
