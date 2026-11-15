import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\VERDICT.md"
t = io.open(p, encoding="utf-8").read()

# The blanket 61 -> 62 replace missed these two phrasings.
pairs = [
    ("| 注册模块 | **61**（32 种 flow） |", "| 注册模块 | **62**（32 种 flow） |"),
    ("每步都真做事 | 61 模块 · 平台", "每步都真做事 | 62 模块 · 平台"),
    ("| 每个函数功能相等 | 61 模块 · 47", "| 每个函数功能相等 | 62 模块 · 47"),
]

for old, new in pairs:
    if old in t:
        t = t.replace(old, new, 1)
        print("fixed:", old[:40])
    else:
        print("miss:", old[:40])

io.open(p, "w", encoding="utf-8", newline="").write(t)
