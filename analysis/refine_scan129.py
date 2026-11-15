import io

p = r"D:\projects\cyber-reverse\replica\tools\endpoint-provenance.py"
t = io.open(p, encoding="utf-8").read()

old = '''def inline_scan(pool):
    """Every URL-shaped string literal anywhere in the flows, constants or not."""
    total = 0
    invented = []
    for name in sorted(os.listdir(FLOWS)):
        if not name.endswith(".cs"):
            continue
        body = io.open(os.path.join(FLOWS, name), encoding="utf-8", errors="replace").read()
        for m in INLINE.finditer(body):
            value = m.group(1)
            # skip interpolated templates and obvious fragments
            if "{" in value or value.endswith("/"):
                continue
            total += 1
            if value not in pool:
                line = body[:m.start()].count("\\n") + 1
                invented.append((name, line, value))
    return total, invented'''

new = '''def proven(value, pool):
    """Is this literal, in any reasonable spelling, present in the pool?

    <para>
    R129 refinement. A flow that writes <c>"/cart/add.js"</c> is quoting a literal the image really
    contains as <c>cart/add.js</c>; judging only the slash-prefixed spelling produced false
    "invented" reports (R128's lesson: a wrong checker makes you fix correct code). The path after
    the host is checked too, so a known host plus a known path both count.
    </para>
    """
    if value in pool:
        return True
    bare = value.lstrip("/")
    if bare in pool:
        return True
    if "://" in value:
        rest = value.split("://", 1)[1]
        slash = rest.find("/")
        if slash > 0 and rest[slash:] in pool:
            return True
        if slash > 0 and rest[slash:].lstrip("/") in pool:
            return True
    return False


def inline_scan(pool):
    """Every URL-shaped string literal anywhere in the flows, constants or not."""
    total = 0
    invented = []
    for name in sorted(os.listdir(FLOWS)):
        if not name.endswith(".cs"):
            continue
        body = io.open(os.path.join(FLOWS, name), encoding="utf-8", errors="replace").read()
        for m in INLINE.finditer(body):
            value = m.group(1)
            # skip interpolated templates and obvious fragments
            if "{" in value or value.endswith("/"):
                continue
            total += 1
            if not proven(value, pool):
                line = body[:m.start()].count("\\n") + 1
                invented.append((name, line, value))
    return total, invented'''

if old not in t:
    raise SystemExit("inline_scan anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("provenance matcher is spelling-tolerant")
