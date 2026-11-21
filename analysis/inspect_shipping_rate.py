"""What does UpdateShippingRate need, and who sends UpdateShippingAddress today?"""

import io
import re

QUERIES = 'replica/src/Cybersole.Stores/Flows/WarhammerQueries.g.cs'
FLOWS = 'replica/src/Cybersole.Stores/Flows/RetailFlows.cs'

text = io.open(QUERIES, encoding='utf-8').read()
match = re.search(r'UpdateShippingRate\s*=\s*@"(.*?)";', text, re.S)
body = match.group(1).replace('""', '"')
print('UpdateShippingRate: %d chars' % len(body))
print(body[:600].replace('\n', ' | '))
print()

flows = io.open(FLOWS, encoding='utf-8').read()
for name in ('SubmitShippingAsync', 'UpdateShippingAddress', 'shippingRateId'):
    hits = []
    for match in re.finditer(r'\b' + name + r'\b', flows):
        hits.append(flows[:match.start()].count('\n') + 1)
    print('%-22s %d occurrence(s) at lines %s' % (name, len(hits), hits[:8]))
