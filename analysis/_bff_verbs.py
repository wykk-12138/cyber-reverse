"""One-shot IDAPython: for each John Lewis /bff URL, find its call site and the HTTP verb slot.

Verb slots established earlier in this project:
  0x1408B6310 = vtable +24 = PUT
  0x1408B63B0 = vtable +16 = POST
  0x1408B61E0 = vtable +8  = GET (no body)
Each URL's frozen string is at chars_va; the code reference points at obj_va = chars_va - 12.
"""
import ida_bytes
import ida_funcs
import ida_ua
import idautils

VERBS = {
    0x1408B6310: "PUT",
    0x1408B63B0: "POST",
    0x1408B61E0: "GET",
}

URLS = [
    0x14705D60C, 0x14705D6B4, 0x14705D744, 0x14705D7CC,
    0x14705D83C, 0x14705D8CC, 0x14705D96C, 0x14705DA04,
    0x14705DA94, 0x14705DB14, 0x14705DBA4, 0x14705DC34,
]


def read_str(chars_va):
    head = ida_bytes.get_bytes(chars_va - 12, 12)
    if not head:
        return "<unreadable>"
    ln = int.from_bytes(head[8:12], "little")
    raw = ida_bytes.get_bytes(chars_va, min(ln * 2, 400))
    return raw.decode("utf-16-le", "replace") if raw else ""


def verb_near(ea, span=24):
    """Walk instructions from ea looking for a call to a known verb slot."""
    cur = ea
    for _ in range(span):
        ins = ida_ua.insn_t()
        if ida_ua.decode_insn(ins, cur) == 0:
            break
        if ins.get_canon_mnem() == "call":
            target = ins.ops[0].addr if ins.ops[0].type in (ida_ua.o_near, ida_ua.o_far) else None
            if target in VERBS:
                return VERBS[target], cur
        cur = ins.ea + ins.size
    return None, None


for chars in URLS:
    obj = chars - 12
    text = read_str(chars)
    xrefs = list(idautils.XrefsTo(obj, 0))
    if not xrefs:
        print("%-96s NO-XREF" % text[:96])
        continue
    for x in xrefs:
        fn = ida_funcs.get_func(x.frm)
        verb, at = verb_near(x.frm, 60)
        print("%-96s site=%x func=%s verb=%s at=%s"
              % (text[:96], x.frm,
                 ("%x" % fn.start_ea) if fn else "?",
                 verb or "?", ("%x" % at) if at else "-"))
