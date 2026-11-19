"""Decode a window of the frozen string pool and list compiler-generated state-machine names.

Why: `ida.py str` finds individual names, but the interesting fact here is the *region* — the runtime keeps the
async state machines' type names in one stretch, so decoding a window and filtering for `<Name>d__N` / `b__N_M`
gives an inventory of which methods exist without chasing each one.

Usage:
    python analysis/name_region.py 0x143383000 0x4000
"""
import json
import re
import subprocess
import sys


def main(argv):
    start = int(argv[0], 16)
    size = int(argv[1], 0) if len(argv) > 1 else 0x4000

    code = ("import ida_bytes; d = ida_bytes.get_bytes(%d, %d); print(d.hex() if d else '')"
            % (start, size))
    out = subprocess.run([sys.executable, 'analysis/ida.py', 'py', code, '--timeout', '600'],
                         capture_output=True, text=True, encoding='utf-8', errors='replace')
    doc = json.JSONDecoder().raw_decode(out.stdout)[0]
    hexstr = (doc.get('stdout') or '').strip().split('\n')[-1]
    blob = bytes.fromhex(hexstr)

    found = []
    i = 0
    while i + 12 <= len(blob):
        length = int.from_bytes(blob[i + 8:i + 12], 'little')
        if 4 <= length <= 120 and i + 12 + length * 2 <= len(blob):
            try:
                text = blob[i + 12:i + 12 + length * 2].decode('utf-16-le')
            except UnicodeDecodeError:
                i += 1
                continue
            if text.isprintable():
                found.append((start + i, length, text))
                i += 12 + length * 2
                continue
        i += 1

    machines = [(a, t) for a, _l, t in found if re.search(r'[<@]([A-Z]\w+)[>@]d__\d+', t)]
    lambdas = [(a, t) for a, _l, t in found if re.search(r'b__\d+_\d+', t)]
    print('window %#x..%#x: %d utf16 strings, %d state machines, %d lambdas'
          % (start, start + size, len(found), len(machines), len(lambdas)))
    for a, t in machines[:40]:
        print('  %#011x %s' % (a, t[:90]))

    # The async state machines are NOT frozen System.String objects: NativeAOT keeps their type names in a packed
    # ASCII table with length prefixes, which is why the UTF-16 pass above saw four strings in a 24 KiB window.
    # Scan printable ASCII runs instead and keep the ones that look like compiler-generated names.
    ascii_hits = []
    run = bytearray()
    run_start = 0
    for idx, byte in enumerate(blob):
        if 0x20 <= byte < 0x7f:
            if not run:
                run_start = idx
            run.append(byte)
        else:
            if len(run) >= 6:
                text = run.decode('ascii')
                if re.search(r'd__\d+|b__\d+_\d+', text):
                    ascii_hits.append((start + run_start, text))
            run = bytearray()
    if len(run) >= 6:
        text = run.decode('ascii')
        if re.search(r'd__\d+|b__\d+_\d+', text):
            ascii_hits.append((start + run_start, text))
    print('ascii name-table hits: %d' % len(ascii_hits))
    for a, t in ascii_hits[:40]:
        print('  %#011x %s' % (a, t[:96]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
