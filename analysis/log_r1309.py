"""R1309 round record: Saucony lands in the catalogue, with its refusals named."""

import io

VERDICT = 'replica/docs/VERDICT.md'
HANDOFF = 'docs/HANDOFF.md'
ROADMAP = 'docs/REMAINING_REPLICATION_ROADMAP.md'

ROUND = """
---

## 第 1309 轮：Saucony 进目录了——能做的两步做，做不了的八步**按序号拒绝**

- **上一轮只发现、这一轮落码**。新增 `SauconyFlow : StoreFlow`：
  - `Id/Name/Domains` = `saucony` / `Saucony` / `saucony.com`（域名是镜像里那张按字母排序的域表里的冻结串 `0x147099D1C`）；
  - `StoreIds` = `saucony_us` / `saucony_ca` / `saucony_eu` / `saucony_europe`（`0x14715229C` / `0x147152204` / `0x147152234` / `0x147152264`）；
  - `StoreIdFor(url)` 按主机后缀选区域 id，**且要求主机名里含 `saucony`**。
- **能做的做**：`GetHomeAsync`（纯 GET）、`FindProductAsync`（GET + 通用 name/price 提取 + 原文落 `raw`）。
- **做不了的不假装**：`AddToCart`(d__7) / `SubmitShipping`(d__9) / `SubmitBilling`(d__10) /
  `SubmitOrder`(d__11) / `HandleOrderResult`(d__12) / `PayerAuthenticate`(d__13) 全部返回带**镜像自己的序号**的拒绝，
  理由写清：该类用 `ApiHeaders` + `traceparent` + `BuildAuthToken` 自己拼请求，而**镜像里没有任何字面量拼出 Saucony 的 API 路径**
  （搜 `saucony` 只有域名和四个 id）。凭猜编 `/api/cart` 或支付提交地址，是这个项目撤回次数最多的一类错误。
- **测试抓到一个真 bug**：`StoreIdFor("https://example.com/x")` 最初返回 `saucony_us`——因为它把任何 `.com` 都当美国站。
  改成先要求主机含 `saucony`。**这是"猜"的代价的活标本**，注释里留了原文。
- **两处守卫按事实移动**：目录 65 → **66**（`ArrowAndBeastTests`、`CoreTests`）。
  前者原名 `TheCatalogueIsSixtyThreeModules` 却在断言 65——**名字和数字早就对不上了**，
  这轮一并改成 `TheCatalogueSizeIsPinned` 并加一条 `Assert.Contains(..., m => m.Id == "saucony")`。
  改名的理由写在注释里：一个改过名却没人再读的守卫，等于没有守卫。

### 五要素

- **改了什么**：新增 `replica/src/Cybersole.Stores/Flows/SauconyFlow.cs`（约 190 行）、
  新增 `replica/tests/Cybersole.Tests/SauconyFlowTests.cs`（14 条）；`Modules/Registry.cs` 注册；
  `ArrowAndBeastTests.cs` / `CoreTests.cs` 计数 65 → 66；NativeAOT 重发布；`docs/METRICS.md` 重生成。
- **验证命令与输出**：`dotnet test --filter SauconyFlowTests` → **14/14**（首轮 13/1，红的正是 `.com` 那个 bug）；
  连同两处计数守卫 `18/18`；`store_catalog.py` → `entries in CreateAll(): 66`；
  `artifact_freshness.py` → `state: current`；`metrics_report.py` → 全部 exit 0；
  `mutation-check.py` → 见本轮 METRICS 变异行。
- **数字变化**（均引 `docs/METRICS.md`）：目录 65 → **66**；套件 2562 → 见 METRICS 当前值（+14）；
  产物 `61,248,512` → **`61,259,776`** 字节。
- **证据等级**：Observation —— 域名串与四个 id 的地址、四行显示名、八个步骤与 d__ 序号、四个字段名、
  以及"搜 `saucony` 只有域名与 id"这一事实。Inference —— 该类的请求由 `ApiHeaders`/`BuildAuthToken` 自拼
  （由辅助方法名推定，方法体未反编译）。Unknown —— 六个拒绝步骤的目标路径与报文。
- **还剩什么**：那六个步骤的 API 路径（这是 Saucony 唯一剩下的硬骨头）；`HandleOrderResult` /
  `PayerAuthenticate` 的报文；66 个 absent 支付名其余部分。
"""

POINTER = """
---

## 第 1309 轮

- **Saucony 落码**：`SauconyFlow` + 目录注册（65 → 66）。`GetHome` / `FindProduct` 实现，
  六个未解步骤**按镜像自己的 d__ 序号拒绝**（`d__7` / `d__9` / `d__10` / `d__11` / `d__12` / `d__13`）。
- 测试抓到一个真 bug：`StoreIdFor` 把任何 `.com` 都当美国站，`example.com` 会被认成 Saucony → 已修（先要求主机含 `saucony`）。
- `ArrowAndBeastTests.TheCatalogueIsSixtyThreeModules` 断言的一直是 65——名字与数字早就不符，
  已改名 `TheCatalogueSizeIsPinned` 并钉住 66 + `saucony` 存在。
- Saucony 唯一剩下的硬骨头：**六个步骤的 API 路径**（镜像里没有任何字面量拼出它们）。
"""


def append(path, block, marker):
    text = io.open(path, encoding='utf-8').read()
    if marker and marker in text:
        print('already recorded, skipped: %s' % path)
        return
    with io.open(path, 'a', encoding='utf-8', newline='') as fh:
        fh.write(block)
    print('appended %d chars to %s' % (len(block), path))


append(VERDICT, ROUND, '\u7b2c 1309 \u8f6e')
append(HANDOFF, POINTER, '\u7b2c 1309 \u8f6e')

text = io.open(ROADMAP, encoding='utf-8').read()
old = '     **\u4e0b\u4e00\u8f6e\u5148\u5b9a\u5b83\u7684 `flow type` \u518d\u8fdb `CreateAll()`**\uff0c\u4e0d\u8981\u51ed\u731c\u3002'
new = ('     **R1309 \u5df2\u8fdb `CreateAll()`\uff08\u76ee\u5f55 65 \u2192 66\uff09**\uff0c\u80fd\u505a\u7684 `GetHome`/`FindProduct` \u5df2\u5b9e\u73b0\uff0c\n'
       '     \u516d\u4e2a\u672a\u89e3\u6b65\u9aa4\u6309\u955c\u50cf\u81ea\u5df1\u7684 `d__\u5e8f\u53f7`\u62d2\u7edd\uff08`SauconyFlow`\uff09\u3002\u5269\u4e0b\u7684\u786c\u9aa8\u5934\u662f\n'
       '     **\u90a3\u516d\u4e2a\u6b65\u9aa4\u7684 API \u8def\u5f84**\u2014\u2014\u955c\u50cf\u91cc\u641c `saucony` \u53ea\u6709\u57df\u540d\u4e0e\u56db\u4e2a id\uff0c\u6ca1\u6709\u4efb\u4f55\u5b57\u9762\u91cf\u62fc\u51fa\u8def\u5f84\u3002')
if old in text:
    text = text.replace(old, new)
    io.open(ROADMAP, 'w', encoding='utf-8', newline='').write(text)
    print('roadmap updated')
else:
    print('roadmap anchor not found (already updated?)')
