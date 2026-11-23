"""Scan the file set SourceEncodingTests is about to cover, before enabling it.

Written as a file rather than `python -c` because inline one-liners with nested
quotes and regex escapes have broken repeatedly in this console.
"""
import glob
import io
import os
import re
import sys

PAT = re.compile('\u9225\\?|\u922b\\?|\u95b3\\?|\ufffd')
ROOTS = ['replica/src', 'replica/tests', 'replica/tools', 'replica/docs', 'docs']
EXTS = ('.cs', '.md', '.json', '.ps1', '.py')


def main():
    files = []
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ('obj', 'bin', '__pycache__', '.snapshots', '.mutation-backup')]
            for name in filenames:
                if name.endswith(EXTS):
                    files.append(os.path.join(dirpath, name).replace('\\', '/'))
    print('scanned files: %d' % len(files))
    hits = 0
    for path in files:
        try:
            text = io.open(path, encoding='utf-8').read()
        except UnicodeDecodeError as exc:
            print('NOT-UTF8 %s byte %d' % (path, exc.start))
            hits += 1
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in PAT.finditer(line):
                hits += 1
                print('HIT %s:%d  %s' % (path, lineno,
                                         ' '.join('U+%04X' % ord(c) for c in m.group(0))))
    print('hits: %d' % hits)
    return 0 if hits == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
