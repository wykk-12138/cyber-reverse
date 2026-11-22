"""Print the coverage ratio explicitly, so "replica declares 64" cannot be read as "64 of 65 carried" again."""

import io

PATH = 'analysis/operation_gap.py'
text = io.open(PATH, encoding='utf-8').read()

old = """print('replica: %d operations' % len(replica))
print()"""
new = """print('replica: %d operations' % len(replica))
# R1377: these two numbers answer different questions and I read one as the other for three rounds. Say the ratio.
covered_now = len(set(image) & set(replica))
print('carried: %d of %d image operations (absent %d)' % (
    covered_now, len(image), len(set(image) - set(replica))))
print()"""
if old not in text:
    raise SystemExit('print block not found')
io.open(PATH, 'w', encoding='utf-8', newline='').write(text.replace(old, new, 1))
print('ratio line added')
