"""How many naive "body contains errors" checks remain, and where?"""

import io
import os
import re

NEEDLE = 'Contains("\\"errors\\"", StringComparison.Ordinal)'

for base, dirs, files in os.walk('replica/src'):
    dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
    for name in files:
        if not name.endswith('.cs'):
            continue
        path = os.path.join(base, name)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        for match in re.finditer(re.escape(NEEDLE), text):
            line = text[:match.start()].count('\n') + 1
            print('%s:%d' % (os.path.relpath(path, 'replica/src'), line))
