"""Record R785: the Casio field clusters split into product and account surfaces."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 211. Casio 的五个字段分成**两簇**：商品面与账户面

> R785。未改产品代码。

### 一、五条字段的引用者（Observation）

```
casio_can_purchase   1  sub_140954410 (0x84a = 2,122 B)
casio_image_url      1  sub_140954410
casio_dob            1  sub_140948FA0 (0x2c9 = 713 B)
casio_gender         1  sub_140948FA0
casioid              2  sub_14094AF90 (0xbb) · sub_140952790 (0x37d)
```

**两簇，界限很清楚：**

| 簇 | 字段 | 函数 |
|---|---|---|
| **商品面** | `casio_can_purchase` · `casio_image_url` | `sub_140954410`（与 R781 那条 `data.products.items` 路径同一个） |
| **账户面** | `casio_dob` · `casio_gender` | `sub_140948FA0`（713 B，另一个函数） |
| 标识 | `casioid` | 取值 + 构造 |

### 二、这说明什么

**`casio_dob`（生日）与 `casio_gender`（性别）同处一个函数** ——
**那是账户/注册数据的形状，不是商品的。** 商品不会有生日。

**而 R780 的池子里还有 `Casio Login` 与 `CasioRegion`。**

**合起来：镜像的 Casio 集成有**：

1. **分区**（`CasioRegion`、AU/SG/US）
2. **登录**（`Casio Login`）
3. **注册/账户字段**（`casio_dob`、`casio_gender`）
4. **商品字段**（`casio_can_purchase`、`casio_image_url`、`casioid`）
5. **Adyen 支付字段**（`_adyenOrderId`）

**而复刻件的 `CasioFlow` 只有商品 + 购物车 + 一个恒失败的提交。**
**登录、注册、分区三样都没有。**

### 三、为什么不改代码

`CasioFlow` 没有 `LoginAsync`。**要加，就得知道往哪发** ——
而 `casio_dob` / `casio_gender` 是**字段名**，与 `_adyenOrderId` 一样，**不是端点**。

**R780 已经在这个坑里栽过一次**（把字段名当端点）。**这一轮不重犯。**

### 四、真正卡住的是同一件事

`CasioFlow.AddToCartAsync` 里那句注释已经写对了：

> `casio: /cart/add is not there — Casio runs AEM behind Akamai, and every root-relative cart path
> returns the SPA 404; the real path is under the /{region}/ prefix and has not been captured`

**`/{region}/` 这个前缀就是分区。** 而 `CasioRegion` 零 xref（R781）说明它是**设置项、按名字读**。

**所以要做 Casio 的登录/注册/加购/支付，四件事卡在同一个缺口上：**

> **区域 token 的取值与它在前缀里的拼法。**

**拿到那个，四件事一起可做；拿不到，一件都做不了。**

### 五、验证

```
本轮未改产品代码
完整套件保持 1761 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **区域 token 的取值与 URL 拼法**：**Unknown —— 四件事的共同前置。**
- `sub_140948FA0`（713 B）除 `dob`/`gender` 外还读什么：**Unknown**。
- `casioid` 是商品 id 还是变体 id：**Unknown**（R783，仍未解）。
- Casio 登录端点的形状：**Unknown**。
"""

VERDICT = """

---

## 第 785 轮：Casio 的字段分成商品面与账户面

### 引用者

```
casio_can_purchase · casio_image_url   -> sub_140954410 (2,122 B)
casio_dob · casio_gender               -> sub_140948FA0 (713 B)
casioid                                -> 取值 (187 B) + 构造 (893 B)
```

**`dob` + `gender` 同处一个函数 —— 商品不会有生日。那是账户/注册面。**

### 于是镜像的 Casio 集成有五块

分区 · 登录 · 注册字段 · 商品字段 · Adyen 支付字段。

**而复刻件的 `CasioFlow` 只有商品 + 购物车 + 一个恒失败的提交。**
**登录、注册、分区三样都没有。**

### 为什么不改代码

`CasioFlow` 没有 `LoginAsync`，**要加就得知道往哪发**，
而 `casio_dob` / `casio_gender` **和 `_adyenOrderId` 一样是字段名，不是端点。**
**R780 已在这个坑里栽过，这轮不重犯。**

### 四件事卡在同一个缺口

`AddToCartAsync` 的注释已经写对了：**真实路径在 `/{region}/` 前缀下，未抓到。**

**登录 / 注册 / 加购 / 支付 —— 四件事一起卡在「区域 token 的取值与拼法」上。**
**拿到那个，四件一起可做；拿不到，一件都做不了。**

### 验证

```
产品代码未改；套件 1761 / 0；度量未变
```
"""

BACKLOG_ADD = """

## 核心 — Casio 的共同前置（R785）

**镜像的 Casio 集成有五块**，复刻件只有商品一块：

| 面 | 原版证据 | 复刻件 |
|---|---|---|
| 分区 | `CasioRegion` · AU/SG/US · `/{region}/` 前缀 | ❌ |
| 登录 | `Casio Login` | ❌ 无 `LoginAsync` |
| 注册字段 | `casio_dob` · `casio_gender`（同一函数 `sub_140948FA0`） | ❌ |
| 商品字段 | `casio_can_purchase` · `casio_image_url` · `casioid` | ✅ 已用（R782/R784） |
| Adyen 支付 | `_adyenOrderId` | ❌ 端点未知 |

**四件事（登录/注册/加购/支付）卡在同一个缺口**：

> **区域 token 的取值，以及它在前缀里的拼法。**

`CasioRegion` 零 xref = **设置项，按名字读**。`AU`/`SG`/`US` 是显示名，**token 本身未知**。

| 项 | 状态 |
|---|---|
| 区域 token 与拼法 | **Unknown —— 最高优先的前置** |
| `sub_140948FA0` 其余读取 | Unknown |
| `casioid` 商品 id / 变体 id | Unknown |
| 登录端点形状 | Unknown |

**纪律提醒**：`casio_dob` / `casio_gender` / `_adyenOrderId` 都是**字段名**。
**R780 把字段名当端点栽过一次，不要再犯。**
"""


def main():
    for p, marker, text in ((P1, "R785", BLOCKER), (P3, "R785", BLOCKER), (P2, "第 785 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R785" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += Casio 共同前置")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R785: Casio's fields split into a product surface and an account surface\n\n"
         "Cross-referencing the five Casio field names sorts them into two clusters with no overlap.\n"
         "casio_can_purchase and casio_image_url both land in sub_140954410, the same function that walks\n"
         "data.products.items. casio_dob and casio_gender both land in sub_140948FA0, a separate 713-byte function.\n"
         "casioid has two readers, the keyed lookup and the object builder.\n\n"
         "The split is informative because a product has no date of birth. dob and gender together describe an\n"
         "account. So the image's Casio integration has five parts: a region selector, a login, registration fields,\n"
         "product fields, and an Adyen payment field. The replica has the product part and a cart call; it has no\n"
         "login, no registration and no region.\n\n"
         "None of that justifies code this round. CasioFlow has no LoginAsync, and adding one requires knowing where\n"
         "to post -- but casio_dob and casio_gender are field names, exactly like _adyenOrderId, not endpoints. R780\n"
         "made that mistake once already by counting a field name as a checkout URL; not again.\n\n"
         "What the round does establish is that four separate pieces of work are blocked on one thing. The comment\n"
         "already in AddToCartAsync states it correctly: the real cart path sits under a /{region}/ prefix and has not\n"
         "been captured. CasioRegion has no cross-references because it is a setting read by name, and AU, SG and US\n"
         "are display names rather than the tokens the URL needs. With the region token and its spelling, login,\n"
         "registration, cart and payment all become buildable together; without it, none of them are.\n\n"
         "No product code changed; suite remains 1761 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
