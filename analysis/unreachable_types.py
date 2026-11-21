"""Types nothing outside their own file refers to.

R1343's finding, made into a check. A class was added with twenty kilobytes of source and two documents; the
document constants had callers, so the R1331 invariant was green, and yet the whole class was trimmed from the
artifact because nothing called its methods. The gap was one level up from where the invariant looked.

This counts references to each public type from *other* files. A type used only inside its own file is either a
private helper that was made public by mistake, or — worse — an API surface that no step reaches, which AOT will
drop without complaint.

The report is a candidate list, not a verdict: view classes are instantiated from XAML, some types are resolved by
reflection, and tests do not count as production callers here. Each entry needs a reason before it is either wired
or deleted.

Usage: python analysis/unreachable_types.py [--all]
"""
import io
import os
import re
import sys

ROOT = 'replica/src'
DECL = re.compile(r'^\s*public\s+(?:static\s+|sealed\s+|abstract\s+|partial\s+)*(?:class|record|struct)\s+(\w+)', re.M)


def files():
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in names:
            if name.endswith('.cs'):
                path = os.path.join(base, name)
                yield path, io.open(path, encoding='utf-8', errors='replace').read()


def main(argv):
    show_all = '--all' in argv
    sources = list(files())

    declarations = []
    for path, text in sources:
        for match in DECL.finditer(text):
            declarations.append((path, match.group(1)))

    print('public types declared: %d' % len(declarations))
    print()

    unreachable = []
    for path, name in declarations:
        pattern = re.compile(r'\b' + re.escape(name) + r'\b')
        outside = 0
        for other_path, text in sources:
            if other_path == path:
                continue
            outside += len(pattern.findall(text))
        if outside == 0:
            unreachable.append((path, name))

    unreachable.sort()
    print('types no other file refers to: %d' % len(unreachable))
    for path, name in unreachable if show_all else unreachable[:60]:
        print('   %-52s %s' % (os.path.relpath(path, ROOT), name))

    if not show_all and len(unreachable) > 60:
        print('   ... %d more (--all)' % (len(unreachable) - 60))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
