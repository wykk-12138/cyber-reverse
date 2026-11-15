import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

old = """- **`NikeKasadaFlowTests.TheFlowProducesARealToken…` 在 `-Full` 里会挂、单跑必过**
  （两轮验证同一条；单跑 3/3 通过 15 s）。它是实时 Kasada 取脚本测试，慢测并行阶段超时。
  **不要把它当成回归**；判断法：单跑 + 看是否只有这一条。"""

new = """- **`-Full` 的 slow 阶段会挂一条实时测试，而且每次挂的不一样（R103/R105/R107 实测）。**
  见过的：`NikeKasadaFlowTests.TheFlowProducesARealToken…`、
  `NonParityClaimsTests.TheSecureTokenRotates…`、`NonParityClaimsTests.TheVendorHostStillAnswers…`、
  `KasadaHeaderSurfaceTests`、`OwnTlsFallbackTests`、`AnalyticsAndModalTests`。
  **每一条单跑都过**（Kasada 那组 3/3、15 s）。判断法：
  ① 单跑该条；② 重跑 `-Full` 看是否换了另一条；③ 换人不换 → 是本机实时网络抖动，不是回归。"""

if old not in t:
    raise SystemExit("anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("rotating-flake note updated")
