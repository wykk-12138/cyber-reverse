"""Every GraphQL-looking string in the image, in one list.

WHY THIS EXISTS: four documents turned up one at a time by grepping for field names I already suspected, and
each time the next one was a surprise. The store of them is a finite, recognisable set -- a GraphQL document
starts with `mutation`, `query`, `fragment` or a bare `{` -- so it can simply be listed, and then the question
"does anything return the cart version" is answered by reading the list instead of guessing another grep.

The strings are UTF-16 in the image, so a match on the decoded form is what counts; the file being read is
`analysis/ida_strings.txt`, which is an **inventory sample** (see AGENTS 2.7b), so this list is a lower bound
on the documents and never evidence that one is absent.

Usage: python analysis/graphql_documents.py [--min N] [--write-doc]
"""
import io
import json
import re
import sys

STRINGS = 'analysis/ida_strings.txt'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

HEAD = re.compile(r'^\s*(mutation|query|fragment|\{)')


def candidates(minimum):
    found = []
    for line in io.open(STRINGS, encoding='utf-8', errors='replace'):
        if '\t' not in line:
            continue
        addr, text = line.split('\t', 1)
        text = text.strip()
        if len(text) < minimum or not HEAD.match(text):
            continue
        try:
            address = int(addr, 16)
        except ValueError:
            continue
        found.append((address, text))
    found.sort()
    return found


def main(argv):
    minimum = 40
    if '--min' in argv:
        minimum = int(argv[argv.index('--min') + 1])

    found = candidates(minimum)
    named = {}
    for address, text in found:
        kind = 'operation'
        if text.lstrip().startswith('fragment'):
            kind = 'fragment'
        elif text.lstrip().startswith('{'):
            kind = 'shorthand'
        name = ''
        match = re.match(r'\s*(?:mutation|query|fragment)\s+(\w+)', text)
        if match:
            name = match.group(1)
        named[address] = {'kind': kind, 'name': name, 'length': len(text), 'text': text}

    print('graphql-looking strings (>= %d chars) in the inventory sample: %d' % (minimum, len(named)))
    for address in sorted(named):
        entry = named[address]
        print('  0x%09X  %-10s %-5d %-28s %s' % (
            address, entry['kind'], entry['length'], entry['name'], entry['text'][:70].replace('\n', '\\n')))
    io.open('analysis/.graphql_documents.json', 'w', encoding='utf-8', newline='').write(
        json.dumps({'%X' % a: v for a, v in named.items()}, ensure_ascii=False, indent=2))
    print('wrote analysis/.graphql_documents.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
