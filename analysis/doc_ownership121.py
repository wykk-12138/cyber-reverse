import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 归属如何证明：lambda 字面量，而不是 `d__` 连续段（第 121 轮）

R120 说「序号扫描证明不了归属」。这一轮找到了**能证明归属的证据**，顺便推翻了自己的一个默认假设。

### 证据一：`d__` 连续段 —— **不可靠**

```
1046:GetAccessToken   1050:CartApiObjectCreate   106:AddToCartGraphQL
```

1046 和 1050 属于**另一个大得多的类**，它的字符串只是**恰好排在这个类的字符串旁边**。

> **池里的相邻 = 文件里的相邻，不是「同一个类」。**

### 证据二：lambda 字面量 —— **可靠**

编译器把一个类的 lambda 生成成**一条字符串**，里面每个方法都带编号和名字：

```
:<CartApiObjectCreate>b__105_0  4<AddToCartGraphQL>b__106_0  B<AddToCartPreloadGraphQL>b__107_0
6<CreateCartGraphql>b__108_0   H<GetCartAvailabilityGraphql>b__109_0 … 6<RefreshEmailLogin>b__114_2
```

**连续 105 → 109，加 114，名字都在。** 这是这个类自己的方法表。

### 于是有一个 GraphQL 购物车类

| 序号 | 方法 |
|---|---|
| 105 | `CartApiObjectCreate` |
| 106 | `AddToCartGraphQL` |
| 107 | `AddToCartPreloadGraphQL` |
| 108 | `CreateCartGraphql` |
| 109 | `GetCartAvailabilityGraphql` |
| 114 | `RefreshEmailLogin`（同一个 lambda 字面量点名，属于这个类但不是购物车调用） |

四条 GraphQL 购物车调用 —— **正是 R96 证明 replica 完全缺失的那半边**。

### 十条回合绕出来的规则

> **lambda 字面量是归属证人；`d__` 连续段不是。**

R112 用连续段读步表（对），R119 用 lambda 表补跳空的步（对），R120 用裸序号扫描（错），
R121 才说清**为什么前两个对、第三个错**：

| 方法 | 能回答什么 |
|---|---|
| `d__` 连续段 | 一个类**大概**有哪些步（相邻但可能串类） |
| **lambda 字面量** | 一个类**确实**有哪些方法（一条串起，名字+序号成对） |
| 裸序号扫描 | 什么都证明不了（跨类编号冲突） |
'''

if "## 归属如何证明：lambda 字面量" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("ownership rule documented")
else:
    print("already present")
