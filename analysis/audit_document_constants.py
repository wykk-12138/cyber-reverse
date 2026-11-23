"""Audit every document-shaped string constant in the replica for the damage a paste leaves behind.

R1326 found one constant that had been pasted out of a truncated display and shipped ending in "[4040 chars
total]". One instance means the shape is worth hunting properly rather than by eye.

The first version of this script raised eight alarms and seven were false: it treated "..." as a truncation
marker, but a GraphQL document is full of fragment spreads ("... on ProductVariant", "...Frag"). The eighth —
ShopifyGraphQl.CartSelection — has unbalanced braces and an odd quote count, and that is correct: the pool
stores it as a fragment without its operation header, so it begins with the tail of that header. Both lessons
are in the rules below:

  marker      a truncation notice ("[N chars total]"), a <b>bare</b> ellipsis, TODO, FIXME
  braces      unbalanced { } unless the constant announces itself as a fragment
  quotes      an odd number of quotes unless the constant is a fragment
  ending      a document-shaped constant that does not end with } unless it is a fragment

A fragment is a constant whose body begins with one of ) , " — the tail of a header somebody else supplies.

Usage: python analysis/audit_document_constants.py
"""
import io
import os
import re
import sys

ROOT = 'replica/src'

VERBATIM = re.compile(r'(?:const|static readonly)\s+string\s+(\w+)\s*=\s*@"((?:[^"]|"")*)";', re.S)
REGULAR = re.compile(r'(?:const|static readonly)\s+string\s+(\w+)\s*=\s*"((?:[^"\\]|\\.)*)";')
BARE_ELLIPSIS = re.compile(r'\.\.\.(?!\s*(?:[A-Za-z_]|on\b|\{))')
GQL_HEAD = re.compile(r'^\s*(?:mutation|query|fragment)\s+\w+', re.S)


def is_fragment(body, name=''):
    if body[:1] in (')', ',', '"'):
        return True
    # R1382: an explicitly named *Prefix/*Suffix half of an interpolated query (e.g. ItemPrefix + name + ItemSuffix)
    # is declared as a fragment rather than a standalone document.
    if name.endswith(('Prefix', 'Suffix')):
        return True
    return False


def documents():
    found = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if not name.endswith('.cs'):
                continue
            path = os.path.join(base, name)
            text = io.open(path, encoding='utf-8', errors='replace').read()
            for pattern, verbatim in ((VERBATIM, True), (REGULAR, False)):
                for match in pattern.finditer(text):
                    body = match.group(2)
                    if verbatim:
                        body = body.replace('""', '"')
                    else:
                        body = body.encode('utf-8').decode('unicode_escape', 'replace')
                    # R1382: drop the <200-char blind spot for real GraphQL documents (e.g. 67-char truncated ItemDocument,
                    # 74-char GetCartCookie, 91-char cartCreate, 133-char getSession, 148-char checkoutAsGuest).
                    is_short_gql = len(body) >= 40 and GQL_HEAD.match(body) is not None
                    is_long_doc = len(body) >= 200 and any(signal in body for signal in ('mutation', 'query', 'fragment', '{'))
                    if not (is_short_gql or is_long_doc):
                        continue
                    line = text[:match.start()].count('\n') + 1
                    found.append((os.path.relpath(path, ROOT), line, match.group(1), body))
    return found


def problems_in(body, name=''):
    issues = []
    if 'chars total' in body:
        issues.append('truncation marker')
    if BARE_ELLIPSIS.search(body):
        issues.append('bare ellipsis')
    for word in ('TODO', 'FIXME', 'truncated'):
        if word in body:
            issues.append(word)

    fragment = is_fragment(body, name)
    if not fragment:
        opens, closes = body.count('{'), body.count('}')
        if opens != closes:
            issues.append('braces %d open / %d close' % (opens, closes))
        if body.count('"') % 2:
            issues.append('odd quote count (%d)' % body.count('"'))
        if not body.rstrip().endswith('}'):
            issues.append('does not end with }')
    return issues


def main():
    found = documents()
    print('document-shaped constants: %d' % len(found))

    fragments = [entry for entry in found if is_fragment(entry[3], entry[2])]
    print('of which declared fragments (header supplied by the caller): %d' % len(fragments))

    total = 0
    for path, line, name, body in found:
        issues = problems_in(body, name)
        if not issues:
            continue
        total += 1
        print('  %s:%d  %s (%d chars)  %s' % (path, line, name, len(body), '; '.join(issues)))

    print()
    print('constants with a problem: %d of %d' % (total, len(found)))
    return 1 if total else 0


if __name__ == '__main__':
    raise SystemExit(main())
