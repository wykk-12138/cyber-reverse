import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 92 轮。", "最后更新：第 93 轮。"),
    ("上一次跑：全 PASS（R92）。", "上一次跑：全 PASS（R93）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **店铺名以「类型名"
add = """- **IDA 数据库现在是「无」——R93 崩了一次，Repair 把 `.id0/.id1/.id2`（约 1.6 GB）删了。**
  反编译这一路归零，重建要重新自动分析 123 MB 的 NativeAOT（小时级）。
  **没有事实损失**：`NikeEndpoints` / `NikeHeaders` / `NikeFlow.Countries` / `IDB_EVIDENCE.md` /
  `NIKE_PARITY.md` / `original_view_classes.txt` 就是全部证据，二进制打不开也一样在。
- **大查询会杀死取证工具。** R93 用 `find_regex "Mozilla/5\\.0" limit=400`（每条几 KB）把 IDA 插件带崩。
  以后一律 `limit ≤ 60` + 窄模式，**取完立刻备份 `.i64`**。
- **目标会自动升版。** R93 打开时 `FileVersion` 已是 **5.18.32**（原 5.18.30），
  `AppVersionTests.VersionMatchesTheOriginalBinary` 自己响了 —— 那正是 R74 加它的理由。
  已全仓 42 文件 82 处改成 5.18.32。**「1:1」永远带一个定语：对哪个版本。**
- **店铺名以「类型名"""
if anchor in t and "IDA 数据库现在是「无」" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
