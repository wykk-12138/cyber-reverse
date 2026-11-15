import io, json, re
seg = [g for g in json.load(io.open(r'D:\projects\cyber-reverse\replica\docs\row_groups_wide.json', encoding='utf-8')) if g['base'] == '0x3388fd2']
print('segment 0x3388fd2:', json.dumps(seg, ensure_ascii=False)[:400] if seg else 'not found')
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
if seg:
    names = [n for _, n in seg[0]['steps']]
    for f in re.finditer(r'new\("(?P<store>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<body>.*?)\n\s*\}(\s*,\s*FlowSource\.\w+)?\);', src, re.S):
        flow_names = re.findall(r'new Step\("([^"]+)"', f.group('body'))
        hit = len(set(names) & set(flow_names))
        if hit: print('  flow %-24s 命中 %d / %d' % (f.group('store'), hit, len(flow_names)))
