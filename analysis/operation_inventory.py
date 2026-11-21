"""Which GraphQL operations exist in the image, and which of them the replica does not carry?

The document inventory in docs/GRAPHQL_DOCUMENTS.md was built one document at a time, each time a round needed
one. That approach finds what a round is looking for and nothing else. This asks the complementary question
directly: take every string in the image that begins a GraphQL operation, read the operation's name, and compare
the set with the names the replica's own document constants declare. Anything in the image and not in the replica
is a step the replica cannot send.

Reading every "mutation "/"query " string is the honest version of "the whole inventory": a sample would give a
lower bound and the conclusion here is a set difference, which a sample cannot support.

Usage: python analysis/operation_inventory.py
"""
import io
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

ROOT = 'replica/src'
PATTERN = re.compile(r'(?:mutation|query)\s+(\w+)\s*[\(\{]')


def search(pattern, limit):
    """ida.py str, tolerating its newline-delimited JSON replies."""
    out = subprocess.run([sys.executable, 'analysis/ida.py', 'str', pattern, '--limit', str(limit)],
                         capture_output=True, text=True).stdout
    matches = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith('{'):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        matches.extend(payload.get('matches', []))
    return matches


image = {}
for keyword in ('mutation ', 'query '):
    for match in search(keyword, 800):
        found = PATTERN.match(match['string'])
        if found:
            image.setdefault(found.group(1), match['addr'])

print('operations in the image: %d' % len(image))

replica = {}
for base, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        path = os.path.join(base, name)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        for found in re.finditer(r'(?:mutation|query)\s+(\w+)\s*[\(\{]', text):
            replica.setdefault(found.group(1), path)

print('operations declared by replica constants: %d' % len(replica))

missing = sorted(set(image) - set(replica))
print()
print('in the image, absent from the replica (%d):' % len(missing))
for name in missing:
    print('   %-44s %s' % (name, image[name]))
