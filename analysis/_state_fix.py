import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
fixes = [
    ('| 测试（快，`Speed!=Slow`） | **1380 通过 / 0 失败 / 2 跳过** |', '| 测试（快，`Speed!=Slow`） | **1388 通过 / 0 失败 / 2 跳过** |'),
    ('| UI 类 | **92 个，37 个不可达** |', '| UI 类 | **94 个，36 个不可达** |'),
]
for old, new in fixes:
    n = t.count(old)
    print(('FOUND ' if n else 'MISS  ') + old[:44], '->', n)
    t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='').write(t)

# read back and show the header lines to prove the file is valid UTF-8
t2 = io.open(p, encoding='utf-8').read().splitlines()
for line in t2[:16]:
    print(line[:110])
