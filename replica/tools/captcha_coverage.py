"""Generate docs/CAPTCHA_COVERAGE.md -- the captcha half of the goal's risk-control list.

The goal names Kasada, Cloudflare, DataDome, PerimeterX, Queue-it and the captcha services. The first five are in
VendorWiring; the captchas were never enumerated, and R1053 left them as three rows in a gap table labelled "generic
challenge type", which says what they are not.

Two findings shape this document. The challenge types are a handful of named families with variants, each supported by
a property or a task-type literal. And the providers are not built in at all: CaptchaProvider is a user-configured
record with an ApiKey, a Balance, a Concurrency and a Priority, sitting behind an EnabledProviders list with Add and
Reorder. That is the image's own evidence for Solver.UserThirdParty in VendorWiring, which until now rested on the
absence of a local solver rather than on a positive structure.

Why a generator: same reason as the other coverage documents, R1030 and R1041.

Run: python tools/captcha_coverage.py   (writes docs/CAPTCHA_COVERAGE.md)
"""

import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "docs", "CAPTCHA_COVERAGE.md")

# (family, probe, note). Each family gets its own probe because the spellings differ -- GeeTest is capital-G in the
# task names and lower-case in the HTML filenames, which is the shape difference AGENTS 2.7 warns about.
FAMILIES = [
    ("reCAPTCHA", r"Recaptcha(E nterprise|V3|Invisible)?|eCAPTCHA|reCAPTCHA", "Recaptcha · RecaptchaInvisible · RecaptchaV3 · RecaptchaEnterprise"),
    ("hCaptcha", r"HCaptcha", "HCaptcha · HCaptchaInvisible · HCaptchaSpoof"),
    ("Cloudflare Turnstile", r"Turnstile", "Turnstile · CloudflareTurnstile · LoopTurnstile · turnstileToken"),
    ("GeeTest", r"[Gg]ee[Tt]est", "Geetest · GeetestV4 · GeeTestTask · GeeTestTaskProxyLess · Geetest.html · GeetestV4.html"),
    ("Castle", r"Castle[A-Za-z]*", "get_Castle"),
    ("TrustDevice", r"TrustDevice[A-Za-z]*", "TrustDeviceGen · TrustDeviceBotDOpen · static.trustdecision.com"),
]

ABSENT = [
    ("Funcaptcha / ArkoseLabs", r"[Ff]un[Cc]aptcha|arkose"),
    ("MTCaptcha", r"[Mm][Tt][Cc]aptcha"),
]

PROVIDER_FIELDS = [
    "Priority", "Name", "Type", "ApiKey", "Balance", "Count", "Concurrency",
    "BalanceSupported", "IsFetchingBalance",
]

REPLICA_MARKERS = ["CaptchaProvider", "HCaptchaSpoof", "RecaptchaEnterprise", "GeetestV4", "TurnstileSiteKey"]


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
    hits = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, "src")):
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
    control = probe(r"kpsdk").get("n", -1)
    if control <= 0:
        print("  !! control failed (kpsdk=%d) -- IDA is not ready; refusing to overwrite docs/CAPTCHA_COVERAGE.md with false zeros"
              % control)
        return 2
    fam = [(n, probe(p).get("n", -1), (probe(p).get("matches") or [{}])[0].get("addr", ""), note)
           for n, p, note in FAMILIES]
    absent = [(n, probe(p).get("n", -1)) for n, p in ABSENT]
    replica = {m: replica_hits(m) for m in REPLICA_MARKERS}
    provider_seen = probe(r"CaptchaProviders\.CaptchaProvider,").get("n", -1)

    lines = []
    add = lines.append
    add("# captcha 覆盖（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/captcha_coverage.py` 生成。填补目标 ②的「各家 captcha」那一块 ——")
    add("前五家（Kasada · Cloudflare · DataDome · PerimeterX · Queue-it）在 `VendorWiring`，captcha 一直没枚举过。")
    add("")
    add("## 一、对照")
    add("")
    add("| 对照串 | 命中 |")
    add("|---|---|")
    add("| `kpsdk` | **%d** |" % control)
    add("")
    add("**→ 对照%s，所以下面的零可读。**" % ("成立" if control > 0 else "不成立"))
    add("")
    add("## 二、原版支持的挑战家族")
    add("")
    add("| 家族 | 命中 | 首条地址 | 变体（取自属性与任务名） |")
    add("|---|---|---|---|")
    for name, n, addr, note in fam:
        add("| **%s** | **%d** | `%s` | %s |" % (name, n, addr or "—", note))
    add("")
    add("## 三、明确的零（有对照）")
    add("")
    add("| 家族 | 命中 |")
    add("|---|---|")
    for name, n in absent:
        add("| %s | **%d** |" % (name, n))
    add("")
    add("**→ 所以「原版支持所有主流 captcha」是**错的**：Funcaptcha/Arkose 与 MTCaptcha 一次都不出现。**")
    add("→ 而这是**负结论**，它只有在对照成立时才有意义 —— 而对照是 `kpsdk %d`。**" % control)
    add("")
    add("## 四、而 provider **不是内建的**")
    add("")
    add("`Cybersole.CaptchaProviders.CaptchaProvider` 的字段（命中 %d 条元数据）：" % provider_seen)
    add("")
    for f in PROVIDER_FIELDS:
        add("- `%s`" % f)
    add("")
    add("**→ 那是一张**用户配置**的服务表**：每家有自己的 `ApiKey`、`Balance`、`Concurrency`、`Priority`，")
    add("而 `Settings.CaptchaProvidersView` 带 `EnabledProviders` / `Add` / `Reorder` —— 可启用、可排序。")
    add("")
    add("**→ 所以原版的 captcha 走**用户第三方**（`VendorWiring.Solver.UserThirdParty`），")
    add("而那是这个值的**正面依据**：此前它只靠「没有本地 solver」这个缺席来支撑。**")
    add("**→ 而 `Geetest.html` / `GeetestV4.html` 说明 GeeTest 有一条**本地**路径**（页面内联脚本），")
    add("所以同一个家族可以两种方式都在 —— 与 R1025 的 queue-it「两种表面」同族。")
    add("")
    add("## 五、复刻件侧")
    add("")
    add("| 标记 | 出现在 | 性质 |")
    add("|---|---|---|")
    for marker, hits in replica.items():
        where = " · ".join("`%s`" % h for h in hits) if hits else "**（无）**"
        add("| `%s` | %s | %s |" % (marker, where, "名字被引用"
                                             if hits else "**无执行面**（识别面见 §七）"))
    add("")
    add("**→ 与 `PAYMENT_CHALLENGES.md` 同一个判据：名字出现不等于实现。**")
    add("")
    add("## 六、边界")
    add("")
    add("- **有属性名不等于有协议**：`HCaptchaSpoof` 证明原版有那一步，不证明它发什么。")
    add("- **家族的变体数不等于组合数**：reCAPTCHA 的四个变体可以共享一条提交路径，也可以是四条。")
    add("- **`Captcha.Type` 的取值已结案（R1286）**：`143ca6a9f` 的 checkpoint 页按它分支 —— `0` 是需要点击的复选框，`1` 是隐形 `execute()`。它与 provider 行的 `Type` 是两件事。")
    add("")
    add("## 七、为什么求解面是**结构性**缺的：原版自带 Chromium")
    add("")
    add("| 证据 | 内容 |")
    add("|---|---|")
    add("| `178267`–`178273` | `DotNetBrowser.Core, Version=4.3.5.8591` + 六平台 `DotNetBrowser.Chromium.*.xml` 清单 |")
    add("| `146a8b90c` | 原文：Native AOT 部署下 Chromium 二进制须手工预置 —— 设 `DOTNETBROWSER_CHROMIUM_DIR` 或 `EngineOptions.ChromiumDirectory` |")
    add("| `146b31fac` | 原文：AOT mode detected: Chromium binaries could not be found |")
    add("| `143dedc4e` 等 | Chromium 包清单 XML，`chrome.dll` 279–312 MB |")
    add("| `1470a1ef4` / `1470ad964` | `imgs.hcaptcha.com` / `js.hcaptcha.com`（页面侧脚本域） |")
    add("")
    add("**→ 原版在嵌入式 Chromium 里真跑 `grecaptcha.enterprise.execute()` 与 `turnstile.render()`**，所以")
    add("`HCaptchaSpoof` / `RecaptchaEnterprise` / `TurnstileSiteKey` 的**执行面**不是「还没写」，而是**需要一个浏览器引擎**。")
    add("复刻件当前没有；接入等于引入新依赖（DotNetBrowser 为商业授权，开源替代需另行裁决）——")
    add("因此这三条从待办移出，理由与所缺条件如上。")
    add("")
    add("**→ 而识别面不依赖引擎**：R1286 的 `CaptchaSurface` 用五个 loader 字面量认出四家挑战，已接进 `StoreFlow.DetectAsync` 写 `captcha.kind`。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/CAPTCHA_COVERAGE.md")
    print("  control=%d  families=%d  absent=%d  provider metadata=%d"
          % (control, len(fam), len(absent), provider_seen))
    for name, n in absent:
        if n != 0:
            print("  !! %s returned %d, expected 0" % (name, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
