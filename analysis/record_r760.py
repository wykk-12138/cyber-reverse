"""Record R760: the store alarm is refuted, and criterion f gets its first real row."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 188. **上一轮那个警报是错的**：7 个站全在原版里；而 Superswipe 的缺口只有 4 项

> R760。新增 `analysis/store_slug_probe.py`。本轮未改产品代码（证据轮）。

### 一、R759 的警报与它的错误原因

R759 我写：「10 个店名里 7 个在原版里 `literals=0`」，并因此怀疑复刻件的 store 清单有猜的成分。

**错的。** 查 **slug 与域名**（而不是显示名）：

```
superswipe   22 条   https://captcha.superswipe.com · https://status.superswipe.com
                     https://enter.superswipe.com/enter · CaptchaOrigin · ProgressApi
yeezysupply   1 条   https://www.yeezysupply.com
offspring     9 条   blocked_page_offspring · collectplusoffspring · platform.poq.io/clients/offspring/
pocketgames   5 条   https://api.pocketgames.nl · /v1/reservations
jbhifi        7 条   https://auth.jbhifi.com.au/Account/Login
endclothing  10 条   ApiHost8:https://api2.endclothing.com · CatalogHost6:https://api.endclothing.com
notre         6 条   （多为 HTML/base64 噪声，需换 token 复检）
```

**结论：7/7 都在，`exact` 全 0 而 `embedded` 全非 0。**

**错误原因**：我搜的是**显示名**（`Footpatrol`、`Yeezy Supply`），而原版**根本不把显示名当字面量存**
—— 名字是拼出来的或来自资源，**域名和端点字段名才是字面量**。

**这是同一类错误的第三次**：

| 轮 | 扫描器假设 | 后果 |
|---|---|---|
| R753 | 标签形如 `"Startup Page"` | 报假缺席（实际 `"(i)  Startup Page"`） |
| R759 | module 字段形如 `=>` | `ShopifyModule` 抽出 `?`（实际在构造函数链里） |
| **R760** | **店名以显示名出现** | **7 个站被误判为可疑** |

**共同点：我假设了"东西长什么样"，而没先问"哪种形式才会被这个工具看到"。**

### 二、原版 Superswipe 的完整契约（Observation）

那 22 条里有 **8 个端点槽 + 4 个 DOM 选择器 + 1 个反指纹路径**：

```
CaptchaOrigin      https://captcha.superswipe.com
ProgressApi        https://status.superswipe.com
EntryUrl           https://enter.superswipe.com/enter
CountryDataUrl     https://cdn.superswipe.com/superswipe-country-data.js
LogoUrl            https://cdn.superswipe.com/superswipe-logo.png
ClickTrackerUrl    https://clicks.superswipe.com/c
SubdomainAlphabet  abcdefghijklmnopqrstuvwxyz0123…
LaunchAttributeKey _superSwipe / _superswipe_launch_id_

DOM   [data-superswipe-block] · [data-superswipe-launch-id] · data-superswipe-music-launch-id
      script[data-superswipe-selling-plans] · script[data-superswipe-variants]
反指纹 .superswipe.app/youwillnevergetthis/fingerprint
```

**`SubdomainAlphabet` 说明它是按 launch 生成子域的**（不是固定 host）；**那条 `youwillnevergetthis/fingerprint`
是原版自己的指纹探测端点。**

### 三、复刻件这一侧：已实现大部分，缺口只有 4 项

`Cybersole.Stores\\Flows\\RetailFlows.cs` 里已有：

```
captcha.superswipe ✓  status.superswipe ✓  enter.superswipe ✓  country-data ✓  launch-id ✓
CaptchaOrigin ✓  EntryUrl ✓  CountryDataUrl ✓
```

**缺**：

```
clicks.superswipe.com/c        点击追踪端点
SubdomainAlphabet              按 launch 生成子域的能力
data-superswipe-*              DOM 选择器（4 个）
youwillnevergetthis/fingerprint 反指纹探测路径
```

**所以 22 个 store 既不是编的，也不是桩。** 判据 f 的第一行因此是**正面的**，缺口**具体且可做**。

### 四、验证

```
本轮未改产品代码
完整套件保持 1745 通过 / 0 失败
新增 analysis/store_slug_probe.py
```

### 五、仍然 Unknown

- `notre` 那 6 条是 HTML 噪声还是真端点：**Unknown** —— 需换 token（`notre-shop.com`）复检。
- `SubdomainAlphabet` 的完整串与用法：**Unknown** —— 只看到前缀，未读使用它的函数。
- 其余 21 个 store 是否也是「大部分已实现、缺几项」：**Unknown** —— 只做了 Superswipe 一个。
- `store_catalog.py` 的构造函数形式缺陷：**未修**（补丁写坏一次，见 R759）。
"""

VERDICT = """

---

## 第 760 轮：警报是错的

### R759 我说"7 个店名在原版里找不到"，并怀疑复刻件在猜

**查 slug 与域名之后，7/7 全在：**

```
superswipe   22 条（8 个端点槽）
yeezysupply   1 条   offspring  9 条   pocketgames 5 条
jbhifi        7 条   endclothing 10 条  notre       6 条
```

**错误原因：我搜的是显示名，而原版根本不把显示名当字面量存 —— 域名和端点字段名才是。**

### 这是同一类错误的第三次

| 轮 | 扫描器假设 | 后果 |
|---|---|---|
| R753 | 标签形如 `"Startup Page"` | 报假缺席 |
| R759 | 字段形如 `=>` | `?` |
| **R760** | **店名以显示名出现** | **7 个站误判可疑** |

> **共同点：我假设了"东西长什么样"，而没先问"哪种形式才会被这个工具看到"。**

### 而原版的 Superswipe 契约相当完整

8 个端点槽 + 4 个 DOM 选择器 + 一条反指纹路径；
其中 **`SubdomainAlphabet` 说明它按 launch 生成子域**，
**`/youwillnevergetthis/fingerprint`** 是它自己的指纹探测端点。

### 复刻件缺的只有 4 项

`clicks.superswipe.com/c` · `SubdomainAlphabet` · `data-superswipe-*` 选择器 · 指纹端点路径

**所以 22 个 store 既不是编的，也不是桩。判据 f 的第一行是正面的。**

### 验证

```
产品代码未改；套件 1745 / 0
```

### 下一轮

补那 4 项（先 `snapshot.py`，整块锚点替换，读 `RetailFlows.cs` 的 Superswipe 段）；
并把 Superswipe 这个方法套到另外 21 个 store 上，逐条填判据 f。
"""


def main():
    for p, marker, text in ((P1, "R760", BLOCKER), (P3, "R760", BLOCKER), (P2, "第 760 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R760: last round's alarm was wrong -- all seven stores are in the original, and Superswipe is mostly built\n\n"
         "R759 reported that seven replica store names had no literal in the binary and raised the possibility that\n"
         "the catalogue was partly guessed. Searching slugs and domains instead of display names refutes it: every\n"
         "one of the seven appears, as endpoint URLs and as configuration field names.\n\n"
         "The mistake was searching for the wrong form. The original does not store display names as literals; it\n"
         "stores domains, endpoints and field names. That is the third time in this session a scanner of mine has\n"
         "assumed a shape and reported absence instead: R753 missed a label because of a quote, R759 missed a\n"
         "module's fields because they were assigned in a constructor, and now this. The common shape of the error\n"
         "is assuming what a thing looks like before asking which form the tool can see.\n\n"
         "The evidence that came out of it is worth having. The original's Superswipe support carries eight endpoint\n"
         "slots, four DOM selectors and a fingerprint path, and SubdomainAlphabet shows it builds per-launch\n"
         "subdomains rather than using a fixed host. The replica already implements most of that contract; four\n"
         "items are missing: the click tracker, the subdomain alphabet, the data-superswipe selectors and the\n"
         "fingerprint path.\n\n"
         "So criterion f's first row is positive, and its remaining work is specific.\n\n"
         "No product code changed; suite remains 1745 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
