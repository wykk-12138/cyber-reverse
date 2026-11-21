"""Document-shaped constants in replica/src that no production code sends.

`analysis/orphan_constants.py` answers "which constants does nothing reference", and most of what it finds are
explanatory strings — one-paragraph comments somebody wanted in a test. That is tolerable. What is not
tolerable is a *document* with no caller: a GraphQL payload the replica cannot send is fidelity that does not
exist, and under AOT it is the first thing to disappear (R1310). R1329 found one of those by accident
(CustomerCartDocument); this finds the rest.

Usage: python analysis/orphan_documents.py
"""
import io
import os
import re

ROOT = 'replica/src'
DECL = re.compile(r'(?:public|internal|private|protected)?\s*(?:const|static readonly)\s+string\s+(\w+)\s*=', re.M)
SIGNALS = ('mutation', 'query', 'fragment', '{')


def sources(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if name.endswith('.cs'):
                path = os.path.join(base, name)
                yield path, io.open(path, encoding='utf-8', errors='replace').read()


def main():
    files = list(sources(ROOT))
    found = []
    for path, text in files:
        for match in DECL.finditer(text):
            name = match.group(1)
            # Take the declaration's own value: everything up to the terminating semicolon. An earlier version
            # searched the next 4000 characters for the next literal, which attributed a *following* constant's
            # 630-character document to three short ones and reported them as orphans.
            span_end = text.find(';', match.end())
            if span_end < 0:
                continue
            span = text[match.end():span_end]
            literals = re.findall(r'@"((?:[^"]|"")*)"', span, re.S) or re.findall(r'"((?:[^"\\]|\\.)*)"', span)
            body = ''.join(literal.replace('""', '"') for literal in literals)
            if len(body) < 60 or not any(signal in body for signal in SIGNALS):
                continue
            uses = sum(len(re.findall(r'\b' + re.escape(name) + r'\b', other)) for _, other in files) - 1
            if uses == 0:
                found.append((os.path.relpath(path, ROOT), name, len(body)))

    print('document-shaped constants with no production caller: %d' % len(found))
    for path, name, length in sorted(found, key=lambda entry: -entry[2]):
        print('  %-52s %-36s %5d chars' % (path, name, length))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
