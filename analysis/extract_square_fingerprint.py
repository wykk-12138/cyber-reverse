"""Extract the Square Web Payments device fingerprint the image carries, byte for byte.

WHY THIS EXISTS: typing a 900-byte JSON literal by hand is how transcription errors get into a replica and
then into a "the image says X" claim nobody can check. This reads the bytes around the address the string
database already pointed at (0x143385527, in the Casio class's metadata), cuts each JSON object exactly at
its braces while respecting string literals, and can emit a C# verbatim literal.

Two templates sit next to each other in the image:
  - the full one, which begins `{"user_agent":"__UA__"` -- a placeholder the caller fills in;
  - the "SansUa" one, the same object with no user_agent member at all,
    which is what the `ComponentsV1SansUa` name beside them refers to.

Usage:
    python analysis/extract_square_fingerprint.py            # print the parsed facts
    python analysis/extract_square_fingerprint.py --csharp   # emit C# verbatim literals
"""
import json
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402

BASE = 0x143385510
SPAN = 0x1800


def read(base=BASE, span=SPAN):
    res = call('get_bytes', {'regions': [{'addr': hex(base), 'size': span}]})
    if isinstance(res, str):
        res = json.loads(res)
    return base, bytes(int(t, 16) for t in res[0]['data'].split())


def cut_object(blob, start):
    """Return the JSON object beginning at `start`, brace-counted with string-literal awareness."""
    if blob[start:start + 1] != b'{':
        return None
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(blob)):
        ch = blob[i:i + 1]
        if in_string:
            if escaped:
                escaped = False
            elif ch == b'\\':
                escaped = True
            elif ch == b'"':
                in_string = False
            continue
        if ch == b'"':
            in_string = True
        elif ch == b'{':
            depth += 1
        elif ch == b'}':
            depth -= 1
            if depth == 0:
                return blob[start:i + 1]
    return None


def find_all(blob, needle):
    out = []
    at = blob.find(needle)
    while at >= 0:
        out.append(at)
        at = blob.find(needle, at + 1)
    return out


def main(argv):
    base, blob = read()
    print('window 0x%X..0x%X (%d bytes)' % (base, base + len(blob), len(blob)))

    found = {}
    for label, needle in (('with_ua', b'{"user_agent":"__UA__"'), ('sans_ua', b'{"language":"en-US"')):
        sites = find_all(blob, needle)
        print('%-8s sites: %d' % (label, len(sites)))
        if not sites:
            continue
        raw = cut_object(blob, sites[0])
        if raw is None:
            print('  could not find the end of the object')
            continue
        try:
            parsed = json.loads(raw.decode('utf-8'))
        except Exception as exc:                       # noqa: BLE001 - report, do not guess
            print('  not valid JSON: %s' % exc)
            continue
        found[label] = (base + sites[0], raw, parsed)
        print('  0x%X  %d bytes  keys=%d' % (base + sites[0], len(raw), len(parsed)))
        for key in parsed:
            value = parsed[key]
            shown = value if not isinstance(value, list) else '[%d items] %s…' % (
                len(value), json.dumps(value[:2]))
            print('    %-22s %s' % (key, shown))

    if 'with_ua' in found and 'sans_ua' in found:
        a, b = found['with_ua'][2], found['sans_ua'][2]
        print('\nonly in the with-UA template: %s' % sorted(set(a) - set(b)))
        print('only in the SansUa template : %s' % sorted(set(b) - set(a)))
        same = [k for k in a if k in b and a[k] == b[k]]
        print('identical members: %d of %d' % (len(same), len(a)))

    if '--csharp' in argv:
        for label, (_, raw, _) in found.items():
            text = raw.decode('utf-8')
            print('\n// template: %s (%d bytes)' % (label, len(raw)))
            print('public const string %sTemplate = """%s""";'
                  % ('BrowserData' if label == 'with_ua' else 'BrowserDataSansUa', text))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
