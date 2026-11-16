"""Record R778: the Poq app identity spec is complete."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 204. Poq App 身份**规格齐了**：13 个头全部有名字，10 个有值，3 个是动态的

> R778。新增 `analysis/poq_header_values.py`。未改产品代码。

### 一、完整规格（Observation）

```
header                    value
------------------------- ------------------------------------
user-agent                Poq-Native-iOS-App
accept                    application/json
accept-language           nl-NL,nl;q=0.9
accept-encoding           gzip, deflate, br
authorization             "Bearer " + <token>            （动态）
version-code              26.0
platform                  iphone
poq-app-id                275
poq-app-identifier        a1dad595-7431-45bc-9fb9-684dac169b5b    （36 字符 GUID）
poq-country-identifier    <对象链取值>                   （动态）
poq-currency-identifier   <sub_140B399B0(a1)>            （动态）
poq-user-id               <a1[24]>                       （动态）
poq-slot-conditions       <名字已确认，值所在构造器未定位>
```

**10 个是常量、3 个是运行时取值**（country / currency / user-id），另有 `poq-slot-conditions` 的取值未定位。

### 二、两个值得单独说的

1. **`poq-app-identifier` 是一个 GUID**：`a1dad595-7431-45bc-9fb9-684dac169b5b`。
   **这像是 App 的客户端标识**，不是站点键。**它是常量，所以可以直接照抄。**
2. **`accept-language` 是 `nl-NL,nl;q=0.9`** —— **荷兰语**。
   **这可能是某个区域的默认值，也可能是一个写死的值。** 我不把它当作"所有任务都用荷兰语"，
   **标为 Inference（低）：这是该构造器里的字面量，但它是否被其它区域覆盖，Unknown。**

### 三、又一次 off-by-12（第四次）

`poq-slot-conditions` 第一次读成 `'ot-conditions'` —— 因为我把 R774 记的 **chars 地址**
（`0x1471152dc`）当成了**对象地址**。对象是 `0x1471152d0`，读出来就是 `'poq-slot-conditions'` len=19。

**第四次栽在同一处：NativeAOT 里"字符地址"和"对象地址"差 12。**
R720 立的规则是"代码 `lea` 的是对象头"，而我这轮从**字符串池的字符地址**反过来推对象时忘了减 12。
**两个方向都要记住：从代码往字符串走 +12，从字符往对象走 −12。**

### 四、验证

```
off_slot_reader.py 校准通过（off_1471151D0 -> 'poq-app-id'，长度一致）
poq_header_values.py 输出上表
本轮未改产品代码；完整套件保持 1752 通过 / 0 失败
```

### 五、仍然 Unknown

- 三个动态值的**具体语义**：country 来自对象链、currency 来自 `sub_140B399B0(a1)`、user-id 是 `a1[24]`
  —— **三者都是会话数据，不是常量，所以"读出来"本来就不适用。**
- `poq-slot-conditions` 的**取值**：**Unknown** —— 名字确认了，值所在的构造器未定位。
- **`nl-NL` 是否被区域覆盖**：**Unknown**。
- **触发 App 面的任务类型**：**Unknown**（R775）。

### 六、下一步

**规格够了，可以建那个 flow 单元了。** 单位仍是 R775 定的：
**App 面一个 flow（身份 + 四个 action + 一个注册项）**，不是只建常量。
三个动态值在 flow 里从会话取，**不照抄** —— 照抄就是把常量冒充成运行时数据。
"""

VERDICT = """

---

## 第 778 轮：规格齐了

| header | value |
|---|---|
| user-agent | `Poq-Native-iOS-App` |
| accept | `application/json` |
| accept-language | `nl-NL,nl;q=0.9` |
| accept-encoding | `gzip, deflate, br` |
| authorization | `"Bearer "` + token（动态） |
| version-code | `26.0` |
| platform | `iphone` |
| poq-app-id | `275` |
| poq-app-identifier | `a1dad595-7431-45bc-9fb9-684dac169b5b` |
| poq-country-identifier / currency / user-id | 动态 |
| poq-slot-conditions | 名字确认，取值未定位 |

**10 常量 + 3 动态。**

### 两个值得单独说的

- **`poq-app-identifier` 是个 GUID** —— 像 App 的客户端标识，**常量，可照抄**。
- **`accept-language` 是荷兰语 `nl-NL,nl;q=0.9`** —— 可能是区域默认值，也可能写死。
  **标 Inference（低）：它是否被其它区域覆盖，Unknown。**

### 又一次 off-by-12（第四次）

`poq-slot-conditions` 先读成 `'ot-conditions'` —— 我把 R774 的 **chars 地址**当成了**对象地址**。
对象要 −12。

**两个方向都要记住：代码→字符串 +12；字符→对象 −12。**

### 验证

```
校准通过；套件 1752 / 0；产品代码未改
```

### 下一步

**规格够了，可以建 flow 单元**（身份 + 四动作 + 注册项）。
**三个动态值从会话取，不照抄** —— 照抄就是把常量冒充成运行时数据。
"""

BACKLOG_ADD = """

## App 面 — 规格已齐（R778），可以建 flow

```
user-agent Poq-Native-iOS-App · accept application/json · accept-encoding gzip, deflate, br
accept-language nl-NL,nl;q=0.9 · version-code 26.0 · platform iphone
poq-app-id 275 · poq-app-identifier a1dad595-7431-45bc-9fb9-684dac169b5b
authorization "Bearer "+token · poq-country-identifier · poq-currency-identifier · poq-user-id   ← 动态
poq-slot-conditions   名字确认，取值未定位
```

**构建单位**：App 面一个 flow（身份 + 四动作 + 注册项）。**不要只建常量**（R772 的教训）。

| 项 | 状态 |
|---|---|
| 三个动态值 | 从会话取，**不照抄** |
| `poq-slot-conditions` 取值 | Unknown |
| `nl-NL` 是否被区域覆盖 | Unknown |
| 触发它的任务类型 | Unknown |

**地址规则（第四次踩）**：从代码往字符串走 **+12**；从字符往对象走 **−12**。
`off_slot_reader.py` 只接受**对象地址**。
"""


def main():
    for p, marker, text in ((P1, "R778", BLOCKER), (P3, "R778", BLOCKER), (P2, "第 778 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R778" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += 规格已齐")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R778: the Poq app identity spec is complete -- ten constants, three dynamic, one value unlocated\n\n"
         "The calibrated reader turns the header set into a spec. Ten headers carry constants: the user agent\n"
         "Poq-Native-iOS-App, accept application/json, accept-encoding gzip deflate br, accept-language\n"
         "nl-NL,nl;q=0.9, version-code 26.0, platform iphone, poq-app-id 275, and poq-app-identifier, which turns out\n"
         "to be a GUID, a1dad595-7431-45bc-9fb9-684dac169b5b. Three are runtime values rather than constants --\n"
         "country from an object chain, currency from sub_140B399B0, and user id from a1[24] -- and reading a\n"
         "constant was never going to work for those, so they are recorded as dynamic rather than unresolved.\n\n"
         "Two deserve a note. The app identifier being a GUID suggests a client identifier rather than a site key,\n"
         "and being constant it can be used directly. The accept-language value is Dutch, which may be a regional\n"
         "default or may be fixed; I am not treating it as 'every task speaks Dutch' and have marked it inferred-low\n"
         "with the override question unknown.\n\n"
         "The fourth off-by-twelve of the session: poq-slot-conditions first read as 'ot-conditions' because I took\n"
         "the character address recorded in R774 for the object address. The object is twelve bytes earlier, and\n"
         "then it reads correctly at length nineteen. R720 established that code leas the object header, so going from\n"
         "code to string means adding twelve; going from a pool character address back to an object means subtracting\n"
         "it. Both directions need holding in mind, and the reader only accepts object addresses.\n\n"
         "With the spec this complete the app-surface flow can be built as R775 scoped it -- identity, four actions,\n"
         "one registry entry. The three dynamic values should come from the session rather than being copied in, since\n"
         "copying them would present runtime data as constants.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
