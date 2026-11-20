"""Remove the last two orphan lines (731-733) left inside AuthorizeAsync by the reorder."""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Payments/Gateways.cs'
lines = io.open(P, encoding='utf-8').read().split('\n')

# the orphans are the retryStatus fail, a blank line and a stray brace, immediately before the method's final fail
target = '        return PaymentResult.Fail($"stripe: status {retryStatus}");'
idx = next(i for i, l in enumerate(lines) if l == target)
print('orphan starts at line', idx + 1)

del lines[idx:idx + 3]          # fail + blank + brace
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('lines now', len(lines))
