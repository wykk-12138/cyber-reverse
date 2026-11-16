"""The replica's store catalogue, read from the one place that defines it. (R763)

R762 found this script undercounting 22 against a real 62, and the repo's own DocsConsistencyTests caught it. The
reason is simple and was avoidable: it walked classes deriving from `StoreModuleBase`, while `StoreModuleCatalog.
CreateAll()` wraps most of them as `FlowStoreModule(new XxxFlow(...))`. A flow is not a module subclass, so forty of
them were invisible.

`DocsConsistencyTests` already says what this script should do -- "the script now reads only CreateAll()" -- and
`ParityDocTests` proves that region is parseable. So this does exactly that: it reads `CreateAll()`'s initialiser, and
for each entry either takes the inline arguments (a store registered with an explicit id, name and domains) or resolves
the flow class's own `Id` / `Name` / `Domains` / constructor default.

**Why not an existing tool** (AGENTS.md §1.2): the question is about this repo's own declarations, so no
reverse-engineering tool applies. What mattered was reading the right region, and the repo states which one that is.
"""

import io
import os
import re
import sys

SRC = r"D:\projects\cyber-reverse\replica\src"
REGISTRY = os.path.join(SRC, "Cybersole.Stores", "Modules", "Registry.cs")


def csharp_files():
    for dirpath, dirnames, filenames in os.walk(SRC):
        if "obj" in dirpath or "bin" in dirpath:
            continue
        for name in filenames:
            if name.endswith(".cs"):
                yield os.path.join(dirpath, name)


def create_all_body(text):
    """The initialiser of CreateAll(), or None."""
    m = re.search(r"CreateAll\(\)\s*=>\s*new\s+IStoreModule\[\]\s*\{(.*?)\n\s*\};", text, re.S)
    return m.group(1) if m else None


def class_body(typ):
    """The body of a class by simple name, from any file under src.

    R764: this used to count braces without regard to string literals, so a class holding a `"{"` -- a JSON
    template, a regex, an interpolation -- closed early or never, and the caller reported "class not found" for a
    class that is right there. The diagnosis named the wrong cause too, which is how it survived a round: only the
    parameterless entries call this, so a dozen siblings with inline arguments never exercised it.

    The walk now skips string, character and comment regions. Absence still returns None, but now it means absence.
    """
    pat = re.compile(r"class\s+" + re.escape(typ) + r"\b[^{]*\{")
    for path in csharp_files():
        text = io.open(path, encoding="utf-8", errors="replace").read()
        for m in pat.finditer(text):
            start = m.end() - 1
            depth = 0
            i = start
            n = len(text)
            while i < n:
                ch = text[i]
                if ch == '"':
                    # verbatim strings double their quotes; ordinary ones honour backslash escapes
                    verbatim = i > 0 and text[i - 1] == "@"
                    i += 1
                    while i < n:
                        if text[i] == "\\" and not verbatim:
                            i += 2
                            continue
                        if text[i] == '"':
                            if verbatim and i + 1 < n and text[i + 1] == '"':
                                i += 2
                                continue
                            break
                        i += 1
                elif ch == "'":
                    i += 1
                    while i < n and text[i] != "'":
                        i += 2 if text[i] == "\\" else 1
                elif ch == "/" and i + 1 < n and text[i + 1] == "/":
                    while i < n and text[i] != "\n":
                        i += 1
                elif ch == "/" and i + 1 < n and text[i + 1] == "*":
                    i += 2
                    while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                        i += 1
                    i += 1
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start:i + 1]
                i += 1
    return None


def prop(body, name):
    """An expression-bodied override, or a constructor-chain argument."""
    m = re.search(r"override\s+string\s+" + name + r"\s*=>\s*\"([^\"]*)\"", body)
    if m:
        return m.group(1)
    # R763: the first version accepted only a `: this(...)` chain and reported a dozen entries as
    # "id/name not resolvable". Those classes pass their identity up with `base("kith", "Kith", ...)` instead --
    # the fifth time this session a scanner of mine has assumed one declaration form and read absence into the
    # others. Both chains are accepted now.
    for chain in ("this", "base"):
        if name == "Id":
            m = re.search(r"[:]?\s*" + chain + r"\(\s*\"([^\"]*)\"", body)
            if m:
                return m.group(1)
        if name == "Name":
            m = re.search(r"[:]?\s*" + chain + r"\(\s*\"[^\"]*\"\s*,\s*\"([^\"]*)\"", body)
            if m:
                return m.group(1)
    return None


def props(body):
    m = re.search(r"override\s+IReadOnlyList<string>\s+Domains\s*=>[^;]*;", body, re.S)
    if m:
        return re.findall(r"\"([^\"]+)\"", m.group(0))
    for chain in ("this", "base"):
        m = re.search(r"[:]?\s*" + chain + r"\(\s*\"[^\"]*\"\s*,\s*\"[^\"]*\"\s*,\s*new\[\]\s*\{([^}]*)\}", body)
        if m:
            return re.findall(r"\"([^\"]+)\"", m.group(1))
    return []


ENTRY = re.compile(r"new\s+FlowStoreModule\(\s*new\s+(\w+)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*\)"
                   r"|new\s+(\w+)\s*\(\s*\)", re.S)


def main():
    text = io.open(REGISTRY, encoding="utf-8", errors="replace").read()
    body = create_all_body(text)
    if body is None:
        print("  CreateAll() not found -- the registry shape changed")
        return 1

    rows = []
    for m in ENTRY.finditer(body):
        if m.group(1):
            typ, args = m.group(1), m.group(2)
        else:
            typ, args = m.group(3), ""
        ctor = 'new %s(%s)' % (typ, args)
        # inline registration: new ShopifyFlow("bodega", "Bodega", new[] { "bodega.com" })
        strs = re.findall(r'"([^"]*)"', args)
        if len(strs) >= 2 and "new[]" in args:
            rid, name = strs[0], strs[1]
            doms = re.findall(r'"([^"]+)"', args[args.find("new[]"):])
        else:
            b = class_body(typ)
            if b is None:
                rows.append((typ, "?", "?", [], ctor, "class not found"))
                continue
            rid, name, doms = prop(b, "Id"), prop(b, "Name"), props(b)
            if rid is None or name is None:
                rows.append((typ, "?", "?", doms, ctor, "id/name not resolvable"))
                continue
        rows.append((typ, rid, name, doms, ctor, ""))

    rows.sort(key=lambda r: (r[1] or ""))
    print("  entries in CreateAll(): %d" % len(rows))
    print()
    print("  %-22s %-20s %-38s %s" % ("id", "name", "domains", "flow type"))
    print("  " + "-" * 106)
    for typ, rid, name, doms, ctor, note in rows:
        print("  %-22s %-20s %-38s %s%s" % (
            rid, (name or "")[:20], (", ".join(doms) or "(none)")[:38], typ, ("  << " + note) if note else ""))

    dupes = {}
    for typ, rid, _n, doms, _c, _x in rows:
        for d in doms:
            dupes.setdefault(d, []).append(rid)
    shared = {d: ids for d, ids in dupes.items() if len(ids) > 1}
    print()
    print("  distinct flow types: %d" % len({r[0] for r in rows}))
    print("  domains claimed by more than one entry: %d" % len(shared))
    for d, ids in sorted(shared.items())[:10]:
        print("    %-34s %s" % (d, ", ".join(ids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
