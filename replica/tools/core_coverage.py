"""Generate docs/CORE_COVERAGE.md -- the core coverage table completion criterion (f) asks for.

Why a generator rather than a document: R1030 established that an append-only list becomes a fossil, and the numbers in
any hand-written table drift from the tools that produce them. Everything below is read at run time from the source
tree and from tools/endpoint-provenance.py, so the file can be regenerated rather than trusted.

The criterion has two halves and they have different answers:

  * the replica side is computable -- every flow file, its override count, and whether its endpoints rest on evidence;
  * the original side is not -- R1040 probed three shapes for a store catalogue and found none, and the evidence points
    to the catalogue being served rather than embedded. That half is recorded as Unknown with what would settle it.

Run: python tools/core_coverage.py   (writes docs/CORE_COVERAGE.md)
"""

import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # replica/
FLOWS = os.path.join(ROOT, "src", "Cybersole.Stores", "Flows")
OUT = os.path.join(ROOT, "docs", "CORE_COVERAGE.md")

OVERRIDE = re.compile(r"public override (?:async )?(?:Task<StepOutcome>|string|IReadOnlyList<string>|bool)\s+(\w+)")
PLACEHOLDER = re.compile(r"endpoint unknown|not captured")


def flows():
    rows = []
    for name in sorted(os.listdir(FLOWS)):
        if not name.endswith(".cs"):
            continue
        path = os.path.join(FLOWS, name)
        text = io.open(path, encoding="utf-8", errors="replace").read()
        overrides = OVERRIDE.findall(text)
        if not overrides:
            continue
        placeholders = len(PLACEHOLDER.findall(text))
        rows.append({
            "file": name,
            "steps": len(overrides),
            "placeholders": placeholders,
            "lines": text.count("\n") + 1,
        })
    return rows


def provenance():
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "endpoint-provenance.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stdout + p.stderr
    numbers = {}
    for key, pattern in (
        ("constants", r"endpoint constants:\s*(\d+)"),
        ("verbatim", r"verbatim in pool:\s*(\d+)"),
        ("invented", r"invented:\s*(\d+)"),
        ("unresolved", r"unresolved:\s*(\d+)"),
        ("inline", r"inline URL/path literals:\s*(\d+)"),
        ("not_in_pool", r"not in pool:\s*(\d+)"),
        ("registered", r"registered in ledger:\s*(\d+)"),
        ("unknown", r"unknown \(invented and unregistered\):\s*(\d+)"),
    ):
        m = re.search(pattern, out)
        numbers[key] = m.group(1) if m else "?"
    numbers["exit"] = p.returncode
    return numbers


def main():
    rows = flows()
    prov = provenance()
    total_steps = sum(r["steps"] for r in rows)
    total_placeholders = sum(r["placeholders"] for r in rows)
    with_placeholders = [r for r in rows if r["placeholders"]]

    lines = []
    add = lines.append
    add("# 核心覆盖表（生成物 —— 不要手改）")
    add("")
    add("由 `python tools/core_coverage.py` 生成。完成判据 (f) 的两半：")
    add("**复刻件侧可算**，**原版站清单不可得**，后者按 (a) 的形态写 Unknown + 缺什么。")
    add("")
    add("## 一、复刻件侧（可复算）")
    add("")
    add("| 度量 | 值 | 命令 |")
    add("|---|---|---|")
    add("| flow 文件 | %d | `ls src/Cybersole.Stores/Flows/*Flow*.cs` |" % len(rows))
    add("| 覆写步骤总数 | %d | 本文件生成时统计 |" % total_steps)
    add("| 其中报告「端点为 Unknown」的 | %d | 同上（匹配 `endpoint unknown` / `not captured`） |" % total_placeholders)
    add("| 含报告的 flow | %d | 同上 |" % len(with_placeholders))
    add("| 端点常量 / 逐字在池 | %s / %s | `python tools/endpoint-provenance.py` |" % (prov["constants"], prov["verbatim"]))
    add("| 常量 invented / unresolved | %s / %s | 同上 |" % (prov["invented"], prov["unresolved"]))
    add("| inline 字面量 / 不在池 | %s / %s | 同上 |" % (prov["inline"], prov["not_in_pool"]))
    add("| inline 已登记 / 未登记 | %s / %s | 同上 |" % (prov["registered"], prov["unknown"]))
    add("| 端点门 exit | **%s** | 同上 |" % prov["exit"])
    add("")
    add("### 逐 flow")
    add("")
    add("| flow | 覆写步骤 | 报告 Unknown | 行数 |")
    add("|---|---|---|---|")
    for r in rows:
        add("| `%s` | %d | %d | %d |" % (r["file"], r["steps"], r["placeholders"], r["lines"]))
    add("")
    add("## 二、原版侧（不可得 —— Unknown + 缺什么）")
    add("")
    add("**问题**：原版支持哪些站？")
    add("")
    add("**结论**：**Unknown。**")
    add("")
    add("**已试并全空的取证路径**（R1040）：")
    add("")
    add("| 路径 | 查询 | 结果 |")
    add("|---|---|---|")
    add("| 反射元数据里的命名空间 | `str \"Stores\\.Flows\\.[A-Za-z0-9_]+\" --limit 600` | **0** |")
    add("| 类型名 | `str \"FarfetchFlow\"` | **0** |")
    add("| 任意 `*Flow` 类型 | `str \"[A-Za-z]+Flow,\"` | 1（TPL Dataflow 文档，无关） |")
    add("| 站名 + 步骤的数据行 | `str \"^[A-Za-z0-9 .&'-]+ Checkout$\"` | 34，其中站名 **4** 条 |")
    add("")
    add("**为什么可能是服务端下发**：复刻件有 %d 个 flow 文件，而二进制里没有对应数量的名字；"
        "镜像有 `api.cybersole.io` 与 `/connect/app`（R1032）。" % len(rows))
    add("")
    add("**缺什么**：`api.cybersole.io/connect/app` 的响应。取它需要**原版登录凭据** —— "
        "那是本工作允许停下等 YG 的两类事之一。")
    add("")
    add("**已得的替代证据**：`Farfetch` · `Farfetch Checkout` 在池里，且后者与 "
        "`Shopify Checkout` · `Kith EU Checkout` · `FUNKO CHECKOUT` 同列 —— 4 个站的**定制结账文案**。"
        "那不是完整清单，但它是**二进制侧对具体站的正面证据**。")
    add("")
    add("### 而 Nike 链上有一个**更具体**的未决问题")
    add("")
    add("镜像里有 `api.nike.com/buy/` 的 **7** 条实名 URL：`checkouts/v3` · `checkout_previews/v3` · "
        "`checkouts_jobs/v3` · `checkout_previews_jobs/v3` · `fulfillment_offerings_jobs/v2` · "
        "`partner_cart_preorder/v2` · `partner_cart_preorder_jobs/v2`。")
    add("")
    add("**所以「Nike 没有结账面」是错的** —— 而有的是**两个**候选资源。")
    add("")
    add("**未决的是**：哪一个承接 **shipping 写入**（`checkouts/v3` 还是 `checkout_previews/v3`）。")
    add("")
    add("**为什么不能靠名字猜**：R1013 换成 `checkouts/v3` 被 R1014 撤回，理由是「路由存在不解决"
        "哪个承接写入」；R48 的裁决「换一个猜测只是移动失败」就在 `NikeFlow.cs` 里那段代码上方。")
    add("")
    add("**什么不能解决它 —— 而这是我上一版写错的**：`xrefs` 对这个产物里的字符串池**完全无效**。")
    add("")
    add("| 检查 | 结果 |")
    add("|---|---|")
    add("| `xrefs_to 0x147053d8c`（checkouts/v3） | **0** |")
    add("| `xrefs_to 0x147053c94`（checkout_previews/v3） | **0** |")
    add("| 8 字节小端立即数搜索（`bin_search`） | **0**（x64 用 `lea rip+disp`，绝对地址不落盘） |")
    add("| **对照**：`datadome`（`0x146ffe1fc`） | **0** |")
    add("| **对照**：`queue-it`（`0x147147794`） | **0** |")
    add("")
    add("**→ 对照也全是 0 ⇒ 「没有 xref」是这个产物的**通性**，不是那两条 URL 的特别之处，"
        "所以它关于那两条什么也没说明。**")
    add("")
    add("**什么能解决它**：从**数据段**里找指向池的 `(ptr, len)` 表，或反编译**已知**调用 Nike buy 面的函数"
        "（例如已经记录过的 `NikeEndpoints` 那一族）并读它装配的字符串。"
        "**那是下一轮的工作，而且它比一次 `xrefs` 查询大。**")
    add("")
    add("## 三、风控清单（可复算）")
    add("")
    add("由 `VendorWiring.Rows` 与 `tests/Cybersole.Tests/VendorWiringTests.cs` 逐条钉住：")
    add("七行 × 九列（`Vendor` · `Marker` · `Cookie` · `State` · `Note` · `MarkerFrom` · `Gap` · `Solver` · `Relayed`）。")
    add("复算：`dotnet test --filter \"FullyQualifiedName~VendorWiring\"`。")
    add("")
    add("原版解**六**家（cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx）；")
    add("`Solving Incapsula` 为 **0**，是 imperva 的第三个独立证据（R1024）。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/CORE_COVERAGE.md")
    print("  flows=%d steps=%d placeholders=%d provenance exit=%s"
          % (len(rows), total_steps, total_placeholders, prov["exit"]))


if __name__ == "__main__":
    main()
