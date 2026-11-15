import io

p = r"D:\projects\cyber-reverse\replica\tools\endpoint-provenance.py"
t = io.open(p, encoding="utf-8").read()

# R129: constants were never the whole risk. Inline string literals in method bodies can carry a
# hand-built URL too — NikeFlow's `api.nike.com/buy/orders/v2/...` was exactly that, and the
# constant-only scan reported "0 invented" while it was still there.
old = '''if __name__ == "__main__":
    main()'''

new = '''INLINE = re.compile(r'"(https?://[^"\\s]{8,}|/[a-z0-9][A-Za-z0-9_\\-./{}$:?=&%]{6,})"')


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
            if value not in pool:
                line = body[:m.start()].count("\\n") + 1
                invented.append((name, line, value))
    return total, invented


if __name__ == "__main__":
    main()

    pool = io.open(STRINGS, encoding="utf-8", errors="replace").read()
    total, invented = inline_scan(pool)
    print()
    print("inline URL/path literals: %d   not in pool: %d" % (total, len(invented)))
    for name, line, value in invented:
        print("  INLINE-INVENTED  %-26s :%-5d %s" % (name, line, value[:70]))'''

if old not in t:
    raise SystemExit("main anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("inline literal scan added")
