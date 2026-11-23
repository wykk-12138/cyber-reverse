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
# R1382: strip comments and string literals before counting identifier references, so a constant like
# `public const string AddCreditCard = "mutation AddCreditCard(..."` cannot count its own GraphQL body
# as a production caller.
STR_AND_COMMENT = re.compile(
    r'@"((?:[^"]|"")*)"'
    r'|"(?:[^"\\]|\\.)*"'
    r'|//[^\n]*'
    r'|/\*.*?\*/',
    re.S,
)


def strip_non_code(text):
    return STR_AND_COMMENT.sub(' ', text)


def sources(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if name.endswith('.cs'):
                path = os.path.join(base, name)
                raw = io.open(path, encoding='utf-8', errors='replace').read()
                yield path, raw, strip_non_code(raw)


def main():
    files = list(sources(ROOT))
    found = []
    same_file_only = []
    for path, text, code_only in files:
        rel = os.path.relpath(path, ROOT)
        for match in DECL.finditer(text):
            name = match.group(1)
            span_end = text.find(';', match.end())
            if span_end < 0:
                continue
            span = text[match.end():span_end]
            literals = re.findall(r'@"((?:[^"]|"")*)"', span, re.S) or re.findall(r'"((?:[^"\\]|\\.)*)"', span)
            body = ''.join(literal.replace('""', '"') for literal in literals)
            if len(body) < 60 or not any(signal in body for signal in SIGNALS):
                continue
            pat = re.compile(r'\b' + re.escape(name) + r'\b')
            in_self = len(pat.findall(code_only)) - 1
            in_other = sum(len(pat.findall(other_code)) for other_path, _, other_code in files if other_path != path)
            if in_self + in_other == 0:
                found.append((rel, name, len(body)))
            elif in_other == 0:
                same_file_only.append((rel, name, len(body), in_self))

    print('document-shaped constants with no production caller: %d' % len(found))
    for path, name, length in sorted(found, key=lambda entry: -entry[2]):
        print('  %-52s %-36s %5d chars' % (path, name, length))
    print('document-shaped constants referenced ONLY inside their defining file: %d' % len(same_file_only))
    for path, name, length, self_refs in sorted(same_file_only, key=lambda entry: -entry[2]):
        print('  %-52s %-36s %5d chars  (self-file refs=%d)' % (path, name, length, self_refs))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
