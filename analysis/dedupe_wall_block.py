"""Remove the second copy of the R1282 wall block that the reorder left behind."""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Payments/Gateways.cs'
text = io.open(P, encoding='utf-8').read()

marker = '        // R1282: the wall. The image runs the orange-wall confirm as its own step inside billing'
first = text.find(marker)
second = text.find(marker, first + 10)
print('copies found:', 1 if second < 0 else 2)
if second < 0:
    raise SystemExit(0)

# the duplicate runs from its comment to the final 'return PaymentResult.Fail($"stripe: status {status}");'
fails = [i for i in range(second, len(text)) if text.startswith('        return PaymentResult.Fail($', i)]
if not fails:
    raise SystemExit('final fail line not found')
cut_end = fails[0]
removed = text[second:cut_end]
text = text[:second] + text[cut_end:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('removed %d chars; copies now: %d' % (len(removed), text.count(marker)))
