"""Locate U+FFFD replacement characters in tracked TEXT files.

Why not grep: the console renders UTF-8 Chinese as mojibake, so a visual scan
lies about which side is broken. This decodes bytes as UTF-8 and reports the
codepoint escapes of the neighbourhood instead of the raw characters, so the
report itself can never carry a broken sample into a document (AGENTS.md §2.5).

Scope: only extensions that are text by contract. Binary artefacts (.png, .ico,
.pyc, .bin, .exe, .i64) legitimately contain 0xFF bytes that decode to U+FFFD;
they are not encoding defects and are skipped.
"""
import io
import subprocess
import sys

TEXT_EXT = {'.md', '.cs', '.py', '.json', '.csproj', '.sln', '.axaml', '.xaml',
            '.txt', '.yml', '.yaml', '.props', '.targets', '.config', '.editorconfig'}
SKIP_DIRS = ('/.git/', '/bin/', '/obj/', '/__pycache__/', '/.publish-aot/')


def tracked():
    out = subprocess.run(['git', 'ls-files'], capture_output=True, text=True,
                         encoding='utf-8', errors='replace').stdout
    return [p for p in out.splitlines() if p]


def main():
    hits = 0
    for path in tracked():
        norm = '/' + path.replace('\\', '/')
        if any(d in norm for d in SKIP_DIRS):
            continue
        ext = '.' + path.rsplit('.', 1)[-1].lower() if '.' in path else ''
        if ext not in TEXT_EXT:
            continue
        try:
            with open(path, 'rb') as fh:
                raw = fh.read()
        except OSError as exc:
            print('UNREADABLE %s (%s)' % (path, exc))
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError as exc:
            print('NOT-UTF8  %s  byte %d  %s' % (path, exc.start, exc.reason))
            hits += 1
            continue
        if '\ufffd' not in text:
            continue
        hits += 1
        for lineno, line in enumerate(text.splitlines(), 1):
            if '\ufffd' not in line:
                continue
            col = line.index('\ufffd')
            lo = max(0, col - 12)
            hi = min(len(line), col + 12)
            ctx = ' '.join('U+%04X' % ord(ch) for ch in line[lo:hi])
            print('FFFD      %s:%d  col %d  context=%s' % (path, lineno, col, ctx))
    print('files with defects: %d' % hits)


if __name__ == '__main__':
    sys.exit(main())
