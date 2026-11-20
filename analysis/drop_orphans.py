"""Drop the two orphan lines the dedupe left inside AuthorizeAsync."""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Payments/Gateways.cs'
lines = io.open(P, encoding='utf-8').read().split('\n')

out = []
skipped = 0
for i, line in enumerate(lines):
    # the orphan pair: a retryStatus fail followed by a stray brace, both sitting after the requires_action block
    if (line.strip() == 'return PaymentResult.Fail($"stripe: status {retryStatus}");'
            and i + 1 < len(lines) and lines[i + 1].strip() == '}' and skipped == 0):
        skipped += 2
        continue
    if skipped == 1 and line.strip() == '}':
        skipped += 1
        continue
    out.append(line)

io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('lines %d -> %d' % (len(lines), len(out)))
