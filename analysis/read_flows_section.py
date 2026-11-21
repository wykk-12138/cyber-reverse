"""Read the Flows section of the progress doc with UTF-8 output, so the table is readable."""

import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

lines = io.open('docs/PROGRESS_AND_GAP.md', encoding='utf-8').read().splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith('###') and 'Flows' in line)
for line in lines[start:start + 26]:
    print(line[:160])
