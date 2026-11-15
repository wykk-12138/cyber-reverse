import io, re
src = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\ErrorCatalog.cs', encoding='utf-8').read()
for m in re.finditer(r'new Entry\("([^"]+)",\s*"([^"]+)",\s*"((?:[^"\\]|\\.)*)"', src):
    print('        "%s",' % m.group(3).replace('\\"', '\\"'))
