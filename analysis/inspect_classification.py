"""Classify VendorWiring as RENAMED now that the ledger lives in the test project (R1281)."""
import io
import json

P = 'tools/type_classification.json'
doc = json.load(io.open(P, encoding='utf-8'))
types = doc['types']

print('types container:', type(types).__name__)
if isinstance(types, dict):
    sample_key = next(iter(types))
    print('sample key:', sample_key)
    print('sample value:', json.dumps(types[sample_key], ensure_ascii=False)[:300])
else:
    print('sample entry:', json.dumps(types[0], ensure_ascii=False)[:300])
