import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # replica\
FLOWS = os.path.join(ROOT, "src", "Cybersole.Stores", "Flows")
STRINGS = os.path.join(os.path.dirname(ROOT), "analysis", "pe_strings.txt")

CLASS = re.compile(r'\b(?:public|internal|private)?\s*static\s+class\s+(\w+)|\b(?:public|internal|private)?\s*(?:sealed\s+)?class\s+(\w+)')
PLAIN = re.compile(r'public const string (\w+)\s*=\s*"([^"]*)"\s*;')
ASSEMBLED = re.compile(r'public const string (\w+)\s*=\s*([A-Za-z_]\w*(?:\s*\+\s*(?:"[^"]*"|[A-Za-z_]\w*))+)\s*;')
TERM = re.compile(r'"([^"]*)"|([A-Za-z_]\w*)')


def scopes(body):
    """Yield (class_name, start, end) for each class body, outermost first."""
    out = []
    for m in CLASS.finditer(body):
        name = m.group(1) or m.group(2)
        brace = body.find("{", m.end())
        if brace < 0:
            continue
        depth = 0
        for i in range(brace, len(body)):
            if body[i] == "{":
                depth += 1
            elif body[i] == "}":
                depth -= 1
                if depth == 0:
                    out.append((name, brace, i))
                    break
    return out


def consts_in(body, start, end, nested):
    """Consts declared *directly* in a scope.

    <para>
    R128: a scope's text contains its nested classes' text, and several classes here declare their
    own <c>Base</c>. Reading the range as one blob collapsed those constants last-wins and resolved
    John Lewis's paths against Scheels' base. The nested ranges are blanked out first.
    </para>
    """
    text = list(body[start:end])
    for n_start, n_end in nested:
        if n_start > start and n_end < end:
            for i in range(n_start - start, n_end - start + 1):
                if 0 <= i < len(text):
                    text[i] = " "
    text = "".join(text)
    plain = dict(PLAIN.findall(text))
    return plain, ASSEMBLED.findall(text)


def resolve(expr, chain):
    parts, ok = [], True
    for literal, ident in TERM.findall(expr):
        if literal:
            parts.append(literal)
        else:
            value = None
            for scope in reversed(chain):          # innermost first
                if ident in scope:
                    value = scope[ident]
                    break
            if value is None:
                return None
            parts.append(value)
    return "".join(parts) if ok else None


def main():
    pool = io.open(STRINGS, encoding="utf-8", errors="replace").read()

    total = proven = invented = unresolved = 0
    problems = []

    for name in sorted(os.listdir(FLOWS)):
        if not name.endswith(".cs"):
            continue
        body = io.open(os.path.join(FLOWS, name), encoding="utf-8", errors="replace").read()

        parsed = []
        for cname, start, end in scopes(body):
            nested = [(o_start, o_end) for _, o_start, o_end, _, _ in
                      [(n, s, e, None, None) for n, s, e in scopes(body)]]
            plain, assembled = consts_in(body, start, end, nested)
            parsed.append((cname, start, end, plain, assembled))

        for cname, start, end, plain, assembled in parsed:
            # enclosing chain: file-level (no scope) + every class containing this one, then self
            chain = [{}]
            for other_name, o_start, o_end, o_plain, _ in parsed:
                if o_start < start and o_end >= end:
                    chain.append(o_plain)
            chain.append(plain)

            for const, value in plain.items():
                if not (value.startswith("/") or "://" in value):
                    continue
                total += 1
                if value in pool:
                    proven += 1
                else:
                    invented += 1
                    problems.append(("INVENTED", name, cname, const, value))

            for const, expr in assembled:
                value = resolve(expr, chain)
                if value is None:
                    unresolved += 1
                    problems.append(("UNRESOLVED", name, cname, const, expr.replace("\n", " ")))
                    continue
                if not (value.startswith("/") or "://" in value or "/" in value):
                    continue
                total += 1
                if value in pool:
                    proven += 1
                else:
                    invented += 1
                    problems.append(("INVENTED", name, cname, const, value))

    print("endpoint constants: %d   verbatim in pool: %d   invented: %d   unresolved: %d"
          % (total, proven, invented, unresolved))
    for kind, file, cname, const, value in problems:
        print("  %-11s %-24s %-22s %-28s %s" % (kind, file, cname, const, value[:64]))


INLINE = re.compile(r'"(https?://[^"\s]{8,}|/[a-z0-9][A-Za-z0-9_\-./{}$:?=&%]{6,})"')


_POOL_LINES = None


def pool_lines(pool):
    """The pool's strings, with the address column stripped, computed once.

    R1016. Two mistakes lived here. `value in pool` searches the file's flat text, so it answers "does
    this appear anywhere", not "is this a string" -- fine for a hit, useless for a prefix. And the pool's
    lines are `0x<addr>  <string>`, not bare strings, so a startswith against a URL never matched while
    the address column was in the way: the first version of this function stripped whitespace only and
    the prefix rule silently matched nothing at all.
    """
    global _POOL_LINES
    if _POOL_LINES is None or _POOL_LINES[0] is not pool:
        strings = set()
        for line in pool.splitlines():
            line = line.strip()
            if not line:
                continue
            # "0x0705312c  https://api.nike.com/product_feed/threads/v2?fields="
            if line.startswith("0x"):
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    line = parts[1]
            strings.add(line)
        _POOL_LINES = (pool, strings)
    return _POOL_LINES[1]


def proven(value, pool):
    """Is this literal, in any reasonable spelling, present in the pool?

    <para>
    R129 refinement. A flow that writes <c>"/cart/add.js"</c> is quoting a literal the image really
    contains as <c>cart/add.js</c>; judging only the slash-prefixed spelling produced false
    "invented" reports (R128's lesson: a wrong checker makes you fix correct code). The path after
    the host is checked too, so a known host plus a known path both count.
    </para>

    <para>
    R1016 refinement. A static prefix is a fragment, and the image carries the full string: the replica
    writes <c>product_feed/threads/v2/</c> where the constant is <c>product_feed/threads/v2?fields=</c>.
    Equality therefore reports a false absence. The rule added here is that a fragment counts as
    evidenced when some pool line starts with it -- which is the actual claim a prefix makes, that the
    image names something beginning this way. A fragment under twelve characters is still not counted,
    because a short prefix starts plenty of unrelated strings.
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

    # the fragment rule: does any image string begin with this prefix?
    for candidate in (value, bare, value.rstrip("/"), bare.rstrip("/")):
        if len(candidate) < 12:
            continue
        for line in pool_lines(pool):
            if line.startswith(candidate):
                return True
    return False


def static_prefix(value):
    """The part of an interpolated template before its first hole.

    R1015. Until this round the scan skipped every value containing "{" as an "interpolated template",
    which meant the whole class of $"...{x}..." literals was never judged at all. Nike's four
    buy/orders/v2 calls are all that shape, so the tool reported "invented: 0" while four live requests
    pointed at a family the image does not contain -- a true answer to a narrower question (R1010's
    domain lesson, this time with a line number).

    The prefix is what can be judged: $"https://api.nike.com/buy/orders/v2/US/{cart}/delivery" makes a
    claim about ".../buy/orders/v2/US/", and that claim is either in the image or it is not. A prefix
    that merely ends on a host is not a claim, so it is left alone.
    """
    hole = value.find("{")
    return value if hole < 0 else value[:hole]


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
            # A path ending in "/" is a prefix by construction, so it can be judged; it used to be skipped.
            total += 1
            if "{" not in value:
                if not proven(value, pool):
                    line = body[:m.start()].count("\n") + 1
                    invented.append((name, line, value))
                continue

            # Interpolated: judge the static prefix, and only when it names more than a host.
            prefix = static_prefix(value)
            if "://" in prefix:
                after_host = prefix.split("://", 1)[1]
                if "/" not in after_host:
                    continue
            if len(prefix) < 12:
                continue
            if not proven(prefix, pool) and not proven(prefix.rstrip("/"), pool):
                line = body[:m.start()].count("\n") + 1
                invented.append((name, line, prefix + "{...}"))
    return total, invented


LEDGER = os.path.join(os.path.dirname(ROOT), "replica", "docs", "ENDPOINT_PROVENANCE.md")
BASELINE = 0           # R201: all 24 judged and registered (live / assembled); the gate now forbids any new one


def ledger_classes():
    """Paths the ledger registers as `live` or `fixture` — allowed to be absent from the pool."""
    if not os.path.exists(LEDGER):
        return set()
    body = io.open(LEDGER, encoding="utf-8", errors="replace").read()
    return set(re.findall(r"-\s+`(?:live|fixture|assembled)`\s+`([^`]+)`", body))


if __name__ == "__main__":
    main()

    pool = io.open(STRINGS, encoding="utf-8", errors="replace").read()
    allowed = ledger_classes()
    total, invented = inline_scan(pool)
    unknown = [row for row in invented if row[2] not in allowed]

    print()
    print("inline URL/path literals: %d   not in pool: %d   registered in ledger: %d"
          % (total, len(invented), len(invented) - len(unknown)))
    print("unknown (invented and unregistered): %d   baseline: %d" % (len(unknown), BASELINE))
    for name, line, value in unknown:
        print("  INLINE-INVENTED  %-26s :%-5d %s" % (name, line, value[:70]))

    if len(unknown) > BASELINE:
        print("FAIL: %d unregistered inline endpoints, above the %d baseline"
              % (len(unknown), BASELINE))
        sys.exit(1)
