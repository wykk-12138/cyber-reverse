import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 94 轮。", "最后更新：第 95 轮。"),
    ("**910 通过 / 0 失败 / 2 跳过**", "**912 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R94）。", "上一次跑：全 PASS（R95）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **端口通了不等于能查。**"
add = """- **「字符串存在性」查得到，「谁引用了它」查不到 —— 这是死路，别再试。**
  R95 在新建的 5.18.32 库上确认三条全空：`xrefs_to <字符串地址>` = 0；
  `find type=immediate/imm/refs/ref/data` = 0；`insn_query` 找 `lea` 引用 = 扫 20 万条 0 命中
  （要整数操作数，且默认只扫 20 万条，全 `.text` 是 200 万级）。
  NativeAOT 用偏移表 + RIP 相对寻址，IDA 看不到这层关系。**要拿引用关系只能靠 PDB 或动态调试。**
- **`insn_query` 真实 schema**：`{queries:[{mnem/op0/op1/op2/op_any(整数)/func/segment/start/end/count}]}`，
  **必须带 scope**（`segment` 或 `start`+`end` 或 `func`），否则报 `Scope required`。
- **数据库运行中无法备份**：IDA 独占 `.id0/.id1`，`Copy-Item` 报「正由另一进程使用」。
  备份只能在 IDA 里打包或关闭后复制。
- **端口通了不等于能查。**"""
if anchor in t and "谁引用了它" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
