import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs', encoding='utf-8').read()
for m in re.finditer(r'new\("(?P<s>[a-z0-9\-]+)",\s*new\[\]\s*\{(?P<b>.*?)\n    \}(?P<tail>[^;]*)\);', src, re.S):
    steps = [(n, int(o)) for n, o in re.findall(r'new Step\("([^"]+)",\s*(\d+)\)', m.group('b'))]
    digest = '|'.join('%s:%d' % (n, o) for n, o in steps)
    print('        ["%s"] = "%s",' % (m.group('s'), digest))
