import io

p = r"D:\projects\cyber-reverse\replica\tools\endpoint-provenance.py"
t = io.open(p, encoding="utf-8").read()

old = '''if __name__ == "__main__":
    main()

    pool = io.open(STRINGS, encoding="utf-8", errors="replace").read()
    total, invented = inline_scan(pool)
    print()
    print("inline URL/path literals: %d   not in pool: %d" % (total, len(invented)))
    for name, line, value in invented:
        print("  INLINE-INVENTED  %-26s :%-5d %s" % (name, line, value[:70]))'''

new = '''LEDGER = os.path.join(os.path.dirname(ROOT), "replica", "docs", "ENDPOINT_PROVENANCE.md")
BASELINE = 24          # R129: the ledger's "待定" count; the gate forbids growth, not existence


def ledger_classes():
    """Paths the ledger registers as `live` or `fixture` — allowed to be absent from the pool."""
    if not os.path.exists(LEDGER):
        return set()
    body = io.open(LEDGER, encoding="utf-8", errors="replace").read()
    return set(re.findall(r"-\\s+`(?:live|fixture)`\\s+`([^`]+)`", body))


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
        sys.exit(1)'''

if old not in t:
    raise SystemExit("main anchor missing")
t = t.replace(old, new, 1)

if "import sys" not in t.split("\n")[0:6]:
    t = t.replace("import io, os, re", "import io, os, re, sys", 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("gate: unknown inline endpoints may not exceed the baseline")
