"""R1295 (cont.): prove the round-1077 guard is no longer decorative, one round at a time.

Applies the mutation by hand, runs only the guard that is supposed to catch it, and restores the file in a finally so a
failure cannot leave the tree mutated.
"""

import io
import subprocess
import sys

FLOW = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/FarfetchFlow.cs'
GOOD = ('            "farfetch: product route unrecorded locally \u2014 it is a server-delivered connect/app config '
        'entry, schema needs the original login to capture");')
BAD = '            "farfetch: product failed");'

original = io.open(FLOW, encoding='utf-8').read()
if GOOD not in original:
    raise SystemExit('good text not found — tree may already be mutated')

try:
    io.open(FLOW, 'w', encoding='utf-8', newline='\n').write(original.replace(GOOD, BAD))
    print('mutated; running the guard ...')
    r = subprocess.run(
        ['D:/tools/dotnet8/dotnet.exe', 'test',
         'tests/Cybersole.Tests/Cybersole.Tests.csproj',
         '--filter', 'FullyQualifiedName~FarfetchIsCoveredByTheOriginalTests',
         '-m:1', '--no-build'],
        cwd='D:/projects/cyber-reverse/replica', capture_output=True, text=True,
        encoding='utf-8', errors='replace')
    tail = [l for l in (r.stdout or '').split('\n') if '失败' in l or '通过' in l]
    print('exit=%d' % r.returncode)
    for l in tail[-2:]:
        print('  ' + l.strip()[:110])
    print('VERDICT:', 'guard fired (tests went red)' if r.returncode != 0
          else 'STILL DECORATIVE (tests stayed green)')
finally:
    io.open(FLOW, 'w', encoding='utf-8', newline='\n').write(original)
    print('restored')
