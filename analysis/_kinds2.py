import io, json, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
kinds = json.loads(re.match(r'\s*const GLOBAL_KINDS = (.*)$', src[160016][12:]).group(1).strip().rstrip(';'))
for k, v in kinds.items():
    if isinstance(v, str):
        print('STR', k, '->', v)
print('---- object rows without tag ----')
for k, v in kinds.items():
    if isinstance(v, dict) and 'tag' not in v:
        print('OBJ', k, '->', v)
