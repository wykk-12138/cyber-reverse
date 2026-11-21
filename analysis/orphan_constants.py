"""Constants in replica/src that nothing else in replica/src refers to.

R1329 was a round spent on one orphan (CustomerCartDocument, declared in R1320, referenced only by its own
declaration and by tests). One was found by accident; this finds the class. It matters more here than in most
codebases because the replica is compared to a native image by behaviour: a constant nothing sends is a piece of
fidelity that does not exist, and under AOT it is also the first thing to disappear (R1310).

Reference counting is source-level, which is the point — it answers "does any production code name this?", not
"is the bytes in the artifact". Tests are counted separately, because a constant referenced only by tests is
still a constant the product cannot send.

Usage: python analysis/orphan_constants.py [--min-chars N] [--all]
"""
import io
import os
import re
import sys

ROOT = 'replica/src'
TEST_ROOT = 'replica/tests'

DECL = re.compile(
    r'(?:public|internal|private|protected)?\s*(?:const|static readonly)\s+string\s+(\w+)\s*=', re.M)


def sources(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if name.endswith('.cs'):
                path = os.path.join(base, name)
                yield path, io.open(path, encoding='utf-8', errors='replace').read()


def main(argv):
    minimum = int(argv[argv.index('--min-chars') + 1]) if '--min-chars' in argv else 0
    show_all = '--all' in argv

    declarations = []
    production = {}
    for path, text in sources(ROOT):
        production[path] = text
        for match in DECL.finditer(text):
            name = match.group(1)
            line = text[:match.start()].count('\n') + 1
            value = ''
            tail = text[match.end():match.end() + 400]
            literal = re.search(r'@"((?:[^"]|"")*)"', tail, re.S) or re.search(r'"((?:[^"\\]|\\.)*)"', tail)
            if literal:
                value = literal.group(1)
            declarations.append((path, line, name, len(value)))

    tests = {}
    for path, text in sources(TEST_ROOT):
        tests[path] = text

    print('constants declared in src: %d' % len(declarations))
    print()

    orphans = []
    for path, line, name, length in declarations:
        if length < minimum:
            continue
        uses = 0
        for other_path, text in production.items():
            uses += len(re.findall(r'\b' + re.escape(name) + r'\b', text))
        uses -= 1                                  # the declaration itself
        test_uses = sum(len(re.findall(r'\b' + re.escape(name) + r'\b', text)) for text in tests.values())
        if uses == 0:
            orphans.append((path, line, name, length, test_uses))

    orphans.sort(key=lambda entry: -entry[3])
    for path, line, name, length, test_uses in orphans:
        if not show_all and length < 40:
            continue
        print('  %-58s %-38s %5d chars  tests:%d' % (
            os.path.relpath(path, ROOT) + ':' + str(line), name, length, test_uses))

    print()
    print('constants with no production reference: %d (of %d declared)' % (len(orphans), len(declarations)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
