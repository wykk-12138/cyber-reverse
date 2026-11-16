"""Record R761: store metadata is data, the endpoint table, and the one real vendor gap."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"

BLOCKER = """

---

## 189. 判据 f 的取法终于对了：**store 元数据是数据不是代码**；端点全覆；**唯一真缺口是 Forter**

> R761。新增 `analysis/store_records.py`。本轮未改产品代码（证据轮）。

### 一、四次尝试，前三次都错在"找的地方不对"

| 轮 | 方法 | 结果 |
|---|---|---|
| R757 | 源码里的子串计数 | 把步骤名（`supreme-add`）当成 store |
| R759 | 顺着 store 基址 URL 的 xref | 落进该模块的**异步状态机** |
| R759 | 多个店名求交 | 落在 `sub_14117C4E0`，**687 KB，不是函数** |
| **R761** | **按字段名找配置记录** | **对** |

**为什么前三次错**：原版把 store 与服务的元数据存成**数据记录**（字段名 + 分隔字节 + 值连写），
**代码按字段名读**，所以**没有可追的 xref**。

```
CaptchaOrigin<https://captcha.superswipe.com
ProgressApi:https://status.superswipe.com
EntryUrlDhttps://enter.superswipe.com/enter
ClickTrackerUrl>https://clicks.superswipe.com/c"SubdomainAlphabetHabcdefghijklmnopqrstuvwxyz0123456789
```

`<` `:` `D` `>` `"` `H` 这些单字节是**长度/分隔**，不是内容。

### 二、由此得到原版自己的服务端点表（16 对，Observation）

```
TelemetryHost    https://telemetry.cybersole.io
EndpointUrl      https://analytics.cybersole.io
WebHost          https://cybersole.io
SolverUrl        https://cf-solver.cybersole.io        ← 自建 Cloudflare solver
BaseUrl          https://api.humanpresence.io/v2       ← Human Presence（反机器人）
RaffleUrl        https://r419.com/  +  _turnstileSiteKey
StripeJsOrigin   https://js.stripe.com + _stripePublishableKey, _stripePaymentMethodId
SquareHost       https://pci-connect.squareup.com + SquareApplicationId: sq0idp-…
UnzerApiHost     https://api.unzer.com
CheckoutHost     https://checkout.johnlewis.com
CheckoutPage     https://checkout-page.omise.co/
```

**复刻件对这些的覆盖：全部有。**
`HumanPresence` 36 处（`Drivers.cs`）· `cf-solver` 12 · `r419.com` 4 · `Turnstile` 50 ·
Stripe 84 / Square 7 / Unzer 17 / Omise 33 · 遥测两个宿主各 4（`CybersoleHosts.cs`、`SessionTelemetry.cs`）。

### 三、**唯一真正的厂商缺口：Forter**，而且另外两个是我猜出来的假项

R757 我按通用风控知识写了三个"缺"：`forter` / `funcaptcha`(Arkose) / `arkoselabs`。核完：

| 厂商 | 原版 | 复刻件 |
|---|---|---|
| **Forter** | **真集成** | **零** |
| funcaptcha | **原版里根本没有**（`str funcaptcha` → no match） | 零 |
| arkose | **原版里根本没有** | 零 |

**Forter 在原版里的形态**（Observation）：

```
Forter                      ← 一个枚举成员（名 + 长度 11）
ForterEnvelope
ForterEventsEncoder
get_ForterEnvelope
Create_ForterEnvelope
```

**`Envelope` + `EventsEncoder` 是 Forter 反欺诈 SDK 的典型协议形状**（传感器数据打封装、事件编码上报）。
**这是可复刻的具体目标，不是模糊的"要做风控"。**

**而 `funcaptcha` / `arkose` 两条要撤回**：原版没有，复刻它没有意义。
**这正是"子串计数只当地图不当判据"那条纪律的反面教材 —— 我当时把它当成了判据。**

### 四、`store_records.py` 的局限（写清）

它找到的是**服务端点**，**没有**给出每个 store 的完整记录 —— 因为多数 store 的记录里**没有 URL**，
而我的模式要求 name 后面跟 URL。所以：

- **判据 f 的左半边仍不完整**：拿到了**服务/厂商清单**，**没拿到 store 清单**。
- 下一步要么放宽模式（接受更多值形态），要么换成"按记录起点分组 + 用域名锚定"。

### 五、验证

```
本轮未改产品代码
完整套件保持 1745 通过 / 0 失败
新增 analysis/store_records.py（有效，但有上述局限）
```

### 六、仍然 Unknown

- 完整的 **store** 记录集：**Unknown** —— 见第四节。
- `ForterEnvelope` 的实际字段与编码方式：**Unknown** —— 未反编译，只看到符号。
- `subdomainAlphabet` 的**用法**：**Unknown** —— 记录里给了字母表，但用法无 xref 可追。
- `notre` 的 6 条命中是否噪声：**未知**（R760 记，未复检）。
"""

VERDICT = """

---

## 第 761 轮：store 元数据是数据不是代码

### 四次尝试，前三次错在"找的地方不对"

| 轮 | 方法 | 结果 |
|---|---|---|
| R757 | 源码子串计数 | 把步骤名当 store |
| R759 | store 基址的 xref | 落进异步状态机 |
| R759 | 多店名求交 | 687 KB 的 IDA 并片 |
| **R761** | **按字段名找配置记录** | **对** |

**原版把元数据存成数据记录**（字段名 + 分隔字节 + 值连写），**代码按字段名读**，所以没有可追的 xref。

### 由此拿到端点表，而复刻件全覆盖

`HumanPresence` 36 · `cf-solver` 12 · `Turnstile` 50 · Stripe 84 · Unzer 17 · Omise 33 · 遥测 4×2 —— **全有。**

### 唯一真缺口：Forter

```
ForterEnvelope · ForterEventsEncoder · get_ForterEnvelope · Create_ForterEnvelope · Forter（枚举成员）
```

**`Envelope` + `EventsEncoder` 是 Forter 反欺诈 SDK 的典型形状。可复刻的具体目标。**

### 而另两个"缺"是我猜的

`funcaptcha` / `arkose` —— **原版里根本没有**。**撤回。**

> **这正是"子串计数只当地图不当判据"的反面教材：我当时把通用风控知识当成了判据。**

### `store_records.py` 的局限（写清）

它给的是**服务端点**，**没给 store 清单** —— 多数 store 记录里没有 URL。
**所以判据 f 的左半边：厂商/服务部分完成，store 部分仍未完成。**

### 验证

```
产品代码未改；套件 1745 / 0
```

### 下一轮

反编译 `ForterEnvelope` / `ForterEventsEncoder`，按形状在复刻件里建对应物 —— **这是第一个有明确名字的风控缺口**。
"""


def main():
    for p, marker, text in ((P1, "R761", BLOCKER), (P3, "R761", BLOCKER), (P2, "第 761 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R761: store metadata is data, not code -- the endpoint table, and Forter as the one real gap\n\n"
         "Three earlier approaches to the original's store list were wrong in the same way: they looked for\n"
         "code. R757 counted substrings and conflated step names with stores; R759 followed a store's base URL\n"
         "into that module's async state machine; R759's intersection of store-naming functions landed on a\n"
         "687 KB IDA blob. The fourth attempt works because the original keeps this metadata as data records --\n"
         "field name, one separator byte, value -- which code reads by name, so there is no xref to follow.\n\n"
         "That yields sixteen field-value pairs naming the app's own services: telemetry and analytics hosts, a\n"
         "self-hosted Cloudflare solver at cf-solver.cybersole.io, humanpresence.io, r419.com with a Turnstile\n"
         "site key, and the payment providers Stripe, Square, Unzer and Omise. The replica covers every one of\n"
         "them.\n\n"
         "Forter is the exception and the only real vendor gap: the original carries ForterEnvelope,\n"
         "ForterEventsEncoder and their accessors, plus a Forter enum member, while the replica has no reference\n"
         "at all. An envelope plus an events encoder is Forter's fraud-sensor shape, which makes this a concrete\n"
         "target rather than 'do something about risk control'.\n\n"
         "Two items from R757 are retracted. funcaptcha and arkose do not appear in the original at all, so\n"
         "there is nothing to replicate; I had inferred them from general bot knowledge and treated that guess\n"
         "as a criterion, which is exactly what the substring-is-a-map rule warns against.\n\n"
         "The script's limitation is recorded: it recovers service endpoints, not per-store records, because most\n"
         "store records carry no URL. Criterion f's vendor half is done; its store half is not.\n\n"
         "No product code changed; suite remains 1745 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
