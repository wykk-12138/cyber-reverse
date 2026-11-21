"""Route the shipping posts through the same host seam the payment posts use."""

import io

PATH = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'
text = io.open(PATH, encoding='utf-8', newline='').read()

pairs = [
    ('        var res = await PostJsonAsync(c, ApiHost + "/graphql",\n'
     '            body.ToString(Newtonsoft.Json.Formatting.None), "wh-shipping", ct).ConfigureAwait(false);',
     '        var res = await PostJsonAsync(c, ApiHostFor(c) + "/graphql",\n'
     '            body.ToString(Newtonsoft.Json.Formatting.None), "wh-shipping", ct).ConfigureAwait(false);'),
]

for old, new in pairs:
    count = text.count(old)
    if count != 1:
        raise SystemExit('anchor found %d times: %s' % (count, old.splitlines()[0]))
    text = text.replace(old, new)

io.open(PATH, 'w', encoding='utf-8', newline='').write(text)
print('shipping post now goes through ApiHostFor')
