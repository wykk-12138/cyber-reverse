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


def wiring_row_count():
    w = os.path.join(ROOT, "src", "Cybersole.Stores", "Scripts", "VendorWiring.cs")
    text = io.open(w, encoding="utf-8", errors="replace").read()
    return text.count("new Row(")


def main():
    rows = flows()
    prov = provenance()
    wiring_n = wiring_row_count()
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
    add("**更正 R1044/R1045 的误判（该项可取证，非不可得）**：")
    add("")
    add("R1044 曾对 `0x147053d8c`（`checkouts/v3`）与 `0x147053c94`（`checkout_previews/v3`）直接查 `xrefs_to` 得 `0`，")
    add("并据此误判为「字符串无 xref，只剩全盘数据流工程，记为不可得」。")
    add("**错因是漏了 NativeAOT 冻结字符串对象头偏移（R702 早已验证）**：")
    add("冻结 `System.String` 布局为 `[MethodTable*: 8B][Length: 4B][UTF-16 chars...]`；")
    add("`ida.py str` 返回的是字符首地址 `chars_va`，而 `.text` 中 `lea reg, [rip+disp32]` 指向的是对象头 **`obj_va = chars_va - 12`（`-0x0C`）**。")
    add("")
    add("对 `chars_va - 12` 实测（可复算命令：`python analysis/disp32_scan_any.py 0x147053d80 0x147053c88` → `python analysis/site_to_func.py 0x140B26A5E 0x140B1EDB1`）：")
    add("")
    add("| URL 串 | `chars_va` | 对象头 `obj_va`（`-12`） | `.text` 引用点 | 所属业务函数（`.pdata`） |")
    add("|---|---|---|---|---|")
    add("| `checkouts/v3/` | `0x147053d8c` | `0x147053d80` | `0x140B26A5E` | **`sub_140B248A0`..`0x140B26B87`（8,935 字节）** |")
    add("| `checkout_previews/v3/` | `0x147053c94` | `0x147053c88` | `0x140B1EDB1` | **`sub_140B1DCC0`..`0x140B1EEC9`（4,617 字节）** |")
    add("")
    add("**→ 已结案（R1076，详见 `docs/NIKE_PARITY.md` §15）**：**两个 POST 都承接** —— 配送块内联在")
    add("`checkout_previews/v3` 的 request 体（`sub_140B1DCC0`），订单提交是 `checkouts/v3` 的 POST")
    add("（`sub_140B248A0`，请求级 `paymentToken`）。`NikeFlow.cs` 的 SubmitShipping / SubmitOrder")
    add("已按反编译落地（钉测 `NikeBuyRequestTests`），Nike 行占位只剩 GetPaymentMethods / SubmitPayment（归队列②支付层）。")
    add("")
    add("**→ Farfetch 分类结案（R1077）**：镜像内足迹仅显示名×2（站点目录条目 `{name, display, typeId 4, flag 1}`，")
    add("构造于 70KB 设置描述符构建器 `sub_140F7DDE0`）+ 结账类型枚举 `'Farfetch Checkout'`（`sub_1407528C0` 的")
    add("任务设置数组，与 Shopify / Kith EU / Finishline 并列）——**零路由字面量**。传输层为服务端下发：")
    add("`https://api.cybersole.io/connect/app`（0x14705357c，`sub_140F3D400`）以 **ConfigAdded / SharedAdded /")
    add("ConfigRemoved / SharedRemoved / SubscribeGroups / UnsubscribeGroups** 六键同步配置条目。配置条目的 schema")
    add("需原版登录凭据捕获 —— `FarfetchFlow` 的 7 条占位据此改判为「凭据受阻」分类（消息保留 `endpoint unknown`")
    add("短语，本表计数不变，缺的条件已在消息与流程头写明）。")
    add("")
    add("## 三、风控清单（可复算）")
    add("")
    add("由 `VendorWiring.Rows` 与 `tests/Cybersole.Tests/VendorWiringTests.cs` 逐条钉住：")
    add("%d 行 × 9 列（`Vendor` · `Marker` · `Cookie` · `State` · `Note` · `MarkerFrom` · `Gap` · `Solver` · `Relayed`）。" % wiring_n)
    add("复算：`dotnet test --filter \"FullyQualifiedName~VendorWiring\"`，完整对账见 `docs/VENDOR_COVERAGE.md`。")
    add("")
    add("原版在进度文案或请求头中点名 8 家站点风控（cloudflare · kasada · datadome · akamai · queue-it softblock · perimeterx · botdeflector · vercel）；")
    add("`Solving Incapsula` 为 **0**，是 imperva 的第三个独立证据（R1024）。")
    add("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    print("  wrote docs/CORE_COVERAGE.md")
    print("  flows=%d steps=%d placeholders=%d provenance exit=%s"
          % (len(rows), total_steps, total_placeholders, prov["exit"]))


if __name__ == "__main__":
    main()
