"""Point the two new Warhammer payment tests at their TinyServer."""

import io

PATH = 'replica/tests/Cybersole.Tests/WarhammerGraphQlTests.cs'
text = io.open(PATH, encoding='utf-8').read()

marker = 'ctx.Session.Vars["paymentToken"] = "tok-1";'
replace = marker + '\n        ctx.Session.Vars["wh.apiHost"] = server.BaseUrl;'

count = text.count(marker)
print('paymentToken sites: %d' % count)
if count == 0:
    raise SystemExit('marker not found')
if 'wh.apiHost' in text:
    raise SystemExit('tests already point at the server')

text = text.replace(marker, replace)
io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('added wh.apiHost to %d test sites' % count)
