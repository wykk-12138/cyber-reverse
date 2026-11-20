"""Log R1288: regenerate the captcha doc, and the GoatFlow comment that claimed five live endpoints were unused."""

import io

B = """
## R1288 —— 补上生成物欠账 + 修掉 `GoatFlow` 里"从未使用"的假陈述

### 一、上轮欠的生成物已补

IDA 的 `ida.py str` 恢复后跑 `python tools/captcha_coverage.py`：
`wrote docs/CAPTCHA_COVERAGE.md`，`control=17  families=6  absent=2  provider metadata=24`。
`docs/CAPTCHA_COVERAGE.md` **未提及"完全缺失"**，`absent=2` 是镜像侧的缺席计数，不是复刻件侧。
§七（DotNetBrowser 证据 + 三条标记的结构性判定）已随生成一并落进文档。

### 二、`GoatFlow` 的 14 处 `inferred` 逐条查过：**没有可核销的**

镜像里有 **5 条完整 URL**（`ida_strings.txt` 命中，正向判据）：

| 路径 | 地址 |
|---|---|
| `/web-api/get-csrf-token` | `1470939FC` |
| `/web-api/v1/login` | `147093B44` |
| `/web-api/v1/users/send_otp_token` | `147093BA4` |
| `/web-api/v1/addresses` | `147093A6C` |
| `/web-api/v1/billing_infos` | `147093AD4` |

而 `GoatFlow` **五个全部已调用**（`L54` / `L60` / `L65` / `L69` / `L132` 附近）。
所以剩下的 `inferred` 只有两类，**都不能核销**：

1. **请求体字段名**（`email` / `password`）——镜像里没有 body，属实无证据；
2. **`/v1/product_variants/buy_bar_data`、`/v1/buys`、`productTemplateId`** —— 在字符串 dump 里 **0 命中**。

### 三、但发现一处**真的假陈述**

原注释（`L44`）写着：

> The image carries four /web-api/v1 paths **this flow never used**

**五个都在用**，而且那句话自己下面三行就写着 `path evidenced`。这是**注释与代码矛盾**——
`GoatFlow.TotalInferred`（14）里有一部分是这条过时陈述在误导读者。

已改为：五条路径逐条列出**地址**，并明确区分「路径是镜像的、body 不是」；同时点明两个产品端点
`buy_bar_data` / `/v1/buys` 在 dump 里 0 命中、所以**它们的路径**也属 inferred。

### 四、验证

`Goat*` **5/5**（4 过 + 1 跳）；全量 **2478 通过 / 0 失败 / 2 跳过 / 2480**。

证据等级：Observation = 五条 URL 与地址、四处调用点、dump 里 0 命中的两个产品端点；
Inference = 「body 无证据」；Unknown = GOAT 加车/下单的真实 body（需 live capture）。
"""

V = """
---

## 第 1288 轮：补生成物 + GoatFlow 端点的假陈述修正

- `tools/captcha_coverage.py` 重生成成功（control=17 / families=6 / absent=2 / metadata=24），§七 已进文档。
- `GoatFlow` 14 处 inferred 逐条查：镜像 5 条完整 URL 全部**已在调用**；剩余 inferred 只有 body 字段与 0 命中的产品端点 ⇒ **无可核销**。
- 修掉 `L44` 的假陈述「four paths this flow **never used**」→ 五条带地址列出（镜像的路径 / 非镜像的 body 分开说）。
- 全量 **2478/0/2/2480**。
"""

H = """
## R1288 —— captcha 文档重生成完成；GoatFlow 假陈述修正；全量 2478/0/2/2480

Observation：
- 生成器跑通：`control=17 families=6 absent=2 provider metadata=24`。
- GOAT 五条 URL 地址：`1470939FC`(csrf) / `147093B44`(login) / `147093BA4`(otp) / `147093A6C`(addresses) / `147093AD4`(billing)。
- 五条在 GoatFlow 均已有调用；`buy_bar_data`/`/v1/buys`/`productTemplateId` 在 dump 0 命中。
- 全量 2478/0/2/2480。

下轮：`StoreFlow`(10) 与 `MagentoFlow`(6) 的 inferred 按同法逐条查——先查 dump，能命中就升为实证，不能则写明 0 命中。
"""

for path, text in (('D:/projects/cyber-reverse/docs/BLOCKERS.md', B),
                   ('D:/projects/cyber-reverse/replica/docs/VERDICT.md', V),
                   ('D:/projects/cyber-reverse/docs/HANDOFF.md', H)):
    io.open(path, 'a', encoding='utf-8', newline='\n').write(text)
    print('logged', path)
