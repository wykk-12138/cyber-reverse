"""Find the `65 个模块` claim the module-count guard is pointing at, with surrounding context.

Written because quoting a backtick fenced block through PowerShell's argument passing keeps mangling the
regex -- the shell eats the escapes before Python ever sees them. A file has no such problem.
"""
import io
import re

PATH = 'replica/docs/VERDICT.md'
text = io.open(PATH, encoding='utf-8').read()
body = re.sub(r'```.*?```', '\n', text, flags=re.S)

pattern = re.compile(r'65\s*\u4e2a\u6a21\u5757')
for m in pattern.finditer(body):
    start = max(0, m.start() - 200)
    window = body[start:m.end() + 80]
    print('--- at %d' % m.start())
    print(window.encode('unicode_escape').decode('ascii'))
