import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 101 轮。", "最后更新：第 102 轮。"),
    ("**940 通过 / 0 失败 / 2 跳过**", "**945 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R101）。", "上一次跑：全 PASS（R102）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **Nike 的结账步骤不是 REST 子路径"
add = """- **三族端点已收（R102）**：`/rpc/ec/*`(7)、`/component/singlepagecheckout/*`(7)、
  `/apps/gatekeeper/api/*`(8) → `StoreApiFamilies`。
  **gatekeeper 是发布闸门不是购物车**：`bootstrap → interaction-challenge/create → render-token →
  gatekeeper-token → validate-gatekeeper-token → release-details`；跳过它的后果是像封号的 403。
  `audit-events/*` 是遥测（带 `?shop=`），**不能当闸门 gate**。
- **同一时间只能跑一个 `verify.ps1 -Full`。** R102 开头有两个同时跑（含 R93 遗留），
  互相抢 `testhost`，两次都卡死不返回；杀掉后单跑一次全绿。
- **Nike 的结账步骤不是 REST 子路径"""
if anchor in t and "三族端点已收（R102）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
