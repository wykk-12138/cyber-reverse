"""Record R791, second attempt. The first never ran: its output was piped into a Select-String whose pattern was an
invalid regex, and parameter binding fails before the pipeline executes."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 217. Warhammer 补上运费/地址步：**71% → 86%**，映射来自 mutation 原文

> R791。`RetailFlows.cs` 新增 `WarhammerFlow.SubmitShippingAsync`。

### 一、R790 说缺的东西，原文里就有

R790 把 `UpdateShippingAddress` 的 `attributes` 映射记成"没取证"。这一轮把那段整行打出来，映射就在里面：

```
变量      $copyFromId: Int, $firstname: String, $lastname: String, $address1: String,
          $address2: String, $zipcode: String, $city: String, $state_id: Int,
          $country_id: Int, $phone: String, $document_number: String,
          $tax_code: String, $neighborhood: String

attributes {copyFromId: …, firstname: $firstname, …, stateId: $state_id, countryId: $country_id,
            phone: $phone, documentNumber: $document_number, taxCode: $tax_code, neighborhood: …}
```

**十三个字段全部可选（没有一个 `!`）。** 变量 snake_case、属性 camelCase ——
**对应关系是原文写死的，不是推断。**

### 二、顺带解答了 R790 的第二个 Unknown

选择集里有 **`shippingRates { ...shippingRate }`** ——
**运费率是这一步的返回值。所以 `selectedShippingRateId` 不是"来源未知"，是"从这里来"。**

复刻件因此把返回体里的第一个 rate id 记进 `Session.Vars["shippingRateId"]`。

### 三、实现

七个字段直接对上 `ProfileData`：`FirstName` / `LastName` / `Address1` / `Address2` / `Zip` / `City` / `Phone`。

**`state_id` / `country_id` 是 Int，而 Profile 里 `State` / `Country` 是名字 —— 对不上。**
所以只有会话里已解析出数字 id 时才发：

```csharp
foreach (var numeric in new[] { "state_id", "country_id" })
    if (c.Session.Vars.TryGetValue(numeric, out var id) && int.TryParse(id, out var parsed))
        variables[numeric] = parsed;
```

**为什么不硬发**：把州名塞进 Int 会被拒；猜一个 id 会把订单挂到错误的地区**而且不报错**。
**十三个变量全可选，省略之后请求仍然合法。**

### 四、`operationName`

**这条 mutation 在镜像里是匿名的**（`mutation (` 无名字），所以请求体**不带** `operationName` ——
与 `AddToCart`（有名字）不同。**这个差别写进了代码注释。**

### 五、覆盖率

```
warhammer    +  +  +  +  +  -  +   86%
resolved 63/63 flows; fully covered 49; exempt 2
```

**71% → 86%，只剩 `SubmitPaymentAsync`。`fully covered` 仍 49** —— 要 7/7 才进那一栏。

### 六、验证

```
构建                已成功
ModuleCoverageTests warhammer 86%
完整套件            1766 通过 / 0 失败 / 0 跳过（与改动前同数）
四项度量            4 / 0 / 17 / 78 / 0（未变）
```

### 七、仍然 Unknown

- **`state_id` / `country_id` 的数值**：**Unknown** —— 有就发、没有就不发。
- **`document_number` / `tax_code` / `neighborhood` / `copyFromId`**：**Unknown** —— 未用。
- **支付 `token` 的来源**：**Unknown** —— 挡着 100%。
- **`shippingRateId` 的选取规则**：**Inference（低）** —— 现在取第一个 `id`，真实规则未取证。

### 八、两次过程事故，都记下来

1. **又以为写坏了 `WarhammerQueries.UpdateShippingAddress`** —— 构建证明文件是对的，坏字只在调用回显里。
   **但这次不同：标识符是编译期检查的**（R789 那次是字符串字面量）。
   **把手抄文本换成生成的标识符引用，同时消掉了抄写风险和这种误判。**
2. **记录脚本第一次根本没跑**：输出被管道接进 `Select-String -Pattern "+=|check"`，
   **而 `+=` 不是合法正则 —— 参数绑定错误发生在管道执行之前，所以 Python 从未启动。**
   **教训：记录脚本裸跑，不要接过滤；"没有输出"要先确认脚本跑了没有。**
"""

VERDICT = """

---

## 第 791 轮：Warhammer 补上地址/运费步 —— 71% → 86%

### R790 说缺的东西，原文里就有

```
变量      $copyFromId: Int, $firstname: String, …, $state_id: Int, $country_id: Int, $phone: String, …
attributes {copyFromId: …, firstname: $firstname, …, stateId: $state_id, countryId: $country_id, …}
```

**十三个字段全可选；变量 snake_case、属性 camelCase，对应关系是原文写死的。**

### 顺带解答了第二个 Unknown

选择集里有 `shippingRates { ...shippingRate }` ——
**运费率是这一步的返回值，所以 `selectedShippingRateId` 不是"来源未知"，是"从这里来"。**

### 实现

七个字段直接对 `ProfileData`。**`state_id`/`country_id` 是 Int，Profile 里是名字 → 有就发、没有就省。**

> **把州名塞进 Int 会被拒；猜一个 id 会把订单挂到错误地区而且不报错。十三字段全可选，省略后仍合法。**

**匿名 mutation → 不带 `operationName`**（与有名字的 `AddToCart` 不同）。

### 覆盖率

```
warhammer    +  +  +  +  +  -  +   86%
resolved 63/63 · fully covered 49 · exempt 2
```

**只剩 `SubmitPaymentAsync`。**

### 验证

```
构建绿 · warhammer 86% · 整套 1766 / 0 · 度量未变
```

### 两次过程事故

1. 又以为写坏了 `WarhammerQueries.UpdateShippingAddress` —— **构建证明文件是对的；标识符是编译期检查的。**
2. **记录脚本第一次根本没跑** —— 输出接进了 `Select-String -Pattern "+=|check"`，
   而 `+=` 不合法，**参数绑定错误在管道执行前发生，Python 从未启动**。
   **教训：记录脚本裸跑；"没有输出"先确认脚本跑了没有。**
"""

BACKLOG_ADD = """

## 核心 — Warhammer（R791：86%，只差支付）

| 步骤 | operation | 状态 |
|---|---|---|
| `AddToCartAsync` | `AddToCart`（536） | ✅ R789 |
| `SubmitShippingAsync` | `UpdateShippingAddress`（1994） | ✅ R791 |
| 运费选择 | `UpdateShippingRate`（2248） | 原文备好，未接 |
| `SubmitOrderAsync` | — | ❌ **仍是编的 `/api/orders`** |
| `SubmitPaymentAsync` | `ApproveOnboardPaymentMutation`（4022） | ❌ 缺支付 `token` 来源 |

**覆盖率 86%（6/7）。**

**R791 的映射依据**（原文写死）：13 个变量全可选，snake_case 变量 → camelCase 属性。

| 仍 Unknown | |
|---|---|
| `state_id` / `country_id` 数值 | 有就发、没有就省 |
| 支付 `token` 来源 | 挡着 100% |
| `shippingRateId` 选取规则 | 取第一个 `id`，Inference（低） |
| 订单提交 operation | 未定位 |

**下一步**：`SubmitOrderAsync` 的 operation 定位（比支付 token 更可能取证成功）。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R791", BLOCKER)
    ensure(RSTATUS, "R791", BLOCKER)
    ensure(RVERDICT, "第 791 轮", VERDICT)
    ensure(BACKLOG, "R791", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 791 轮" if path == RVERDICT else "R791"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R791: Warhammer gains its shipping step, taking the mapping from the mutation text itself -- 71% to 86%\n\n"
         "R790 recorded the address mapping as unknown. Printing that line of the recovered mutation in full showed it\n"
         "was there: thirteen optional variables, each mapped to a camelCase attribute inside\n"
         "updateShippingAddress(attributes:), snake_case on the left and camelCase on the right. The correspondence is\n"
         "stated by the image rather than inferred, which is the difference between reading and guessing.\n\n"
         "The same block answered R790's second unknown. The selection set includes shippingRates, so the rate id for\n"
         "the next step is not of unknown origin -- it is this step's return value. The flow records the first rate id\n"
         "from the response into the session.\n\n"
         "Seven fields map straight onto ProfileData. state_id and country_id are Ints while the profile holds names,\n"
         "so they travel only when a caller has already resolved numeric ids: coercing a name where an Int is expected\n"
         "would be rejected, and inventing an id would attach the order to the wrong region without an error. All\n"
         "thirteen variables being optional means omitting them still yields a valid request.\n\n"
         "Because this mutation is anonymous in the image, the request carries no operationName, unlike AddToCart.\n\n"
         "Warhammer moves from 71% to 86%: six of seven, with SubmitPaymentAsync remaining. The fully-covered count\n"
         "stays at 49 because a module must reach seven of seven to join it.\n\n"
         "Two process accidents worth recording. I again believed I had corrupted the generated identifier reference,\n"
         "and the build disproved it -- identifiers are compile-checked where string literals are not, so generating\n"
         "them removed both the transcription risk and this false alarm. And the first attempt at this record never\n"
         "ran at all: its output was piped into a Select-String whose pattern was an invalid regex, and parameter\n"
         "binding fails before the pipeline executes. Run record scripts bare, and when there is no output, first\n"
         "establish that the script started.\n\n"
         "Suite 1766 pass / 0 fail unchanged; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
