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
REPLICA_MARKERS = ["PayPal3DS", "PayPalThreeDs", "StripeChallenge", "Submit3DS", "CreateStripePaymentMethod"]


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
    if not control_ok:
        print("  !! controls failed (%s) -- IDA is not ready; refusing to overwrite docs/PAYMENT_CHALLENGES.md with false zeros"
              % ", ".join("%s=%d" % (label, n) for _, label, n, _ in control))
        return 2
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
    add("**→ R1078 反编译落地了阶段 1（两条路）**：目标是冻结字面量 **`https://www.paypal.com/graphql/`**" +
        "（0x147097e78，send 步 `sub_14110D670` 以 `sub_1408B6310` 的 +24 槽 = **PUT** 发送）；" +
        "头墙是 PayPal 自己的 web 客户端指纹 —— `x-app-name: checkoutuinodeweb_hermione`（0x146fc7338）、" +
        "`x-paypal-internal-euat`、`paypal-client-metadata-id`、`sec-fetch-site/mode/dest = same-origin/cors/empty`、" +
        " `origin/referer = https://www.paypal.com`；Hosted 方言另带 `x-requested-with: fetch`、`x-locale: en_US`、" +
        " `x-country`、`priority: u=1, i` 且 x-app-name/referer 取自上下文。预算 30 秒（+236=30000），" +
        "注册 white/StatusInfo 墙，状态分发 **200 → 成功续体，403 与 429 → 共享重试闭包**。" +
        "状态文案按 ctx+144 布尔选 `Solving PayPal 3DS (1)` 或 `Proccesing 3D Secure`（原版拼写保留；" +
        "R1081 更正：阶段 1 字面量带 `(1)` 后缀，此前文档速记把它丢了）。")
    add("")
    add("**→ 九个阶段的构建器已全数解码（R1081/R1082）**：每阶段与阶段 1 **同一请求模板**"
        "（同头墙方言/同 30 秒预算/同 200→成功续体 + 403/429→共享重试分发），仅进度串、续体槽与载荷不同。"
        "标签对象与池清单逐一吻合：(1) `sub_141102970`/`sub_141105A80`（续体 a1[4]/a1[9]）；"
        "(2) `sub_141103410` + hosted 孪生 `sub_141107DA0`/`sub_141108170`（a1[7]，B 变体带 per-context "
        "origin/referer 覆写）；(2.1) `sub_141103800`（a1[8]）；(3) `sub_141103BF0`（全局闭包 "
        "qword_1472C7328+120）；(4) `sub_1411090C0`（a1+80）；(5) `sub_141109550`（a1+88）；"
        "(6) `sub_141109910`（a1[12]，origin/referer 按上下文拼接）；(7) `sub_14110A080`（a1+104）；"
        "(8) `sub_141106360`（a1[11]）。**阶段 4–8 走 hosted 方言**。")
    add("")
    add("**→ R1083：载荷层也解了——graphql 操作是冻结字面量**（0x1470cc8cc..0x14712190c 的 "
        "threeDomainSecure 家族）：`ApproveOnboardPaymentMutation` · `CurrencyConversion` · "
        "`OnboardGuestMutation`（带 `is3DSecureRequired` 旗标）· `approveMemberPayment` ×2 · "
        "`PayWithQuery` · **`ResolveThreeDsContingency` ×2（解析操作：token/authId/referenceId/"
        "creditCardId/status/experiences 六变量）**。变体 B（0x1470dc9bc）由 **hosted solver "
        "`sub_141113680` 自己组装**——即 R1078 定位的 15,615 B / 11-case 状态机；变体 A"
        "（0x1470d7974）由普通 solver `sub_14110FDB0`（14,458 B）组装。九个可观察阶段 = 该机驱动"
        " `ResolveThreeDsContingency` 的解析环。**剩余未知 = 每 case 的变量绑定**"
        "（哪个 case 设哪个 authId/referenceId/status）——两台 solver 的 case 体是下一探针。")
    add("")
    add("**→ R1084：绑定源也定了位**——解析器变量从两路读入：**JSON 针**（冻结串 `\"referenceId\":\"` "
        "0x146a76254 ← 解析器 `sub_140940820`（335 B）/`sub_140D91B40`（308 B））与**挑战页 DOM**"
        "（选择器 `input[id='referenceId']` 0x1470a48dc ← `sub_14092F630`（557 B）——挑战页隐藏域，"
        "不只是响应 JSON）。响应键 `authId`（0x143446208）、`creditCardId`（0x146fd8f54）同为裸键"
        "字面量。剩余未知收窄为**每 case 用哪条源**——即两台 solver 的 switch case 体。")
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
    add("**→ R1080：挑战确认步已解码落地**：`Solving Stripe challenge`（0x146e94270）唯一引用者"
        " `sub_140BE31F0` 是**橙色墙** + hCaptcha 供词的确认机 —— 状态文案 `Submit billing`（0x146E9FFB8）、"
        "墙色 `orange`（0x1471099B0）、等待标签 `Waiting for captcha`（0x146F25E60）、失败文案"
        " `Stripe challenge captcha failed` + UI 色 `#FB4961`（0x146E9F310/0x146A76FD0）；表单五字段："
        "`challenge_response_token`（验证码令牌）、`challenge_response_ekey`=\"\"（空串哨兵）、"
        "`client_secret`（ctx728）、`captcha_vendor_name`=`hcaptcha`（0x147045DF0）、`key`（ctx704，"
        "可发布密钥）→ **PUT `https://api.stripe.com`（0x147054DD8）+ ctx800 的逐单路径**（+24 槽）。"
        "已落地为 `Payments/StripeChallenge.cs` 并由 `StripeChallengeTests` 钉住。")
    add("")
    add("**→ 而「六步流程」的名字（`SubmitOrderStripe` 等六条）仍只是名字**：它们的方法体尚未按 "
        "`chars_va - 12` 链解码；挑战确认是六步中第一块落地的可执行协议。")
    add("")
    add("**→ R1078/R1080 后复刻件侧分半**：PayPal 阶段 1 + Stripe 挑战确认均已落地"
        "（`PayPalThreeDs.cs` / `StripeChallenge.cs`，判据 e 变异各配可杀锚）；PayPal 阶段 2–8 与 "
        "Stripe 六步的其余步骤体已定位、每条一记反编译即可结案。")
    add("")
    add("## 六、边界")
    add("")
    add("- **有方法名不等于有协议，但入口函数已可直接反编译**：`SubmitOrderStripe` 等名字只证明原版有这一步；" +
        "在 NativeAOT 里取协议须按冻结字符串头 `obj_va = chars_va - 12` 查引用（`disp32_scan_any.py` → `site_to_func.py` → Hex-Rays + `names_at.py`）。" +
        "已核实入口：`Solving PayPal 3DS`（`0x146e93fb4 - 12 = 0x146e93fa8`）→ `sub_141102970`（927 B）/ `sub_141105A80`（1,047 B）；" +
        "`Solving Stripe challenge`（`0x146e9427c - 12 = 0x146e94270`）→ `sub_140BE31F0`（1,017 B）。")
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
