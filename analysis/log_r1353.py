"""R1353 record: the third probe's dead end, and the store table that already held the endpoint."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
UNATTR = 'docs/UNATTRIBUTED_OPERATIONS.md'

ROUND = """
---

## 第 1353 轮：第三种静态手法也走到底了 —— 六份正式登记为 Unknown；第七份在**旧表里找到了家**

- **新手法（本轮首次用）**：无主机无路径的发送方，反编译出来**都是异步状态机的 `MoveNext`**，
  URL 在调用方填的字段里。于是查**谁 Start 了这个状态机**：
  `disp32_scan_any.py 0x140E55F90`（getCart 的 MoveNext）→ 5 个引用点 → `0x1422A07A4` / `0x1428EA9E7` / `0x1428EAADA`
  三个都在函数里，**但三个函数的字面量都是 0** —— **那是元数据/表，不是代码**。
- **三探全空**：主机扫描（R1352）、路径扫描（R1352）、调用方扫描（本轮）。
  **所以这六份在现有工具集下静态不可归属 —— 这就是结论，不是继续猜的理由。**
  已写入 `docs/UNATTRIBUTED_OPERATIONS.md`，逐条写明**需要什么证据才能定**（一次运行期抓包看到主机）。
- **第七份有家**：`checkoutAsGuest`(148) 的发送方带 `https://www.on.com/ko-kr/graphql`，
  而 **`AccountAndAuthFamilies.OnRunning.GraphQl` 早就是这个字符串** —— 那张表是更早一轮写的，
  当时没有任何东西用它。**现在它有了用户**：`OnRunningGraphQl` + `StoreFlow.GuestCallbackAsync` 分支。
- **一次真正的自伤（值得记）**：我用 `git show HEAD:path > file` 还原文件，**PowerShell 的 `>` 写 UTF-16**，
  把 `StoreFlow.cs` 写成 156 KB 的 UTF-16 乱码；随后按索引切片又拼坏了一行。
  正确做法：**`subprocess.run(['git','show',...]).stdout` 取字节再 `write bytes`**。
  已按此还原并只替换**一个成员**（`GuestCallbackAsync`），43 条 StoreFlow/Highsnobiety 用例全绿。
- **产物**：`mutation checkoutAsGuest` UTF-16 命中 **1**；尺寸 62,046,016 → **62,055,232**。
  （`on.com/ko-kr/graphql` 两编码皆 0 —— 该 URL 由常量拼接，字面量本身不在产物里，按 §4.5 无结论。）

### 五要素

- **改了什么**：新增 `Flows/OnRunningGraphQl.cs`、`tests/OnRunningGraphQlTests.cs`（4 条）；
  `StoreFlow.GuestCallbackAsync` 由表达式体改成带分支的 async；新增 4 个 analysis 脚本；
  新增 `docs/UNATTRIBUTED_OPERATIONS.md`；重发布；METRICS 重生成。
- **验证命令与输出**：`OnRunningGraphQlTests` → **4/4**；`StoreFlow|Guest|Highsnobiety` → **43/43**；
  `operation_gap.py` → 覆盖 **37/65**（缺 28）；`orphan_documents.py` → 0；
  产物命中 1；尺寸 62,046,016 → 62,055,232。
- **数字变化**：覆盖 36 → **37**；缺 29 → **28**；套件 +4；产物 +9,216 字节。
- **证据等级**：Observation —— 三个 MoveNext 调用方零字面量、On Running 表里已有的字符串、文档 148 字符、产物命中。
  Unknown —— 六份无主机无路径操作的归属（**需要运行期抓包**，已登记）。
- **还剩什么**：Unknown 六份（已登记，等运行期证据）；B 块其余；`approveMemberPayment` 两方言；浏览器侧结账面；
  `/cartApi/checkout` 归属；`AddressInput`；方言条件（blocker）；AO 三个 checkout 体；Saucony 六步路径。
"""

POINTER = """
---

## 第 1353 轮

- **第三种静态手法（查谁 Start 状态机）也走到底**：getCart 的 MoveNext 有三个调用方，**三个函数字面量全为 0**（是元数据不是代码）。
  三探全空（主机 / 路径 / 调用方）→ **六份正式登记 `docs/UNATTRIBUTED_OPERATIONS.md`**，写明所需证据 = 一次运行期抓包。
- **`checkoutAsGuest`(148) 归位**：其发送方带 `https://www.on.com/ko-kr/graphql`，
  而 `AccountAndAuthFamilies.OnRunning.GraphQl` 早就是这个字符串 —— **那张旧表终于有了用户**。
  落成 `OnRunningGraphQl` + `StoreFlow.GuestCallbackAsync` 分支。
- **自伤一条**：`git show HEAD:path > file` 在 PowerShell 里写 **UTF-16**，把 `StoreFlow.cs` 写成乱码；
  正确做法是 `subprocess` 取字节再写 bytes。已还原，只替换一个成员。
- 覆盖 36 → **37/65**，缺 29 → **28**。
"""

UNATTR_TEXT = """# 不可归属的 GraphQL 操作（R1352–R1353）

这六份文档的发送方**既无主机也无路径**，且三种静态手法都试过：

| 手法 | 做法 | 结果 |
|---|---|---|
| 主机扫描 | 扫发送方函数里的全部字面量 | 无 `http`、无 `graphql.json` |
| 路径扫描 | 扫 `api/` / `/graphql` / 含 `?` 的相对路径 | 无 |
| 调用方扫描 | 反编译出来是异步状态机 → 扫"谁 Start 了这个 MoveNext" | 三个调用方函数**字面量全为 0**（元数据，不是代码） |

| 操作 | 长度 | 声明集 |
|---|---|---|
| `getCart` | 3234 | `key`、`locale` |
| `createCartByStore` | 421 | `country`、`currency`、`locale`、`storeKey`、`taxMode` |
| `createMyPayment` | 493 | `amount`、`customFields`、`key`、`paymentInterface`、`paymentMethod` |
| `initiateCheckout` | 251 | 无 |
| `saveAddress` | 296 | `address`、`editAddress`、`saveAddress`、`setDefault` |
| `maintainShippingGroups` | 223 | `cartId` |

**需要什么才能定**：一次**运行期抓包**，看到这些操作实际打到哪个主机。
静态一律到此为止 —— 再往下的推断没有证据支撑。

另有两条不是"无主机"，而是**别的语境缺失**：

- `approveMemberPayment` 有两份方言（5407 / 5620 字符），**选择条件**不明；
- `/cartApi/checkout` 有完整变量（cartType / lineItems / locationId / sourceSystem，值 Retail / Shopify）但**没有发送方 URL**。
"""

with io.open(UNATTR, 'w', encoding='utf-8', newline='') as fh:
    fh.write(UNATTR_TEXT)
print('wrote %s' % UNATTR)


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1353 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1353 \u8f6e')
