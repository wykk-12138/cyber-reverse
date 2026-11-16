"""Record R776: the header set I can evidence, and the six I cannot -- with the reason."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 202. App 身份的**可证据部分**，以及六个读不出来的头名（附确切原因）

> R776。未改产品代码。

### 一、能证据的（Observation）

```
User-Agent            Poq-Native-iOS-App          (0x146e46694)
poq-app-id            (0x1471151dc)
poq-app-identifier    (0x14711520c)
poq-country-identifier(0x14711524c)
poq-currency-identifier(0x147115294)
poq-slot-conditions   (0x1471152dc)
poq-user-id           (0x14711531c)
```

端点（R771/R775）：

```
platform.poq.io/clients/offspring/{products?ids=, cart/items, checkout/start, account/guest-token}
platform.poq.io/clients/office/{AtaVerifyCaptcha, recaptcha?trackingId=}
```

### 二、读不出来的六个，以及**为什么**

`sub_140B3B7C0` 里对每个头调用一次 `sub_1408BAD40(容器, 键, 值)`，键形如 `&off_147115240`。
**共 12 个这样的槽位，我只能解出其中 6 个（就是上面那族 `poq-*`）。**

尝试与失败经过：

| 尝试 | 结果 |
|---|---|
| 把 `off_x` 当作字符串对象头，直接读到 +12 | **读回乱码** |
| 用 `pe_strings.txt` 按地址过滤 | **它记的是文件偏移，不是虚拟地址** |
| 自己解析 PE 节表做 VA→文件偏移换算 | 换算本身对了（`.data` RVA 0x6a47000 / raw 0x6a45c00），**但读出来仍是同一串乱码** |

**原因**：`off_x` **不是字符串对象，是静态槽位的地址** —— 槽里存着**指向**字符串对象的指针，
且那个指针**受重定位影响**（文件里是未重定位值）。

**这与本会话早前记过的一次是同一件事**：当时发现「四个 `off_14492xxxx` 槽位读回同一个不合理长度，
不是字符串指针，是某种描述符」。**这是第三次撞上 `off_` 家族**，我仍然没有把它写成一个可复用的读取器。

**所以那六个头名是 Unknown，不是"没有"。** 我不拿猜测填它们 —— 按项目纪律，
**猜出来的头名会把后面每一个读这段代码的人带偏。**

### 三、这一轮没有代码，理由仍然成立

R775 已经定下：**构建的单位是「App 面一个 flow」（身份 + 四步 + 注册项），不是身份常量。**
**身份本身现在也只证据了 7/13 项**（UA + 6 头，另有 6 头 + 各头取值 Unknown）。
**在这个完整度上开工，等于建一个半懂的东西。**

### 四、验证

```
本轮未改产品代码
完整套件保持 1752 通过 / 0 失败
```

### 五、仍然 Unknown

- **六个头的名字**：**Unknown**，原因见第二节（`off_` 是槽位不是对象；需解引用 + 重定位）。
- **所有头的取值**：**Unknown** —— 反编译里取值来自 `sub_141CF6230(&off_146B5C780, a1[29])`
  与 `sub_140B399B0(a1)`，两者的返回值语义未读。
- **触发 App 面的任务类型**：**Unknown**（R775）。
- 四个头部构造器为何是四个：**Unknown**。

### 六、下一步该先做的（比我原来的计划更靠前）

**写一个 `off_` 槽位读取器**：读槽 8 字节 → 判断是 VA 还是 RVA → 加 imagebase → +12 → 读 UTF-16。
**没有它，这一族的每一个键都得手工试一遍**，而这一族在原版里到处都是。
**这是工具债，不是这一轮的任务，但它挡着后面好几轮的路。**
"""

VERDICT = """

---

## 第 776 轮：七项证据，六项读不出来，原因写清了

### 能证据的

```
User-Agent             Poq-Native-iOS-App
poq-app-id · poq-app-identifier · poq-country-identifier
poq-currency-identifier · poq-slot-conditions · poq-user-id
+ 4 个 offspring action，2 个 office action
```

### 读不出来的六个

`sub_140B3B7C0` 对每个头调 `sub_1408BAD40(容器, 键, 值)`，键形如 `&off_147115240`，**共 12 个槽位，只解出 6 个。**

| 尝试 | 结果 |
|---|---|
| 当作字符串对象头直接读 +12 | **乱码** |
| `pe_strings.txt` 按地址过滤 | 它记的是**文件偏移** |
| 自己解析 PE 节表换算 VA→文件偏移 | 换算对了，**读出来还是乱码** |

**原因：`off_x` 不是字符串对象，是静态槽位的地址，槽里存着指向对象的指针，且受重定位影响。**

**本会话第三次撞上 `off_` 家族** —— 前两次是「四个槽位读回同一个不合理长度」。
**我仍然没把它写成可复用的读取器。**

**六个头名是 Unknown，不是"没有"。不拿猜测填。**

### 没有代码，理由仍成立

构建单位是「App 面一个 flow」，**而身份本身只证据了 7/13 项**。**在这个完整度开工，等于建一个半懂的东西。**

### 下一步（比我原计划更靠前）

**写一个 `off_` 槽位读取器**：读槽 8 字节 → 判断 VA/RVA → 加 imagebase → +12 → 读 UTF-16。
**这一族在原版里到处都是，没有它每个键都要手工试一遍 —— 这是工具债。**
"""

BACKLOG_ADD = """

## 工具债 — `off_` 槽位读取器（R776，优先于 App flow）

**问题**：Hex-Rays 里 `&off_XXXX` 是**静态槽位的地址**，槽里存着指向字符串对象的指针，**且受重定位**。
直接读到的是槽内容，不是字符串。

**已证据的错误路径**：① 当对象头读 +12 → 乱码；② `pe_strings.txt` 是文件偏移；
③ 自己换算 VA→文件偏移（`.data` RVA 0x6a47000 / raw 0x6a45c00）→ 仍乱码。

**要做**：读槽 8 字节 → 判断 VA 还是 RVA → 加 imagebase → +12 → 读 UTF-16LE。

**为什么优先**：`off_` 家族在原版里到处都是；这次挡住的是 Poq 六个头名，
**下一次会挡别的东西**。**本会话已经撞过三次。**

**在此之前**，Poq App 身份的进度冻结在：

```
已知：User-Agent + 6 个头名 + 4 个 offspring action + 2 个 office action
Unknown：另外 6 个头名、全部头的取值、触发它的任务类型
```

**构建单位不变**：App 面一个 flow（身份 + 四步 + 注册项），**不要只建身份常量**（R772 的教训）。
"""


def main():
    for p, marker, text in ((P1, "R776", BLOCKER), (P3, "R776", BLOCKER), (P2, "第 776 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R776" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += off_ 槽位读取器（工具债，优先）")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R776: seven Poq identity items evidenced, six header names unresolved with the exact reason\n\n"
         "The app identity is now partly pinned: the User-Agent Poq-Native-iOS-App and six headers -- poq-app-id,\n"
         "poq-app-identifier, poq-country-identifier, poq-currency-identifier, poq-slot-conditions and poq-user-id --\n"
         "alongside the four offspring actions and two office actions already recorded.\n\n"
         "The other six header names in that request builder are unresolved, and the attempts are worth writing down.\n"
         "Treating off_147115240 as a string object header and reading twelve bytes past it returns mojibake.\n"
         "pe_strings.txt records file offsets rather than virtual addresses, so filtering it by address finds nothing.\n"
         "Parsing the PE section table myself gets the conversion right -- .data RVA 0x6a47000, raw 0x6a45c00 -- and\n"
         "the bytes read back are the same mojibake anyway.\n\n"
         "The reason is that off_x is not a string object but the address of a static slot that holds a pointer to one,\n"
         "and that pointer is subject to relocation, so the file holds an unrelocated value. This is the third time\n"
         "this session has run into the same off_ family -- earlier it was four off_14492xxxx slots returning the same\n"
         "implausible length, which I noted at the time were descriptors rather than string pointers. Three encounters\n"
         "and still no reusable reader for it.\n\n"
         "So those six names are unknown rather than absent, and they stay blank. A guessed header name would mislead\n"
         "everyone who reads that code afterwards, which is a worse outcome than an honest hole.\n\n"
         "No code this round either, and the reason holds: the unit of work is an app-surface flow -- identity, four\n"
         "steps, one registry entry -- and the identity itself is only seven of thirteen items evidenced. Building on\n"
         "that would produce something half-understood.\n\n"
         "What should come first is a small reader for off_ slots: read eight bytes, decide whether the value is a VA or\n"
         "an RVA, add the image base, step twelve bytes, decode UTF-16LE. The family is everywhere in this image, and\n"
         "without the reader every key costs another round of trying. It is tooling debt, and it stands in front of\n"
         "several rounds' worth of work.\n\n"
         "No product code changed; suite remains 1752 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
