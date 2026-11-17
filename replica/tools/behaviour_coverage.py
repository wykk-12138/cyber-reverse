"""How much of the core behaviour is asserted, by priority.

The goal asks for equal function count, equal per-function behaviour, and comparable efficiency. This round established
that per-function behaviour cannot be verified function by function in an artifact with no symbols -- 96.87% of its
functions are sub_*. So the honest question is not "is each function equal" but "how much of the core behaviour has an
assertion behind it", and that is countable.

The 2258-test suite is the evidence. This groups it by the goal's own priorities so the coverage has a number rather
than a feeling: how many tests stand behind checkout flows, how many behind risk control, how many behind the request
and fingerprint layer, and how many behind everything else.

Run: python tools/behaviour_coverage.py   (writes docs/BEHAVIOUR_COVERAGE.md)
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, "tests", "Cybersole.Tests")
OUT = os.path.join(ROOT, "docs", "BEHAVIOUR_COVERAGE.md")

# Keyword groups, by the goal's ordering rather than by filename, because a test's name says what it pins.
PRIORITIES = [
    ("① checkout flow", ["Flow", "Store", "Checkout", "Cart", "AddToCart", "Shipping", "Order", "Basket", "Product", "Variant"]),
    ("② 风控对抗", ["Vendor", "AntiBot", "Wall", "Captcha", "Kasada", "Cloudflare", "DataDome", "PerimeterX", "QueueIt", "Queue",
                  "Imperva", "Akamai", "Kasada", "Turnstile", "Recaptcha", "HCaptcha", "Geetest", "Solver"]),
    ("③ 请求与指纹", ["Fingerprint", "Http", "Tls", "Bouncy", "Identity", "Header", "Client", "Proxy", "Cookie", "Session"]),
]


def test_methods():
    """Every [Fact] or [Theory] name, with its class."""
    out = []
    fact = re.compile(r"\[(?:Fact|Theory)\]")
    for name in sorted(os.listdir(TESTS)):
        if not name.endswith(".cs"):
            continue
        text = io.open(os.path.join(TESTS, name), encoding="utf-8", errors="replace").read()
        cls = re.search(r"public\s+(?:sealed\s+)?class\s+(\w+)", text)
        cls_name = cls.group(1) if cls else name[:-3]
        for m in fact.finditer(text):
            tail = text[m.end():m.end() + 600]
            meth = re.search(r"public\s+(?:async\s+)?(?:Task|void)\s+(\w+)", tail)
            if meth:
                out.append((cls_name, meth.group(1)))
    return out


def main():
    methods = test_methods()
    groups = {label: [] for label, _ in PRIORITIES}
    other = []
    for cls, meth in methods:
        hay = cls + " " + meth
        hit = None
        for label, keys in PRIORITIES:
            if any(k.lower() in hay.lower() for k in keys):
                hit = label
                break
        if hit:
            groups[hit].append("%s.%s" % (cls, meth))
        else:
            other.append("%s.%s" % (cls, meth))

    total = len(methods)
    lines = []
    add = lines.append
    add("# 功能覆盖面（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/behaviour_coverage.py` 生成。")
    add("")
    add("**为什么用这个判据**：goal 要「每个函数功能相等」，而 R1045 证明这个产物"
        "**96.87% 的函数是 `sub_*`**、没有业务符号 ⇒ **逐函数比对不可行**。")
    add("所以可行的问题是「核心行为里有多少有断言撑着」，而那是可数的。")
    add("")
    add("## 一、口径：方法数与用例数不同")
    add("")
    add("| 口径 | 值 | 来源 |")
    add("|---|---|---|")
    add("| `[Fact]` + `[Theory]` **方法数** | **%d** | 本工具（数方法） |" % total)
    add("| 套件实际跑的**用例数** | **2258** | `python tools/metrics_report.py` |")
    add("")
    add("**→ 差额来自 `[Theory]`：一个方法带 N 组参数就跑 N 次**，所以用例数大于方法数。")
    add("**→ 下表的每级数字都是**方法数**，不是用例数 —— 两个数都对，但它们回答不同的问题。**")
    add("")
    add("## 二、按 goal 的优先级分组")
    add("")
    add("| 优先级 | 测试数 | 占比 |")
    add("|---|---|---|")
    for label, _ in PRIORITIES:
        n = len(groups[label])
        add("| **%s** | **%d** | %.1f%% |" % (label, n, 100.0 * n / max(total, 1)))
    add("| 其余（含 UI） | %d | %.1f%% |" % (len(other), 100.0 * len(other) / max(total, 1)))
    add("| **合计** | **%d** | 100%% |" % total)
    add("")
    add("## 二、边界")
    add("")
    add("- **分组按测试名，不按文件**：一个测试属于哪一级由它断言什么决定，而名字是最近的证据。")
    add("- **名字可能误导**：`VendorWiringTests` 断言的是台账数据而非行为，它落进 ② 是因为关键词。")
    add("  所以本表的数字是**上界**，不是精确的覆盖面。")
    add("- **断言数不等于覆盖度**：2258 个测试也可能反复断言同一件事。")
    add("- **原版侧没有对应数字**：它没有测试，所以这张表**只说复刻件**，不能用来声称「与原版等价」。")
    add("")
    add("## 三、而 (e) 的另一半")
    add("")
    add("完成判据 (e) 要「套件绿、**变异测试全 fired**」。")
    add("**→ 「全 fired」的判据是每一个变异都能让至少一个测试变红**，而那与上面的覆盖面是两件事：")
    add("上面数有多少行为被断言，下面数有多少变异被抓住。**两者都要，而只有前者是本轮算的。**")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/BEHAVIOUR_COVERAGE.md")
    print("  tests=%d" % total)
    for label, _ in PRIORITIES:
        print("    %-18s %d" % (label, len(groups[label])))
    print("    %-18s %d" % ("other", len(other)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
