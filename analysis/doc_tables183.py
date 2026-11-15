import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 两张窗口名单，和一次自我纠错（第 183 轮）

原版有两张表，不是一张：

| 表 | 读法 | 数量 |
|---|---|---|
| `WINDOW_ALL` | `Object.getOwnPropertyNames(window)` | **1062** |
| `WINDOW_ENUM` | `Object.keys(window)` | **228** |

上一轮我写的是 **1290** —— 那是我的正则把数组外围的引号串也算进去了。
**名单是证据，数字是我对名单的猜测。**

### 一、两条表的关系解释了一句我之前读不懂的话

```
// a name reported from the enumerable pass lands BEFORE the script globals and one reported only from the
// own-names pass lands after them. The iPhone reported ["__gCrWeb","hsw","__wdata","webkit"], with `webkit`
// LAST, after two script-created globals.
```

对照两张表就明白了：

```
WINDOW_ALL  最后一 项  = "webkit"      （自有名，非枚举）
WINDOW_ALL  倒数第二   = "__gCrWeb"   （枚举）
WINDOW_ENUM 最后一项   = "__gCrWeb"
WINDOW_ENUM 里没有     "webkit"
```

于是「`webkit` 排在两个脚本全局之后」不是错乱，而是**它只出现在自有名那一遍**。

### 二、十二个注入名**全部可枚举**

上一轮的十二个名字在两张表里都在 —— 所以手机的 `Object.keys(window)` 里就有它们。
「子帧要少两个」是**原版自己加的规则**，不是设备的属性。

### 三、这一轮的交付

- `WindowNameTable.Generated.cs`（27 KB）：两张表**逐字**生成，头部写明来源与「不许手改」；
- `WindowNameTable`：`AllCount` / `EnumCount` / `OwnOnly`(834) / `Injected`(12) / `LastOwnOnly='webkit'` / `Correction`；
- `WindowBaseline.RecordedNameCount` 从 1290 改为 **1062**，并新增 `RecordedEnumCount = 228`。

### 四、这一轮的一句话

> 上一轮我「数出了」1290，这一轮老老实实把数组取出来是 1062。差的那部分是**我的工具的产物**，不是设备的。
>
> **先让工具报数，再让数字进文档 —— 顺序反了，就会把自己的 bug 写成别人的事实。**
'''

if "## 两张窗口名单，和一次自我纠错" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("documented")
else:
    print("already present")
