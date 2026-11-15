import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 98 轮。", "最后更新：第 99 轮。"),
    ("**923 通过 / 0 失败 / 2 跳过**", "**930 通过 / 0 失败 / 2 跳过**"),
    ("上一次跑：全 PASS（R98）。", "上一次跑：全 PASS（R99）。"),
]

for old, new in subs:
    if old not in t:
        print("skip:", old[:30])
        continue
    t = t.replace(old, new, 1)

anchor = "- **`StepOutcome` 是 struct**"
add = """- **抽签链路（R99）**：镜像有 `/pages/raffle`、`<script id="panagora-raffle-data"[^>]*>(.*?)</script>`
  （逐字提取器）、`.raffle-data[data-id]`、`/api/raffle-sig`、`SaleRegistration-Config` /
  `-SignupSubmit`、`Cart-CartDrawBody`、`Already Entered Draw`。
  已落成 `DemandwareRaffle` + `DemandwareFlow.EnterRaffleAsync`。
  **关键分支：页面没有抽签数据 → `raffle=absent` 且返回成功** ——
  「没有这个功能」不等于「这个功能失败了」，否则不办抽签的店连普通结账都会挂。
- **`StepOutcome` 是 struct**"""
if anchor in t and "抽签链路（R99）" not in t:
    t = t.replace(anchor, add, 1)
    print("traps added")
else:
    print("anchor missing or present")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE saved")
