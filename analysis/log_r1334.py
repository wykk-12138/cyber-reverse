"""R1334 record: the cartApi endpoint rule lands, with the host rule measured rather than assumed."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
DOC = 'docs/GRAPHQL_DOCUMENTS.md'

ROUND = """
---

## 第 1334 轮：把 cartApi 的端点规则写进代码——中间先被自己的测试纠正了一次

- **上一轮只找到路径和两个主机标签，没找到拼接规则。** 这轮把它读完：
  ```
  v42 = sub_141E541B0()                                // 实例属性：请求的主机
  v43 = sub_141CF82E0(v42, "www", "themeapis")         // 主机里的 www 换成 themeapis
  v44 = sub_141CF62D0("https://", v43, "/cartApi/checkout")
  ```
  配合字面量 `https://themeapis.`（`0x14708885C`）——那正是**没有 `www.` 前缀时**的结果。
- **落码**：`MagentoCart.CartApiPath`（`/cartApi/checkout`）、`CartApiEndpointFor(host)`、`ThemeApisHost(host)`、
  以及 `ResolveEndpoint(endpointOrHost)`；**六个方法（`CreateEmptyAsync`/`AddProductAsync`/`SetBillingAsync`/
  `AddPaymentAsync`/`SubmitOrderAsync`/`ReadCartAsync`）开头统一过一遍 `ResolveEndpoint`**。
  **今天所有调用方传的都是完整 URL，行为一字未变**；只有传裸主机时才走新规则。
- **测试当场纠正了我**：我第一版只做了 `www.` → `themeapis.` 的替换，四条 Theory 里
  `casio.com` 与 `shop.test` 两条**红了** —— 没有 `www` 可替换时应当**加前缀** `themeapis.`。
  **这正是那个 `https://themeapis.` 字面量存在的理由**，我读了它却没把它读进实现里。
- **产物**：`/cartApi/checkout` 命中 **1**；尺寸 61,402,112 → **61,403,648**。

### 五要素

- **改了什么**：`MagentoCart.cs`（4 个新成员 + 6 处归一化）；`MagentoCartTests.cs`（+5 条：4 行 Theory + 1 条直通断言）；
  新增 2 个 analysis 脚本；重发布；METRICS 重生成。
- **验证命令与输出**：`dotnet test --filter MagentoCartTests` → **25/25**；
  `disp32_scan_any.py 0x146AB27F0` → 1 site；`ida.py dec 0x141E541B0` → 主机属性 getter；
  产物 `/cartApi/checkout` 命中 1；尺寸与哈希见上；内嵌 `5c9484120d44`。
- **数字变化**：套件 2682 → 见 METRICS 当前值（+5）；产物 +1,536 字节。
- **证据等级**：Observation —— 两条拼接指令、`https://themeapis.` 字面量、路径单一引用点、产物命中。
  **Inference（仍未定）** —— 哪家店在用 `themeapis.`；`MagentoCart` 六个方法的调用方默认端点是否该改成它。
- **还剩什么**：确认使用 `themeapis.` 的店铺；据此决定 `CasioFlow`/Warhammer 传的端点；
  `CurrencyConversion`(10406)、`approveMemberPayment`(5407) 归宿；`AddressInput`；方言条件（blocker）。
"""

POINTER = """
---

## 第 1334 轮

- cartApi 的拼接规则读完并落地：`https://<host 的 www 换成 themeapis>/cartApi/checkout`，
  **没有 `www.` 时加前缀**（`https://themeapis.` 那个字面量就是为此存在）。
- `MagentoCart` 增 `CartApiPath` / `CartApiEndpointFor` / `ThemeApisHost` / `ResolveEndpoint`，
  **六个方法开头统一归一化**；今天所有调用方传完整 URL，**行为不变**。
- **测试纠正了我**：第一版只做替换、没做前缀，两条 Theory 当场红。
- 仍未定：**哪家店用 `themeapis.`**，以及 `MagentoCart` 调用方的默认端点是否该改。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1334 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1334 \u8f6e')

text = io.open(DOC, encoding='utf-8').read()
if 'CartApiEndpointFor' not in text:
    text = text.replace(
        '**因此**：`MagentoCart` 里那些方法接收的 `endpoint` 由调用方传入（当前是 `<origin> + /graphql`），\n'
        '这条默认值**存疑**，需要用一次抓包或一个明确的店来定，不要凭形状改。',
        '**R1334 补充**：拼接规则已读完 —— `https://` + `host 的 www 换成 themeapis`（无 `www.` 时加前缀）+ `/cartApi/checkout`，\n'
        '已落成 `MagentoCart.CartApiEndpointFor` / `ThemeApisHost` / `ResolveEndpoint`，六个方法开头统一归一化。\n'
        '**今天所有调用方传完整 URL，行为不变**；仍待定的是**哪家店**用这条路径。')
    io.open(DOC, 'w', encoding='utf-8', newline='').write(text)
    print('GRAPHQL_DOCUMENTS.md updated')
