"""Record R902: ten customer paths added, and the coverage moved for the first time in a while."""

import io
import os
import re
import subprocess

ROOT = r"D:\projects\cyber-reverse"
DOC = os.path.join(ROOT, "docs", "ASYNC_OPS.md")
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

TABLE = """
### `/customer/v1/` 那 10 条补上了 —— 覆盖率**第一次真的动了**（R902）

**R901 说「下一轮第一件事：跑 `-v` 拿清单」。跑了，然后补了最多的一族。**

### 补了什么

**`/customer/v1/*` 10 条 —— 账户管理的完整四动词集与注册链路：**

| 路径 | 干什么 |
|---|---|
| `/customer/v1/address/add` · `del` · `list` · `update` | 地址增删查改 |
| `/customer/v1/customer/app` | 读当前客户 |
| `/customer/v1/customer/exist` | 注册前的存在性检查 |
| `/customer/v1/customer/guest/register` | 访客注册 |
| `/customer/v1/customer/login` · `register` | 登录 / 注册 |
| `/customer/v1/verification/send` | 发验证码 |

**而按 §2.7c 先查过：`/customer/v1` 字面量全库没有。
`ScapiEndpoints.cs` 里那个 customer 是 Salesforce Commerce API，另一回事。**

### 数字变化

| 度量 | R901 | **R902** |
|---|---|---|
| `hostless` 覆盖 | 46 / 67（68.7%） | **56 / 67（83.6%）** |
| 总缺失 | 105 | **95** |
| 套件 | 1790 | **1796** |

**所以这是 R892 以来第一次有**可测的产品进步**，而不是度量改进。**

### 而这一族比 Vans 那族更值得标注

**`OwnerIsUnknown = true`。它比 `VansEndpoints.OwnershipIsInference = false` 弱一档：**

| 类 | 归属状态 | 为什么 |
|---|---|---|
| `VansEndpoints` | **Observation** | 宿主与路径同处一条字面量 |
| **`CustomerApiEndpoints`** | **Unknown** | **没有任何一条字面量同时含这些路径与宿主** |

**所以这 10 条是「镜像里确实存在的端点，而属哪个站不知道」。
写常量是正当的（路径是观察），写步骤不是（体、响应、鉴权、调用者四样全缺）。**

### 6 个用例里两个值得说

| 用例 | 钉住 |
|---|---|
| `TheOwningStoreIsRecordedAsUnknown` | **把「归属未知」钉成断言** —— 将来谁找到共现证据，得改这个 flag 并说明 |
| `TheListIsOrderedForUseRatherThanAlphabetically` | **`All` 是按注册流程排的，不是字典序** —— 断言首项是 `CustomerExist` 且整体不等于排序结果 |
"""

if "`/customer/v1/` 那 10 条补上了" not in io.open(DOC, encoding="utf-8").read():
    io.open(DOC, "a", encoding="utf-8").write("\n" + TABLE)
    print("  ASYNC_OPS.md: R902 appended")

BLOCKER = """

---

## 326. `/customer/v1/` 10 条补齐：hostless 覆盖 **68.7% → 83.6%**，套件 **1790 → 1796**

> R902。**改产品代码 +6 用例。** 套件 **1796 通过 / 0 失败 / 0 跳过**。

### 一、补了什么

**`/customer/v1/*` 10 条：地址四动词（`add` `del` `list` `update`）· 读当前客户（`app`）·
存在性检查（`exist`）· 访客注册（`guest/register`）· 登录与注册 · 发验证码（`verification/send`）。**

**先查过（§2.7c）：`/customer/v1` 字面量全库没有；`ScapiEndpoints.cs` 那个 customer 是 Salesforce 的，另一回事。**

### 二、数字

| 度量 | R901 | **R902** |
|---|---|---|
| `hostless` 覆盖 | 46 / 67（68.7%） | **56 / 67（83.6%）** |
| 总缺失 | 105 | **95** |
| 套件 | 1790 | **1796** |

**R892 以来第一次有可测的**产品**进步，而不是度量改进 —— 这正是 R901 说的缺的东西。**

### 三、归属比 Vans 那族弱一档

| 类 | 归属 | 依据 |
|---|---|---|
| `VansEndpoints` | **Observation** | 宿主与路径同处一条字面量 |
| **`CustomerApiEndpoints`** | **Unknown**（`OwnerIsUnknown = true`） | **没有任何字面量同时含路径与宿主** |

**所以这 10 条是「镜像里确实存在的端点，属哪个站不知道」。
写常量正当（路径是观察），写步骤不正当（体/响应/鉴权/调用者四样全缺）。**

### 四、6 个用例

**`TenPathsWereRecovered`（含 `RecoveredPathCount` 与去重）· `TheOwningStoreIsRecordedAsUnknown`（把「未知」钉成断言）·
`TheAddressVerbsAreComplete` · `TheSignupCheckAndTheRegistrationAreSeparate`（只注册不查会重复建号）·
`EveryPathIsUnderTheCustomerFamily` · `TheListIsOrderedForUseRatherThanAlphabetically`**

### 五、验证

```
endpoint_coverage.py -v   -> hostless 里列出这 10 条
where_is customer         -> 11 文件，但 /customer/v1 字面量全库无
CustomerApiEndpoints.cs   -> 新建，10 常量 + OwnerIsUnknown + RecoveredPathCount
test --filter CustomerApi -> 6 通过
endpoint_coverage.py      -> hostless 56/67 = 83.6%，missing 95
metrics_report.py         -> 1796 通过 / 0 失败
```

### 六、仍然 Unknown

- **这 10 条属哪个站**：**Unknown** —— 无共现证据。
- **请求体 / 响应 / 鉴权 / 谁调用**：**全部 Unknown** —— 所以无步骤。
- **`missing 95` 里还有多少是这种「整族缺」**：**Unknown** ——
  **`-v` 里还看到 `/commerce/v1/` 2 条、`/product-core/v1/` 2 条、`/legacy/v1/` 2 条、`/checkout/v1/orders` 等。**
- **`/shield/v1/verify_otp`**：**特别注意** —— 名字像防护服务的 OTP 校验，**属优先级 ②**。

### 七、教训

**R901 的教训是「先做产品再做度量」。这一轮的验证很直接：
**补 10 个常量，`hostless` 从 68.7% 到 83.6%，`missing` 从 105 到 95，套件 +6。**

**而前五轮的度量工作，一行产品代码也没动。**

**所以度量的正确用法是：跑到能列出清单就停。R901 之后我确实停了，而清单第一条就是这一族。**
"""

VERDICT = """

---

## 第 902 轮：`/customer/v1/` 10 条补齐 —— hostless 覆盖 68.7% → 83.6%

### 补了什么

**10 条：地址四动词（`add` `del` `list` `update`）· `customer/app` · `customer/exist` ·
`customer/guest/register` · `customer/login` · `customer/register` · `verification/send`**

**先查过（§2.7c）：`/customer/v1` 字面量全库无。**

### 数字

| 度量 | R901 | **R902** |
|---|---|---|
| `hostless` 覆盖 | 46 / 67（68.7%） | **56 / 67（83.6%）** |
| 总缺失 | 105 | **95** |
| 套件 | 1790 | **1796** |

> **R892 以来第一次有可测的**产品**进步，而不是度量改进。**

### 归属比 Vans 那族弱一档

| 类 | 归属 | 依据 |
|---|---|---|
| `VansEndpoints` | **Observation** | 宿主与路径同处一条字面量 |
| **`CustomerApiEndpoints`** | **Unknown** | **没有字面量同时含路径与宿主** |

> **写常量正当（路径是观察），写步骤不正当（体/响应/鉴权/调用者四样全缺）。**

### 6 个用例

**`TheOwningStoreIsRecordedAsUnknown`（把「未知」钉成断言）· `TheListIsOrderedForUseRatherThanAlphabetically`
（`All` 按注册流程排，断言首项是 `CustomerExist` 且整体不等于排序结果）· 其余四个钉数量与族前缀。**

### 仍然 Unknown

**这 10 条属哪个站** · **请求体/响应/鉴权/调用者全未知**（故无步骤）·
**`missing 95` 里还有多少整族缺**（`-v` 还看到 `/commerce/v1/` 2 条、`/product-core/v1/` 2 条、`/legacy/v1/` 2 条）·
**`/shield/v1/verify_otp`**（**名字像防护服务的 OTP 校验，属优先级 ②**）

### 教训

> **R901 说「先做产品再做度量」。这一轮验证很直接：补 10 个常量，hostless 68.7% → 83.6%，missing 105 → 95，套件 +6。**
> **而前五轮的度量工作，一行产品代码也没动。**
> **度量的正确用法是：跑到能列出清单就停 —— 而清单第一条就是这一族。**
"""

BACKLOG_ADD = """

## 优先级 ① — `/customer/v1/` 10 条（R902，**改产品代码 +6 用例**）

### 10 条

**地址 `add` `del` `list` `update` · `customer/app` · `customer/exist` · `customer/guest/register` ·
`customer/login` · `customer/register` · `verification/send`**

### 数字

| 度量 | R901 | **R902** |
|---|---|---|
| `hostless` 覆盖 | 46/67（68.7%） | **56/67（83.6%）** |
| 总缺失 | 105 | **95** |
| 套件 | 1790 | **1796** |

### 归属：Unknown（比 Vans 弱一档）

**`CustomerApiEndpoints.OwnerIsUnknown = true`** —— 无任何字面量同时含路径与宿主。
**对比 `VansEndpoints.OwnershipIsInference = false`（共现有证）。**

**写常量正当（路径是观察）· 写步骤不正当（体/响应/鉴权/调用者四样全缺）。**

### 6 用例

**`TheOwningStoreIsRecordedAsUnknown` · `TheListIsOrderedForUseRatherThanAlphabetically` · 其余钉数量与族前缀**

| 仍 Unknown | |
|---|---|
| 这 10 条属哪个站 | 无共现 |
| 体/响应/鉴权/调用者 | 四样全缺 |
| missing 95 里还有多少整族缺 | `/commerce/v1/` 2 · `/product-core/v1/` 2 · `/legacy/v1/` 2 |
| **`/shield/v1/verify_otp`** | **优先级 ②** |

**纪律**：**度量跑到能列清单就停 —— 再往后的精度不如一行常量。**
"""


def ensure(path, marker, text):
    b = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in b:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R902", BLOCKER)
    ensure(RSTATUS, "R902", BLOCKER)
    ensure(RVERDICT, "第 902 轮", VERDICT)
    ensure(BACKLOG, "R902", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R902" not in h:
        h += ("\n## R902 补充 — `/customer/v1/` 10 条补齐（**改产品代码 +6 用例**）\n\n"
              "**补 10 条**：地址四动词 · `customer/app` · `customer/exist` · `customer/guest/register` · "
              "`customer/login` · `customer/register` · `verification/send`。**先查过 `/customer/v1` 字面量全库无。**\n"
              "**数字**：`hostless` 覆盖 **46/67 → 56/67（68.7% → 83.6%）** · 总缺失 **105 → 95** · 套件 **1790 → 1796**。"
              "**R892 以来第一次可测的产品进步。**\n"
              "**归属 Unknown**（`OwnerIsUnknown = true`）：无字面量同时含路径与宿主 → **写常量正当，写步骤不正当**。\n"
              "**下一族**：`/commerce/v1/` 2 条 · `/product-core/v1/` 2 条 · `/legacy/v1/` 2 条 · **`/shield/v1/verify_otp`（优先级 ②）**。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    doc = io.open(RVERDICT, encoding="utf-8", errors="surrogateescape").read()
    prose = re.sub(r"```.*?```", "\n", doc, flags=re.S)
    n = sum(1 for m in re.finditer(r"(\d+)\s*(?:个模块|modules)", prose) if int(m.group(1)) >= 20)
    print("  'N 个模块' sentences now: %d (ceiling 16)" % n)
    if n > 16:
        print("  !! over the ceiling")
        return 1

    ok = all(k in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, k in ((RBLOCK, "R902"), (RSTATUS, "R902"), (RVERDICT, "第 902 轮"), (BACKLOG, "R902")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R902: ten customer API paths, and the coverage figure moves for the first time in six rounds\n\n"
         "R901 ended by saying the next round's first action was to run the tool verbosely and take the list. This\n"
         " round did that, and the largest single family on it was the account API at /customer/v1/, ten paths the\n"
         " replica had no literal for at all.\n\n"
         "The ten cover addresses as a four-verb set, reading the current customer, the existence probe a signup makes\n"
         " before registering, guest registration, login and registration proper, and sending a verification code.\n"
         " Checking first, as section 2.7c requires, found no /customer/v1 literal anywhere in the source; the customer\n"
         " reference in ScapiEndpoints.cs is Salesforce Commerce API and unrelated.\n\n"
         "The measurement moved for the first time since R892. The hostless bucket goes from forty-six of sixty-seven\n"
         " to fifty-six, sixty-eight point seven percent to eighty-three point six, total missing from a hundred and\n"
         " five to ninety-five, and the suite from 1790 to 1796. Five rounds of measurement work before this had moved\n"
         " no product code at all.\n\n"
         "The ownership label differs from Vans's in a way worth keeping visible. Vans's paths share literals with their\n"
         " host, so OwnershipIsInference is false and the ownership is observed. None of these ten shares a literal with\n"
         " any host, so OwnerIsUnknown is true: the endpoints are observed and the owning store is not. Constants are\n"
         " legitimate at that strength because a path is an observation; a step would not be, because the body, the\n"
         " response, the authentication scheme and the caller are all absent.\n\n"
         "Six tests pin it, two of them deliberately awkward. One asserts the unknown-owner flag so a future round that\n"
         " finds co-occurrence has to flip it and say so. The other asserts the list is ordered for use rather than\n"
         " alphabetically, by checking the first entry is the existence probe and that the whole list differs from its\n"
         " own sort, so the ordering stays a claim rather than an accident.\n\n"
         "Unknown: which store owns these ten; the four missing facts per path, which is why nothing calls them; how\n"
         " many of the remaining ninety-five are likewise whole families, since the verbose list still holds\n"
         " commerce/v1, product-core/v1 and legacy/v1 at two paths each; and what shield/v1/verify_otp does, which the\n"
         " name suggests is an OTP check belonging to a protection service and therefore to the anti-bot priority.\n\n"
         "The lesson is the one R901 named, now with a number attached: run the measurement until it can produce a\n"
         " list, then stop measuring and start adding. Ten constants moved three figures; the five rounds before them\n"
         " moved none.\n\n"
         "Product code changed, ten constants and six tests; suite green at 1796."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))


if __name__ == "__main__":
    main()
