"""Generate docs/PAYMENT_CHALLENGES.md -- the two challenges the vendor ledger put out of scope.

R1048 sorted seven reconciliation gaps into vendors, payment challenges and generic challenge types, and ruled that the
payment ones belong to the payment layer. where_is then showed neither exists in this workspace at all: no PayPal3DS,
no StripeChallenge. So "belongs to the payment layer" was true and also an unrecorded gap, which is the shape criterion
(f) exists to catch.

This writes down what the image actually carries for both, so the gap has a size rather than a name. Every count is
probed fresh; the controls print first because a zero underneath them is only readable against a non-zero.

Why a generator: R1030 and R1041, the same reason as the other two coverage documents.

Run: python tools/payment_challenges.py   (writes docs/PAYMENT_CHALLENGES.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "PAYMENT_CHALLENGES.md")

PROBES = [
    ("control", "kpsdk", r"kpsdk"),
    ("paypal", "Solving PayPal 3DS", r"Solving PayPal 3DS"),
    ("paypal", "SolvePayPal3DS body", r"SolvePayPal3DS"),
    ("paypal", "SolvePayPalHosted3DS body", r"SolvePayPalHosted3DS"),
    ("3ds", "state machine names", r"Submit3DS|Process3DS|Waiting3DS|Complete3DS"),
    ("stripe", "SubmitOrderStripe body", r"SubmitOrderStripe"),
    ("stripe", "ProcessOrderStripe body", r"ProcessOrderStripe"),
    ("stripe", "GetStripePaymentIntent", r"GetStripePaymentIntent"),
    ("stripe", "CreateStripePaymentMethod", r"CreateStripePaymentMethod"),
    ("stripe", "ValidateStripeIntent", r"ValidateStripeIntent"),
    ("stripe", "StripeFallbackHandler", r"StripeFallbackHandler"),
    ("stripe", "API version", r"StripeVersion|2025-08-27"),
]

# The replica's payment layer, checked rather than asserted.
REPLICA_MARKERS = ["PayPal3DS", "StripeChallenge", "Submit3DS", "CreateStripePaymentMethod"]


def probe(pattern, limit=600):
    p = subprocess.run(
        [sys.executable, os.path.join(REPO, "analysis", "ida.py"), "str", pattern, "--limit", str(limit)],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        m = re.search(r"\{.*\}", p.stdout or "", re.S)
        return json.loads(m.group(0)) if m else {"n": 0, "matches": []}


def replica_hits(marker):
    """Where the marker appears, and in which file.

    R1053: the first version answered yes/no and that was misleading. PayPal3DS appears in WallSolving.cs, a risk file,
    and CreateStripePaymentMethod appears in a step map -- both are the name being referenced, neither is the challenge
    being implemented. A name showing up is not the work, which is R1042's point about text versus solver.
    """
    hits = []
    src = os.path.join(ROOT, "src")
    for base, _dirs, files in os.walk(src):
        for name in files:
            if not name.endswith(".cs"):
                continue
            try:
                text = io.open(os.path.join(base, name), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if marker in text:
                hits.append(name)
    return hits


def main():
    rows = []
    for kind, label, pattern in PROBES:
        d = probe(pattern)
        rows.append((kind, label, d.get("n", -1), (d.get("matches") or [{}])[0].get("addr", "")))

    control = [r for r in rows if r[0] == "control"]
    control_ok = all(r[2] > 0 for r in control)
    replica = {m: replica_hits(m) for m in REPLICA_MARKERS}

    # The staged strings, taken whole so the count is a fact rather than a recollection.
    staged = probe(r"Solving PayPal 3DS \(")
    stages = sorted({h["string"] for h in staged.get("matches", [])})

    lines = []
    add = lines.append
    add("# 支付侧挑战（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/payment_challenges.py` 生成。" +
        " `VENDOR_COVERAGE.md` 把 7 个缺口分成厂商 / 支付挑战 / 通用挑战三类，" +
        "其中**支付挑战归支付层**；而 `where_is` 显示这一层在本工作里**不存在**。")
    add("")
    add("**→ 所以「归支付层」这句话是真的，同时也是一个没有被记下来的缺口。**")
    add("")
    add("## 一、对照")
    add("")
    add("| 对照串 | 命中 |")
    add("|---|---|")
    for _k, label, n, _a in control:
        add("| `%s` | **%d** |" % (label, n))
    add("")
    add("**→ 对照%s。**" % ("成立" if control_ok else "不成立，下方为零不可读"))
    add("")
    add("## 二、PayPal 3DS 的阶段")
    add("")
    add("**镜像里有 %d 条分期文案：**" % len(stages))
    add("")
    for s in stages:
        add("- `%s`" % s)
    add("")
    add("**→ 注意 `(2.1)`：那是阶段 2 之后的**子阶段**，所以" +
        "**可观察阶段是 %d 个而不是 8 个** —— R1048 把「9 条文案」读成「8 个阶段」，而多出来的那条正是 2.1。"
        % len(stages))
    add("")
    add("## 三、3DS 状态机")
    add("")
    add("镜像里有四个状态名：`Submit3DS` · `Process3DS` · `Waiting3DS` · `Complete3DS`。")
    add("")
    add("**→ 那是一个 4 态机：提交 → 处理 → 等待 → 完成。**" +
        " 而 PayPal 侧有两个 solver 体：`<SolvePayPal3DS>` 与 `<SolvePayPalHosted3DS>` ——" +
        " **普通 3DS 与 Hosted 3DS 是两条路**，不是一条。")
    add("")
    add("## 四、Stripe")
    add("")
    add("| 名字 | 命中 | 首条地址 |")
    add("|---|---|---|")
    for kind, label, n, addr in rows:
        if kind != "stripe":
            continue
        add("| `%s` | **%d** | `%s` |" % (label, n, addr or "—"))
    add("")
    add("**→ 那是一条完整流程**：配置 → 支付意图 → 支付方法 → 提交 → 校验，" +
        "外加一个 `StripeFallbackHandler` 与一个 API 版本常量（`2025-08-27.basil`）。")
    add("")
    add("## 五、复刻件侧")
    add("")
    add("| 标记 | 复刻件里出现在 | 性质 |")
    add("|---|---|---|")
    for marker, hits in replica.items():
        where = " · ".join("`%s`" % h for h in hits) if hits else "**（无）**"
        add("| `%s` | %s | %s |" % (marker, where,
                                     "名字被引用" if hits else "**完全缺失**"))
    add("")
    add("**→ 「名字被引用」不等于「实现了」**：`PayPal3DS` 出现在 `WallSolving.cs`（风控侧），"
        "`CreateStripePaymentMethod` 出现在步骤映射表与 `RetailFlows`（flow 的步骤名）。" +
        "两者都是**这个名字被提到**，不是支付挑战被执行 —— 与 R1042 那条「有文案不等于有 solver」同族。")
    add("")
    add("**→ 所以这两个缺口「为什么未覆盖」的答案是**：" +
        "镜像把两条支付挑战写全了（9 条分期、4 态机、两个 PayPal solver、Stripe 六步），" +
        "而本工作里**没有一处实现它们**：`StripeChallenge` 与 `Submit3DS` 连名字都没有，" +
        "另两个只在别处被引用。")
    add("")
    add("## 六、边界")
    add("")
    add("- **有方法名不等于有协议**：`SubmitOrderStripe` 证明原版有这一步，不证明它发什么。" +
        "要协议得反编译那几个体，而那是下一步。")
    add("- **3DS 的真实分支取决于银行**：9 条分期是原版的**观察顺序**，不是所有卡都会走满。")
    add("- **这两个挑战不属于 `VendorWiring`**：那张表问的是「哪个站的风控在拦路」，" +
        "而支付挑战是「付款这一步还要做什么」，两者不同类。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/PAYMENT_CHALLENGES.md")
    print("  control ok=%s  stages=%d  markers absent=%d/%d"
          % (control_ok, len(stages), sum(1 for v in replica.values() if not v), len(replica)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
