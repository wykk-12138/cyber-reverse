import io, json, re
src = io.open(r'D:\projects\cyber-reverse\analysis\pe_strings.txt', encoding='utf-8', errors='replace').read().splitlines()
kinds = json.loads(re.match(r'\s*const GLOBAL_KINDS = (.*)$', src[160016][12:]).group(1).strip().rstrip(';'))
for k in ('gcrweb', '__gCrWeb', 'webkit', 'hsw', 'Raven', '_sharedLibs', '__wdata', 'speechSynthesis', 'status'):
    print(f'{k:18} -> {kinds.get(k, "(absent)")}')
