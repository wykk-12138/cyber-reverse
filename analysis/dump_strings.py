"""Dump every string IDA knows about, once, so later audits are local and complete.

Why this exists: R1247 audited 38 payment paths by calling `ida.py str` once per literal, which works but costs one
round trip each and cannot scale to the flow layer's several hundred literals. IDA's own string list is the full
inventory (as opposed to analysis/pe_strings.txt, which R816 established is a sample), so dumping it once turns every
later "is this literal attested" question into a local lookup over complete data.

The dump is written by IDA on this machine, because the plugin's py passthrough truncates stdout near four kilobytes
and cannot carry a multi-megabyte listing.

Usage:
    python analysis/dump_strings.py            # writes analysis/ida_strings.txt
"""
import json
import subprocess
import sys

IDA_CODE = r'''
import idautils, json
out = open(r'D:\projects\cyber-reverse\analysis\ida_strings.txt', 'w', encoding='utf-8', errors='replace')
n = 0
for s in idautils.Strings():
    try:
        text = str(s)
    except Exception:
        continue
    if not text:
        continue
    out.write('%x\t%s\n' % (s.ea, text.replace('\n', '\\n').replace('\r', '\\r')))
    n += 1
out.close()
print('STRINGS %d' % n)
'''

out = subprocess.run([sys.executable, 'analysis/ida.py', 'py', IDA_CODE, '--timeout', '1800'],
                     capture_output=True, text=True, encoding='utf-8', errors='replace')
doc = json.JSONDecoder().raw_decode(out.stdout)[0]
print('stdout:', (doc.get('stdout') or '').strip()[:120])
err = (doc.get('stderr') or '').strip()
if err:
    print('stderr:', err[:300])
