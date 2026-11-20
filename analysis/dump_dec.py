"""Dump a decompilation to a UTF-8 file (the console cannot carry this text).

Reads the plugin's own decompiler output through the same client the rest of analysis/ uses, so the
file is byte-for-byte what Hex-Rays printed rather than a re-render.
"""
import io
import sys

sys.path.insert(0, 'analysis')
from ida import call  # noqa: E402


def main(argv):
    if len(argv) < 2:
        print('usage: dump_dec.py <hexaddr> <outfile> [--lines N]')
        return 2
    res = call('decompile', {'addr': argv[0], 'max_lines': 20000})
    if isinstance(res, str):
        import json
        res = json.loads(res)
    code = res.get('code') if isinstance(res, dict) else None
    if code is None:
        print('no code in response: %r' % (str(res)[:200],))
        return 1
    io.open(argv[1], 'w', encoding='utf-8', newline='\n').write(code)
    print('wrote %s  %d chars  %d lines' % (argv[1], len(code), code.count('\n') + 1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
