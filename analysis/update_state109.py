import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 108 轮。", "最后更新：第 109 轮。"),
    ("**972 通过 / 0 失败 / 2 跳过**", "**976 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：`verify.ps1`（非 Full）全绿；`-Full` 未跑完（R108，见下）。",
     "上一次跑：单元测试 976 全绿；`verify.ps1` 未跑完（R109，本机长命令被杀，见下）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:36])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`-Full` 的 slow 阶段现在会「重试整组一次」**"
add = """- **slow 阶段已拆成两条检查（R109）**：`Speed=Slow&FullyQualifiedName!~Kasada`
  与 `Speed=Slow&FullyQualifiedName~Kasada`。Kasada 实时组要下载并求值真实脚本，
  比其余实时测试慢一个数量级，**它一挂会挡住其它所有实时结果**。
- **单元测试跑法 `-v m` → `-v q`（R109）**：`-v m` 下输出捕获会把测试进程弄成
  `StackOverflowException`，同一过滤器 `-v q` 976 通过 / 7 秒。
- **截到最后一个 `}` 改文件会误删后面的内容（R109 补回 R108 删掉的两条测试）。**
  改测试文件优先用锚点插入，不要用 rfind 截断。
- **`-Full` 的 slow 阶段现在会「重试整组一次」**"""
if anchor in t and "slow 阶段已拆成两条检查（R109）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
