"""Cross-check `bind_scope`'s 0 with an independent implementation (R585)

`bind_scope.py` reports `types with scope misses: 0` over 152 types, where a member counts as present if it appears in
the type's body **merged with its ancestors'**. A tool that reports zero deserves a second implementation: if two
independently written checks agree, the zero means something; if they disagree, one of them is wrong.

This walks the contract types that can be located, resolves each declaration's base list, merges up to three
ancestors, and asks whether every contract-bound member name appears. Differences from `bind_scope` are what matter:

  * this reports gaps  bind_scope misses      -> bind_scope's 0 is wrong
  * bind_scope reports gaps this does not     -> this is too permissive
  * both zero                                 -> the 0 is corroborated

Deliberately does **not** reuse `bind_scope`'s code: a shared helper would share its bug.

Coverage is a name count. It cannot see semantics, and a member satisfied by an inherited name is counted present
even if the replica overrides it with different behaviour. Read-only.
"""

import glob
import io
import json
import os
import re

REPO = r"D:\projects\cyber-reverse\replica"
BIND = os.path.join(REPO, "docs", "xaml_bindings.json")

NAMESPACE = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
# declaration with an optional base list, then either a brace body or a positional parameter list
DECL = re.compile(
    r"\b(?:class|interface|record|struct)\s+(\w+)\s*(?:<[^>]*>)?\s*(\([^)]*\))?\s*"
    r"(?::\s*([^{;]*?))?\s*(\{|;)")


def scan():
    """name -> {'text': declaration text, 'bases': [names]}"""
    out = {}
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        for d in DECL.finditer(text):
            name = d.group(1)
            params = d.group(2) or ""
            bases = d.group(3) or ""
            start = d.start()
            if d.group(4) == "{":
                brace = d.end() - 1
                depth, i = 0, brace
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                body = text[start:i + 1]
            else:
                body = text[start:d.end()]
            base_names = [b.strip().split("<")[0].split(".")[-1]
                          for b in bases.split(",") if b.strip()]
            prev = out.get(name)
            if prev is None or len(body) > len(prev["text"]):
                out[name] = {"text": params + body, "bases": base_names}
    return out


def merged(name, decls, depth=3, seen=None):
    seen = seen or set()
    if name in seen or depth < 0 or name not in decls:
        return ""
    seen.add(name)
    d = decls[name]
    parts = [d["text"]]
    for b in d["bases"]:
        parts.append(merged(b, decls, depth - 1, seen))
    return "\n".join(parts)


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    decls = scan()

    examined = 0
    gaps = []

    for full in sorted(binds):
        members = list(binds.get(full) or [])
        simple = full.split(".")[-1].split("`")[0]
        if simple not in decls:
            continue
        examined += 1
        text = merged(simple, decls)
        missing = [m for m in members if re.search(r"\b" + re.escape(m) + r"\b", text) is None]
        if missing:
            gaps.append((full, missing, decls[simple]["bases"]))

    print("independent check: types examined : %d" % examined)
    print("                  types with gaps : %d" % len(gaps))
    print()

    if gaps:
        print("=== gaps this implementation finds ===")
        for full, missing, bases in gaps:
            print("  %-50s base=%-24s missing: %s"
                  % (full, ",".join(bases)[:24] or "-", ", ".join(missing[:6])))
    else:
        print("no gaps — corroborates bind_scope's 0 on this set")


if __name__ == "__main__":
    main()
