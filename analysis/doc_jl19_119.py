import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 修正：John Lewis 是 **19 步**，不是 17（第 119 轮）

R112 读到的 John Lewis 步表是 17 条，序号从 20 跳到 23 —— 我当时把那个缺口当成了编译器噪音。

**它不是。** 同一个类的**另一条字面量**（lambda 表）里写着：

```
<<FindProduct>g__Available|21_3      ← 方法 21 = FindProduct（内部还有个 local function）
<AddToCart>b__22_0                    ← 方法 22 = AddToCart
```

所以 **21 和 22 也是这个 flow 的步**：

| 序号 | 步 | R112 是否读到 |
|---|---|---|
| 20 | `GetHome` | 是 |
| **21** | **`FindProduct`** | **否** |
| **22** | **`AddToCart`** | **否** |
| 23 | `WebHandOver` | 是 |
| … | … | … |

**19 步。**

### 为什么这次能发现，上次不能

Nike 的 45/47 缺口真的是 `MoveNext` 助手（R111 已核实），所以「缺口=噪音」在 Nike 身上成立。
John Lewis 的 21/22 不是 —— **但只靠一条字面量分不出来**。

区别只在**第二条证据**：lambda 表把每个方法的序号和名字又列了一遍，
`21` 和 `22` 在那里有名字。

> **一条字面量的缺口，需要第二条字面量来判。**
> 我从 R112 到 R118 用了六轮，才第一次去看同一个类的 lambda 表。

### 对映射的影响

`FindProduct` / `AddToCart` 留空 —— **BFF 里根本没有购物车端点**，它从 handover 才开始。
所以 John Lewis 的留空步骤从 3 条变成 5 条：

```
GetHome   FindProduct   AddToCart   HandleRequiresAction   GetStripePaymentIntent
```

而「14 步 → 9 端点」不变：**新发现的两步没有端点，所以映射部分不受影响 —— 只有总数变了。**
'''

if "## 修正：John Lewis 是 **19 步**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("JL 19-step correction documented")
else:
    print("already present")
