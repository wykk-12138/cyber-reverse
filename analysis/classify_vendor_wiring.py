"""Classify VendorWiring as RENAMED now that the ledger lives in the test project (R1281).

Schema is a dict keyed by the absent type's full name, each value carrying kind/to/evidence — matching the existing
entries rather than inventing a shape.
"""
import io
import json

P = 'tools/type_classification.json'
doc = json.load(io.open(P, encoding='utf-8'))
types = doc['types']

name = 'Cybersole.Stores.Scripts.VendorWiring'
types[name] = {
    'kind': 'renamed',
    'to': 'VendorAuditTable',
    'evidence': ('tests/Cybersole.Tests/VendorAuditTable.cs — the vendor audit table is a ledger, and AGENTS.md §3 keeps '
                 'ledgers out of src/; R1281 moved the file and its four remaining consumers into the test project'),
}

io.open(P, 'w', encoding='utf-8', newline='\n').write(json.dumps(doc, indent=2, ensure_ascii=False) + '\n')
print('classified %s -> %s; total entries %d' % (name, 'VendorAuditTable', len(types)))
