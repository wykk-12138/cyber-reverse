import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()

# dead anchor 1: the R155 round reworded the comment
old1 = '"find": "        if (SinkUrl is null) return;     // nothing to do, and nothing to lose\\n",'
new1 = '"find": "        if (SinkUrl is null) return;     // nothing to do on the request side, and nothing to lose\\n",'
assert old1 in t, 'round 127 anchor line not found'
t = t.replace(old1, new1, 1)

# dead anchor 2: PARITY.md's UI count moved from "77 个 UI 类：24 个" to "83 个 UI 类：26 个 … + 57 个"
old2 = '"find": "**77 个 UI 类：24 个'
i = t.find(old2)
assert i >= 0, 'round 164 anchor not found'
line_end = t.index('\n', i)
old_line = t[i:line_end]
new_line = old_line.replace('**77 个 UI 类：24 个', '**83 个 UI 类：26 个')
t = t[:i] + new_line + t[line_end:]
print('replaced:', old_line[:80])
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('two dead anchors repaired')
