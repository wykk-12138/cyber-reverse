"""Session keys a flow writes and never reads back — asked per flow class, not per repository.

The first version of this asked the question repository-wide and got 224 keys, which is not a defect list: the
session is shared, so a store writing `billingZip` for the UI or for another step is doing nothing wrong, and
any key read in exactly one of ninety files swamps the report.

The smell this is actually after is narrower. R1330's shipping rate id and R1331's line id both had the same
shape: **a class extracted a value it needed for its own next request and never looked at it again**. So: for
each class, the keys it writes and no code in that class reads. A key another flow reads is that flow's
business; a key nobody reads anywhere is listed separately, because that one is dead either way.

Usage: python analysis/unconsumed_session_keys.py [--all]
"""
import io
import os
import re
import sys

ROOT = 'replica/src'
WRITE = re.compile(r'Vars\["([^"]+)"\]\s*=(?!=)')
READ = re.compile(r'(?:GetValueOrDefault|TryGetValue|ContainsKey|Remove)\(\s*"([^"]+)"')
INDEX_READ = re.compile(r'(?<![=\s])Vars\["([^"]+)"\](?!\s*=(?!=))')
CLASS_START = re.compile(r'(?:public|internal)\s+(?:sealed\s+)?class\s+(\w+)')


def classes():
    """(file, class name, body) for every class in src, by brace matching."""
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if not name.endswith('.cs'):
                continue
            path = os.path.join(base, name)
            text = io.open(path, encoding='utf-8', errors='replace').read()
            for match in CLASS_START.finditer(text):
                brace = text.find('{', match.end())
                if brace < 0:
                    continue
                depth = 0
                for position in range(brace, len(text)):
                    if text[position] == '{':
                        depth += 1
                    elif text[position] == '}':
                        depth -= 1
                        if depth == 0:
                            yield os.path.relpath(path, ROOT), match.group(1), text[brace:position]
                            break


def main(argv):
    show_all = '--all' in argv
    rows = list(classes())

    all_reads = {}
    for _, _, body in rows:
        for match in list(READ.finditer(body)) + list(INDEX_READ.finditer(body)):
            all_reads[match.group(1)] = all_reads.get(match.group(1), 0) + 1

    self_unread = []
    dead = []
    for path, name, body in rows:
        written = {}
        for match in WRITE.finditer(body):
            written.setdefault(match.group(1), body[:match.start()].count('\n'))
        # Reads inside this class only.
        local = {match.group(1) for match in READ.finditer(body)}
        local |= {match.group(1) for match in INDEX_READ.finditer(body)}

        for key, line in written.items():
            if key in local:
                continue
            if all_reads.get(key, 0) == 0:
                dead.append((path, name, key, line))
            else:
                self_unread.append((path, name, key, line))

    print('classes scanned: %d' % len(rows))
    print()
    print('written by a class that never reads it back, though something else does (%d):' % len(self_unread))
    for path, name, key, line in self_unread[:40 if not show_all else len(self_unread)]:
        print('  %-28s %-34s %s:%d' % (name, key, path, line))

    print()
    print('written and read nowhere in src at all (%d):' % len(dead))
    for path, name, key, line in dead[:40 if not show_all else len(dead)]:
        print('  %-28s %-34s %s:%d' % (name, key, path, line))

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
