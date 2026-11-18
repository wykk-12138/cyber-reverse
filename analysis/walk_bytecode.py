# WHY THIS EXISTS: the payload's bytecode is a private token stream (docs/KASADA/11 5.27). This walks it
# from a known instruction boundary, following the two jump opcodes, so `configure`'s capability checks
# can be read as operations. No public disassembler knows this format.
#
# Facts this relies on (all established by experiment):
#   * head was captured BEFORE the payload spliced its literal pool out, so a post-splice pc >= 13772
#     lives 6283 words further along in head
#   * __dshDecoded == 28-char random prefix + P.O   =>   P.O = decoded[28:]
#   * odd f -> inline int f>>1 ; f==8 true ; f==24 false ; f==14 null ; f==42 undefined
#   * f==22 -> string, eats two words (len, off) -> P.O[off:off+len]
#   * f==4  -> double, eats two words ; otherwise -> slot f>>5
#   * opcode 63 = unconditional jump (n.m[0] = operand) ; opcode 47 = conditional jump
#
# Usage: python analysis/_walk.py <start_pc> <max_steps>
import io
import json
import re
import sys

ROOT = "D:/projects/cyber-reverse"
payload = io.open(ROOT + "/analysis/kasada/nike-p.js", encoding="utf-8").read()
dump = json.load(io.open(ROOT + "/.tmp-cfg2.json", encoding="utf-8"))
PO = dump["decoded"][28:]
head = dump["head"]

SPLICE_AT = 13772
SPLICE_LEN = 6283
LIMIT = len(head) - SPLICE_LEN


def word(pc):
    return head[pc] if pc < SPLICE_AT else head[pc + SPLICE_LEN]


def effects():
    i = payload.find("u=new Proxy([")
    start = payload.index("[", i) + 1
    spans = []
    depth = 0
    quote = None
    esc = False
    cur = start
    j = start
    while j < len(payload):
        ch = payload[j]
        if quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote:
                quote = None
        else:
            if ch == '"' or ch == "'":
                quote = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                if depth == 0:
                    spans.append((cur, j))
                    break
                depth -= 1
            elif ch == "," and depth == 0:
                spans.append((cur, j))
                cur = j + 1
        j += 1
    out = {}
    for idx, (a, b) in enumerate(spans):
        src = payload[a:b]
        # Every call that consumes a bytecode word counts, not just e(n): r/v/G are the other readers
        # (r = G, v = f, G = slot-by-name) and B's p(e) consumes one for the push target. Counting only
        # e(n) drifts by one word per r(v(...)) operand and corrupts every boundary after it.
        reads = (len(re.findall(r"\be\(n\)", src))
                 + len(re.findall(r"\br\(n\)", src))
                 # v(n) is f(e) = e.m[1] — the frame itself, no operand word. Counting it over-reads.
                 + len(re.findall(r"\bG\(n\)", src))
                 + len(re.findall(r"\bp\(e\)", src)))
        pushes = len(re.findall(r"\ba\(n\s*,", src))
        out[idx] = (reads, pushes)
    return out


def one(pc):
    f = word(pc)
    pc += 1
    if f & 1:
        return ("int", f >> 1), pc
    if f == 4:
        return ("double", (word(pc), word(pc + 1))), pc + 2
    if f == 8:
        return ("true", True), pc
    if f == 22:
        ln, off = word(pc), word(pc + 1)
        return ("str", PO[off:off + ln]), pc + 2
    if f == 14:
        return ("null", None), pc
    if f == 24:
        return ("false", False), pc
    if f == 42:
        return ("undef", None), pc
    return ("slot", f >> 5), pc


def main():
    pc = int(sys.argv[1])
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    fx = effects()
    for _ in range(steps):
        if pc >= LIMIT:
            print("-- out of captured range at pc", pc)
            break
        op = word(pc)
        if op not in fx:
            print("%6d  ?? %s is not an opcode (wrong boundary?)" % (pc, op))
            break
        pops, pushes = fx[op]
        cur = pc + 1
        args = []
        for _ in range(pops + pushes):
            if cur >= LIMIT:
                break
            v, cur = one(cur)
            args.append(v)
        shown = ", ".join(
            ("%s:%s" % (k, repr(v) if k == "str" else v)) for k, v in args)
        print("%6d  op=%-3d  %s" % (pc, op, shown))
        if op == 63 and args and args[0][0] == "int":
            pc = args[0][1]
        else:
            pc = cur


def from_trace():
    """Decode at the pcs the VM actually executed. Correct by construction: no jump guessing."""
    seq = json.load(io.open(ROOT + "/.tmp-cfgseq.json", encoding="utf-8"))
    fx = effects()
    for pc, op in seq:
        if op not in fx:
            print("%6d  ?? %s not an opcode" % (pc, op))
            continue
        pops, pushes = fx[op]
        cur = pc + 1
        args = []
        for _ in range(pops + pushes):
            if cur >= LIMIT:
                break
            v, cur = one(cur)
            args.append(v)
        shown = ", ".join(("%s:%s" % (k, repr(v) if k == "str" else v)) for k, v in args)
        print("%6d  op=%-3d  %s" % (pc, op, shown))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "trace":
        from_trace()
    else:
        main()
