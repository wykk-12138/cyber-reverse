"""R1285: make the two captcha-provider fields read-only, as the image has them.

Evidence: 1432159dc is `Cybersole.CaptchaProviders.CaptchaProvider,Cybersole.Core.Type!Getter` and the `!Property` twin
at 14363e134 — a getter with no setter. `BalanceSupported` is the same pair (143215d50 / 14363e343). Every other member
in that block (Name, ApiKey, Balance, Count, Concurrency, Priority, IsFetchingBalance) has both accessors, so the
asymmetry is the image's, not ours.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Services/Captcha/Drivers.cs'
text = io.open(P, encoding='utf-8').read()

pairs = [
    ('public string Type { get; set; } = "humanpresence";',
     'public string Type { get; init; } = "humanpresence";'),
    ('public bool BalanceSupported { get; set; }',
     'public bool BalanceSupported { get; init; }'),
]

for old, new in pairs:
    if old not in text:
        print('MISS:', old)
        continue
    text = text.replace(old, new)
    print('ok:', old)

io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
