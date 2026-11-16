"""Record R829: the first decompiled flow step, the recipe that reached it, and what it confirmed."""

import io
import os
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = os.path.join(ROOT, "docs", "BLOCKERS.md")
RSTATUS = os.path.join(ROOT, "docs", "DELIVERY_STATUS.md")
RVERDICT = os.path.join(ROOT, "replica", "docs", "VERDICT.md")
BACKLOG = os.path.join(ROOT, "replica", "docs", "BINDING_BACKLOG.md")
HANDOFF = os.path.join(ROOT, "docs", "HANDOFF.md")

BLOCKER = """

---

## 253. **第一个反编译出来的流程步骤**：`/cart.js` —— 而且复刻件早就是这么做的

> R829。未改产品代码。

### 一、路线（记住这四步，含那个 `−12`）

```
1. python analysis\\ida.py str "/cart.js"          -> 0x146ab247c
2. python analysis\\ida.py xrefs 0x146ab2470        -> 0x141156e1d, in sub_141156D40
3. python analysis\\ida.py dec 0x141156d40          -> the async MoveNext
```

**第 2 步的关键**：**xrefs 打到 `字符串字符地址` 是 0，打到 `地址 − 12`（NativeAOT 的字符串对象头）才有。**
我试了 `+0` / `+12` / `−12` 三个，**只有 `−12` 命中一次。**

### 二、反编译出来的东西

`sub_141156D40`（0x216 字节）是一个 `async` 状态机的 `MoveNext` —— 特征是
`if (*((_DWORD *)a1 + 4))` 按状态字段分支、`__ExceptionPtrRethrow`、收尾 `sub_143028EE0(v12)`。

**决定性的一行：**

```c
v7 = sub_141CF6230(*(_QWORD *)(v1 + 16), (__int64)&off_146AB2470);   // &off_146AB2470 == "/cart.js"
```

**所以镜像里确有一段代码真的用 `/cart.js`。**

### 三、复刻件那边已经有

```
ShopifyFlow.cs:181   var res = await GetAsync(c, Origin(c.Url) + "/cart.js", "shopify-cart-get", ct)
ShopifyFlow.cs:11    /// Walked in the order the binary uses: product JSON → cart/add → cart.js → checkout to
```

**它不但有，而且注释写明顺序是照二进制走的。**

**所以这次反编译印证了已有实现，没暴露缺口。** 这是本会话第一次用反编译去对一个复刻件流程做交叉验证，
**结果是吻合的。**

### 四、这一轮真正的产出是两条

1. **一条可复用的路线**（`str` → `xrefs` 到 `−12` → `dec`），**下一轮可以直接用来查 `HandleBlock`**
2. **一个校准结果**：复刻件的 `ShopifyFlow` 与镜像在 `/cart.js` 这一点上一致

**至于 `HandleBlock`，本轮没查到** —— **它不是被字符串引用的东西，得走上一轮说的 MethodTable 路线。**
**而这一轮的路线能查的是「有 endpoint 的步骤」，`HandleBlock` 按名字看是「处理封锁」，可能没有自己的 endpoint。**

### 五、验证

```
python analysis\\ida.py str "/cart.js"      -> 1 match @0x146ab247c
python analysis\\ida.py xrefs 0x146ab2470   -> 1 xref, sub_141156D40
python analysis\\ida.py dec 0x141156d40     -> 2747 chars, 含 &off_146AB2470
复刻件 ShopifyFlow.cs:181 已有 GetAsync(... "/cart.js")
本轮未改产品代码
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **`sub_141156D40` 属于哪个流程类**：**Unknown** —— 状态机名在元数据里但没和这个地址关联上，
  **要关联得走 MethodTable。**
- **它调用前后还做了什么**：**Unknown** —— 我只读了这一段的 80 行，
  **`sub_140B61E0` / `sub_142D72040` 是构请求与 await，没展开。**
- **`HandleBlock` 的代码**：**Unknown，且本轮没推进** —— 需要另一条路线。

### 七、教训

**这一轮没有找到缺陷，但它把「能不能用反编译核对复刻件」这件事验证了：能。**
**而代价只是一次字符串搜索加一次 xref 尝试。**

**`−12` 这个偏移我试了三个地址才命中。** **下次先试 `−12`，别再试 `+12`。**
"""

VERDICT = """

---

## 第 829 轮：第一个反编译的流程步骤 —— `/cart.js`，而复刻件早就是这么做的

### 路线（含 `−12`）

```
ida.py str "/cart.js"        -> 0x146ab247c
ida.py xrefs 0x146ab2470     -> 0x141156e1d in sub_141156D40     <- 地址 − 12 才命中
ida.py dec 0x141156d40       -> async MoveNext
```

**`xrefs` 打到字符地址是 0，打到 `−12`（字符串对象头）才有。我试了 `+0`/`+12`/`−12`，只有 `−12` 命中。**

### 反编译结果

```c
v7 = sub_141CF6230(*(_QWORD *)(v1 + 16), (__int64)&off_146AB2470);   // "/cart.js"
```

**镜像里确有一段代码真的用 `/cart.js`。**

### 复刻件那边已经有

```
ShopifyFlow.cs:181   await GetAsync(c, Origin(c.Url) + "/cart.js", "shopify-cart-get", ct)
ShopifyFlow.cs:11    /// Walked in the order the binary uses: product JSON → cart/add → cart.js → checkout to
```

> **它不但有，而且注释写明顺序照二进制走 —— 这次反编译印证了已有实现，没暴露缺口。**
> **这是本会话第一次用反编译对复刻件流程做交叉验证，结果吻合。**

### 产出

1. **一条可复用的路线**，下一轮可直接用于查有 endpoint 的步骤
2. **一个校准结果**：`/cart.js` 这一点上复刻件与镜像一致

**`HandleBlock` 本轮没查到** —— 它不是被字符串引用的东西，得走 MethodTable；而按名字看它是「处理封锁」，可能没有自己的 endpoint。

### 验证

```
str 1 match · xrefs 1 (sub_141156D40) · dec 2747 chars 含 &off_146AB2470 · 复刻件已有
产品代码未改 · 度量 4 / 0 / 17 / 78 / 0
```

### 教训

**`−12` 我试了三个地址才命中。下次先试 `−12`。**
**而「能不能用反编译核对复刻件」这件事，本轮验证了：能，代价是一次字符串搜索加一次 xref。**
"""

BACKLOG_ADD = """

## 方法 — 反编译一个流程步骤的四步（R829）

```
1. ida.py str "<endpoint>"          -> string addr
2. ida.py xrefs <addr - 12>         -> <- 关键：−12（字符串对象头），+0 与 +12 都是 0
3. ida.py dec <enclosing func>      -> async MoveNext
4. 找 &off_<addr> 那一行            -> 该步骤确实用了这个 endpoint
```

**首个用例**：`/cart.js` → `0x146ab247c` → `xrefs 0x146ab2470` → `sub_141156D40`（0x216 B）→
`v7 = sub_141CF6230(..., &off_146AB2470)`。

**校准结果**：复刻件 `ShopifyFlow.cs:181` 已 `GetAsync(... "/cart.js")`，
且 `:11` 注释写明顺序照二进制走。**吻合，无缺口。**

**`HandleBlock` 不能用这条路** —— 它不是被字符串引用的，得走 MethodTable；
按名字看是「处理封锁」，可能没有自己的 endpoint。

| 仍 Unknown | |
|---|---|
| `sub_141156D40` 属于哪个流程类 | 状态机名未与地址关联，需 MethodTable |
| 该步骤前后还做什么 | 只读了 80 行；构请求与 await 未展开 |
| `HandleBlock` 的代码 | **本轮未推进** |

**纪律**：**`xrefs` 的地址要 `−12`。下次先试它，别再试 `+12`。**
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8", errors="surrogateescape").read()
    if marker in body:
        print("  %-24s already has %s" % (os.path.basename(path), marker))
        return
    io.open(path, "a", encoding="utf-8", errors="surrogateescape").write(text)
    print("  %-24s appended %s" % (os.path.basename(path), marker))


def main():
    ensure(RBLOCK, "R829", BLOCKER)
    ensure(RSTATUS, "R829", BLOCKER)
    ensure(RVERDICT, "第 829 轮", VERDICT)
    ensure(BACKLOG, "R829", BACKLOG_ADD)

    h = io.open(HANDOFF, encoding="utf-8").read()
    if "R829" not in h:
        h += ("\n## R829 补充 — 反编译一个流程步骤的四步\n\n"
              "```\n1. ida.py str \"<endpoint>\"        -> string addr\n"
              "2. ida.py xrefs <addr - 12>       -> 关键：−12（对象头），+0/+12 都是 0\n"
              "3. ida.py dec <enclosing func>    -> async MoveNext\n"
              "4. 找 &off_<addr> 那一行          -> 确认该步骤用了这个 endpoint\n```\n\n"
              "**首个用例 `/cart.js` 印证复刻件 `ShopifyFlow.cs:181` 已一致 —— 反编译核对这条路是通的。**\n"
              "**`HandleBlock` 不走这条路**（不被字符串引用），需 MethodTable。\n")
        io.open(HANDOFF, "w", encoding="utf-8", newline="").write(h)
        print("  handoff updated")

    ok = all(key in io.open(p, encoding="utf-8", errors="surrogateescape").read()
             for p, key in ((RBLOCK, "R829"), (RSTATUS, "R829"), (RVERDICT, "第 829 轮"), (BACKLOG, "R829")))
    print("  all markers present: %s" % ok)
    if not ok:
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R829: the first decompiled flow step, and it agrees with the replica\n\n"
         "After R828 established that name strings carry no xrefs, the way to code had to come from something else."
         " Endpoint literals do carry xrefs, provided the address is right: xrefs to the character data return nothing,"
         " while xrefs to that address minus twelve -- the NativeAOT string object header -- return the reference. I"
         " tried plus zero, plus twelve and minus twelve; only the last one hit.\n\n"
         "So /cart.js at 0x146ab247c is referenced once, from 0x141156e1d inside sub_141156D40, a 0x216-byte async"
         " state machine MoveNext which dispatches on a state field, rethrows through ExceptionPtrRethrow and closes by"
         " releasing the state. The decisive line builds something from &off_146AB2470, which is the /cart.js string"
         " object, so this code does fetch that endpoint.\n\n"
         "The replica already does it: ShopifyFlow line 181 issues GetAsync against Origin(c.Url) plus /cart.js, and its"
         " header comment says the order was walked as the binary uses it, product JSON then cart/add then cart.js then"
         " checkout. So the decompilation confirms an existing implementation rather than exposing a gap, which is the"
         " first time this session has used the decompiler to cross-check a replica flow. It agrees.\n\n"
         "What the round produces is therefore a recipe and a calibration. The recipe is string, then xrefs at minus"
         " twelve, then decompile, then find the &off_ line; it works for any step that owns an endpoint literal. The"
         " calibration is that the replica's Shopify flow matches the image on this point.\n\n"
         "HandleBlock was not reached, and this route cannot reach it. It is not referenced by a string, so it needs the"
         " MethodTable walk described last round, and by its name it handles a block rather than calling an endpoint.\n\n"
         "Unknown: which flow class owns sub_141156D40, since the state machine name exists in metadata but is not tied"
         " to this address without the type graph; what the step does either side of the fetch, since I read eighty lines"
         " and left the request construction and the await unexpanded; and HandleBlock's code, which did not move this"
         " round.\n\n"
         "No product code changed; four metrics unchanged at 4 / 0 / 17 / 78 / 0."],
        cwd=ROOT, capture_output=True, text=True)
    print("  commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:120]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
