import sys, io
try:
    import yaml
except ImportError:
    print('pyyaml missing'); sys.exit(0)
p = sys.argv[1]
docs = list(yaml.safe_load_all(io.open(p, encoding='utf-8')))
ok = True
for d in docs:
    if isinstance(d, list):
        for item in d:
            if isinstance(item, dict) and 'insert' in item:
                for entry in item['insert']:
                    print('entry id=%-16s serverName=%s' % (entry.get('id'), entry.get('config', {}).get('serverName')))
                    cfg = entry.get('config', {})
                    print('   command=%s args=%s' % (cfg.get('command'), cfg.get('args')))
print('parsed documents:', len(docs))
