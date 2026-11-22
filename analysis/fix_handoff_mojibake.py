"""Repair the two U+FFFD characters my PowerShell heredoc introduced into docs/HANDOFF.md.

The scan caught them; the rule (AGENTS §2.5) is that a document must not carry mojibake, so this replaces the damaged
line with the text it was meant to be. The replacement is written from a Python literal, not from a shell heredoc, which
is what mangled it in the first place.
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PATH = 'docs/HANDOFF.md'
text = io.open(PATH, encoding='utf-8').read()

damaged = [line for line in text.splitlines() if '\ufffd' in line]
print('damaged lines: %d' % len(damaged))
for line in damaged:
    print('  before: %r' % line[:60])

fixed = text
for line in damaged:
    if line.lstrip().startswith('- **\u6b8b'):
        replacement = '- **\u6b8b\u4f59**\uff1a\u2460 267 \u4e2a\u5f02\u6b65\u540d\u9700\u6309\u5730\u5740\u9010\u6761\u53cd\u7f16\u8bd1' \
                      '\uff08\u72ec\u7acb\u961f\u5217\uff0c\u4e0d\u5728\u53d6\u4ef6\u5224\u636e\u5185\uff09' \
                      '\uff1b\u2461\u4f1a\u8bdd\u503c\u7c7b\u8f93\u5165\uff08euat / metadata id / token\uff09\u3002'
    else:
        replacement = re.sub('[\ufffd]+', '', line)
    fixed = fixed.replace(line, replacement, 1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(fixed)

remaining = [line for line in io.open(PATH, encoding='utf-8').read().splitlines() if '\ufffd' in line]
print('after repair, damaged lines: %d' % len(remaining))
