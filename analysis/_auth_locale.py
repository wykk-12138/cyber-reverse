import io, re, json
raw = io.open(r'D:\projects\cyber-reverse\replica\src\Cybersole.Core\Locales\Cybersole.Locales.en.json', encoding='utf-8').read()
pairs = re.findall(r'"(Auth\.[A-Za-z0-9_.]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
for k, v in pairs:
    print('%-38s %s' % (k, v))
