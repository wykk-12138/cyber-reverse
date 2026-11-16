"""Split C10's invisible binding members into "compiled away" and "never implemented". (R708)

**Why this exists** (project convention §1.2): `replica/tools/aot_member_coverage.py` reports that only 12 of 819
binding members are visible as functions in the AOT artifact. Its own header correctly refuses to read that as missing
behaviour -- the linker may have trimmed, inlined or folded a member into metadata. But it cannot say *which* members
fall into that bucket, and neither can any other tool here: deciding it needs the source declarations on one side and
the artifact's symbol inventory on the other, which is a cross-check no existing script performs.

**Why now**: R707 re-measured C10 on the rebuilt artifact (12/819, unchanged while the artifact gained 1,358 functions).
That pair of numbers is only interpretable if we know whether the 807 are *compiled away* or *never written*.

**Criterion, fixed before measuring** -- every one of the 819 members lands in exactly one bucket:

    visible          a symbol <Type>__<Member> (or __get_/__set_) exists in the artifact export
    declared-absent  the source declares the member inside the type's body, but no symbol carries it
                     -> compiled away; the product may still work through inlining
    type-absent      no class in source carries the type's name (after applying the triage's renames),
                     so no member could be declared
    undeclared       the type IS in source but the member is not declared in it
                     -> a real gap, and the only bucket that is one

`visible + declared-absent + undeclared` must equal the member count of the in-source types, and `type-absent` accounts
for the rest. The point of the split is that **only `undeclared` is a defect**; the rest are linker behaviour.
"""

import io
import json
import os
import re
import sys

ROOT = r"D:\projects\cyber-reverse"
BINDINGS = os.path.join(ROOT, "replica", "docs", "xaml_bindings.json")
SYMBOLS = os.path.join(ROOT, "analysis", "replica_funcs.txt")
TRIAGE = os.path.join(ROOT, "docs", "TYPE_PRESENCE_TRIAGE.md")
SRC = os.path.join(ROOT, "replica", "src")


def renames():
    """{original simple name: source simple name} from the triage table, so a rename cannot fake a gap."""
    out = {}
    if not os.path.exists(TRIAGE):
        return out
    text = io.open(TRIAGE, encoding="utf-8").read()
    for line in text.splitlines():
        if "**RENAMED**" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        orig = cells[0].strip("`").split(".")[-1]
        m = re.match(r"`([A-Za-z0-9_]+)`", cells[2])
        if orig and m:
            out[orig] = m.group(1)
    return out


def source_classes():
    """({simple name: [declaration text]}, {simple name: [base simple names]}).

    (R708c) A `record` declares its members in the POSITIONAL PARAMETER LIST, not inside braces:

        record Notification(NotificationKind Kind, string Title, string Body, DateTime Timestamp)

    So `Title`/`Timestamp` are real members with no `{ get; }` anywhere, and a body-only scan calls them undeclared.
    The captured text therefore starts at the declaration head and includes the parameter list before the body.

    (R709) The base list matters as much: `Close`, `Save`, `Create`, `Delete` and `Reset` appear on a dozen views
    without being declared on any of them -- they come from a shared view-model base. Reporting those as undeclared
    would be a false gap, so each declaration also records the type names it derives from and the caller walks that
    chain.
    """
    bodies, bases = {}, {}
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d not in ("obj", "bin")]
        for name in filenames:
            if not name.endswith(".cs"):
                continue
            path = os.path.join(dirpath, name)
            text = io.open(path, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"\b(?:class|record|struct|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
                simple = m.group(1)
                start = text.find("{", m.end())
                if start < 0:
                    continue
                head = text[m.start():start]          # declaration head + parameter list + base list
                depth, i = 0, start
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                bodies.setdefault(simple, []).append(head + text[start:i + 1])

                # base list: everything after ':' up to 'where' / the body, split on commas, generic args dropped
                colon = head.find(":")
                if colon >= 0:
                    tail = head[colon + 1:]
                    tail = re.split(r"\bwhere\b", tail)[0]
                    names = []
                    for part in tail.split(","):
                        part = part.split("<")[0].strip()
                        part = part.split(".")[-1].strip()
                        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part or ""):
                            names.append(part)
                    if names:
                        bases.setdefault(simple, []).extend(names)
    return bodies, bases


def declares_in_chain(bodies, bases, type_name, member, _seen=None):
    """True when `member` is declared on the type or anywhere up its base chain."""
    seen = _seen or set()
    if type_name in seen or type_name not in bodies:
        return False
    seen.add(type_name)
    if any(declares(b, member) for b in bodies[type_name]):
        return True
    for base in bases.get(type_name, []):
        if declares_in_chain(bodies, bases, base, member, seen):
            return True
    return False


def visible_symbols():
    """Names of functions in the artifact export, so visibility can be tested type-qualified.

    (R708a) An earlier version of this function collected only the part after `__` and tested the bare member name,
    which reported 378/819 visible against `aot_member_coverage.py`'s 12/819. Both cannot be right: `Name` appears as
    `<SomeOtherType>__Name` in a great many types, so a bare-name test says "visible" for members that no symbol
    carries. The type has to be part of the key, exactly as the coverage tool defines it.
    """
    names = []
    text = io.open(SYMBOLS, encoding="utf-8", errors="replace").read()
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and parts[2]:
            names.append(parts[2])
    return names


def is_visible(symbols, type_name, member):
    """A symbol carrying exactly this type's member -- method, or property getter/setter.

    The leading separator is load-bearing. `aot_member_coverage.py` requires `_<Type><suffix>`; dropping the underscore
    (as an earlier version of this file did) makes the type name a plain suffix, so binding type `Action` matches
    `SmartAction__get_Name` and type `Element` matches `XmlElement__get_Name`. Those two false positives were the whole
    of a 14-vs-12 disagreement between the two tools, and the older, documented rule is the correct one -- the same
    suffix-versus-substring distinction `func_compare.py` records for its own binding probe.
    """
    for suffix in ("__" + member, "__get_" + member, "__set_" + member):
        needle = "_" + type_name + suffix
        for name in symbols:
            if name.endswith(needle):
                return True
    return False


def declares(body, member):
    """A property, method, field or positional record parameter named `member` in this declaration."""
    pat = r"\b%s\s*(?:\{|=>|\(|[;=]|[,)])" % re.escape(member)
    return re.search(pat, body) is not None


def resolve(full_type, rename_map):
    """(simple name, name to look up in source) for a binding-table type.

    (R708d) The binding table spells generic types with an arity marker (`EditValue`1`); the source declares
    `EditValue<T>`, whose identifier stops at the backtick. Applying the triage's rename on top of that gives the
    only name that can exist in source. Exposed so the cross-check script cannot drift from this one.
    """
    simple = full_type.split(".")[-1]
    bare = simple.split("`")[0]
    return simple, rename_map.get(simple, rename_map.get(bare, bare))


def main(argv):
    bindings = json.load(io.open(BINDINGS, encoding="utf-8"))
    rename_map = renames()
    classes, bases = source_classes()
    visible = visible_symbols()

    buckets = {"visible": [], "declared-absent": [], "type-absent": [], "undeclared": []}
    total = 0

    for full_type, members in sorted(bindings.items()):
        simple, resolved = resolve(full_type, rename_map)
        bodies = classes.get(resolved) or classes.get(simple) or classes.get(simple.split("`")[0])
        for member in members:
            total += 1
            if is_visible(visible, resolved, member):
                buckets["visible"].append((full_type, member))
            elif not bodies:
                buckets["type-absent"].append((full_type, member))
            elif declares_in_chain(classes, bases, resolved, member) or declares_in_chain(classes, bases, simple.split(chr(96))[0], member):
                buckets["declared-absent"].append((full_type, member))
            else:
                buckets["undeclared"].append((full_type, member))

    print("binding members total      : %d" % total)
    for key in ("visible", "declared-absent", "undeclared", "type-absent"):
        print("  %-16s %4d  (%.1f%%)" % (key, len(buckets[key]), 100.0 * len(buckets[key]) / total))
    print()
    print("  sum = %d  %s" % (sum(len(v) for v in buckets.values()),
                               "MATCHES" if sum(len(v) for v in buckets.values()) == total else "MISMATCH"))

    if argv and argv[0] == "--undeclared":
        print()
        print("=== the only bucket that is a defect ===")
        for t, m in buckets["undeclared"]:
            print("  %-58s %s" % (t, m))
    if argv and argv[0] == "--type-absent":
        print()
        print("=== members whose type has no class in source ===")
        per_type = {}
        for t, _m in buckets["type-absent"]:
            per_type[t] = per_type.get(t, 0) + 1
        for t, n in sorted(per_type.items(), key=lambda kv: -kv[1]):
            print("  %-58s %3d" % (t, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
