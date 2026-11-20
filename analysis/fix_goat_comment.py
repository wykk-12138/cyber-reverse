"""R1288: the GoatFlow comment said the flow never used the account paths; the code has used all of them since R328.

Two facts from the artifact (strings 1470939FC…147093BA4) make the claim wrong twice over: all five paths are in the
image as full URLs, and every one of them has a caller in this file.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/GoatFlow.cs'
lines = io.open(P, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines)
             if 'The image carries four /web-api/v1 paths this flow never used' in l)
end = next(i for i, l in enumerate(lines)
           if i > start and 'bodies are not, so every body below is marked inferred' in l)

replacement = [
    '    // The image carries five /web-api paths, each as a full URL, and this flow calls every one of them:',
    '    //   GET  /web-api/get-csrf-token             https://www.goat.com/web-api/get-csrf-token             (1470939FC)',
    '    //   POST /web-api/v1/login                   https://www.goat.com/web-api/v1/login                   (147093B44)',
    '    //   POST /web-api/v1/users/send_otp_token    https://www.goat.com/web-api/v1/users/send_otp_token    (147093BA4)',
    '    //   GET  /web-api/v1/addresses               https://www.goat.com/web-api/v1/addresses               (147093A6C)',
    '    //   GET  /web-api/v1/billing_infos           https://www.goat.com/web-api/v1/billing_infos           (147093AD4)',
    '    //',
    "    // The paths are the image's verbatim. The *bodies* are not: no request body for these five appears anywhere in",
    '    // the artifact, so each body below stays marked inferred until a capture says otherwise. The two product',
    '    // endpoints are a different case — /v1/product_variants/buy_bar_data and /v1/buys answer 0 hits in the string',
    '    // dump, so their paths are inferred as well.',
]

lines[start:end + 1] = replacement
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('replaced lines %d-%d with %d lines' % (start + 1, end + 1, len(replacement)))
