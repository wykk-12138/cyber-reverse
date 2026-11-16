"""Record R783: casioid is a property name, and that is not enough to change code."""

import io
import subprocess

P1 = r"D:\projects\cyber-reverse\docs\BLOCKERS.md"
P2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
P3 = r"D:\projects\cyber-reverse\docs\DELIVERY_STATUS.md"
B = r"D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 209. `casioid` 是个**属性名**；而"知道它是属性名"不足以改代码

> R783。未改产品代码。

### 一、两个函数读出来了（Observation）

**`sub_14094AF90`（187 B）** —— 形状是"按键取值，带默认"：

```c
v3 = sub_1419DFEE0(a2, 59, 512);          // 取/切一个键
v4 = new(unk_144D78A38);
sub_143028E70(v4 + 16, v3);
v5 = sub_142E74730(&off_14496B7C8, v4, v9);   // 字典查
v6 = v5 ? *(v5 + 32) : nullptr;
if (!v6) v6 = &off_146A622F8;             // 默认值
v7 = sub_141CFA730(v6, &off_146FC1E80);   // 比较
```

**它比较的对象 `off_146FC1E80` 就是 `casioid`** —— `0x146fc1e8c − 12 = 0x146fc1e80`，
而 R774 的池子记录里 `0x146fc1e8c` 正是 `'casioid'`。

**所以这个函数 = 「取 `casioid` 这个键的值，取不到给默认」。**

**`sub_140952790`（893 B）** 里把它当**成员名**挂到构造出的对象上
（`*(v9 + 16) = &off_146FC1E80`），并做数组/列表的扩容。

**合起来：`casioid` 是 Casio 商品对象上的一个属性名。**

### 二、而我不改 `FindVariantAsync`

`CasioFlow.FindVariantAsync` 现在是：

```csharp
var sku = Regex.Match(body, @\"\"\"sku\"\"\\s*:\\s*\"\"([^\"\"]+)\"\"\").Groups[1].Value;
c.Session.VariantId = sku;
```

**诱惑是**：既然镜像里有 `casioid`，就把它也当候选 id 加进去。

**但这个改动可能是"看起来成功"的错误**：

- 如果 `casioid` 是**商品 id**，把它当 `VariantId` 会让加购请求带错标识
- 而那种错**不会报错** —— 请求可能带着一个合法但错误的 id 发出去

**这比"现在用 sku"更糟**：至少 `sku` 是明确的变体概念。

**所以本轮不改。** 需要的是**一个能区分「商品 id」与「变体 id」的证据**，而不是一个名字。

### 三、连着三轮"只记录不改"

R781（Casio 判定路径）、R782（改了，但只在有保底时改）、R783（不改）。

**这不是停滞**：R781 定出了路径，R782 用它改了判定并加了保底，R783 拒绝了一个会让请求带错 id 的改动。

**判据是"改完之后出错的方式会不会更糟"**：
R782 的改动有 fallback，最坏情况等于没改；R783 那个没有，最坏情况是**静默发错 id**。

### 四、验证

```
本轮未改产品代码
完整套件保持 1757 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 五、仍然 Unknown

- **`casioid` 是商品 id 还是变体 id**：**Unknown** —— 这是挡在 `FindVariantAsync` 前面的唯一问题。
- `casio_dob` / `casio_gender` / `casio_image_url` 的用途：**Unknown** —— 名字像商品属性，未验证。
- `sub_140952790` 构造的是什么对象：**Unknown** —— 893 B 里有多处对象分配与数组扩容，未读全。
- `CasioRegion` 的取值集合与分区行为：**Unknown**（R781）。
"""

VERDICT = """

---

## 第 783 轮：知道了属性名，但那不足以改代码

### 两个函数读出来了

- **`sub_14094AF90`** = 「取 `casioid` 键的值，取不到给默认」——
  它比较的对象 `off_146FC1E80` 就是 `casioid`（`0x146fc1e8c − 12`）
- **`sub_140952790`** 把 `casioid` 当**成员名**挂到构造出的对象上

**所以 `casioid` 是 Casio 商品对象的一个属性名。**

### 而我不改 `FindVariantAsync`

诱惑是「镜像里有 `casioid`，就把它当候选 id」。**但那个改动可能是看起来成功的错误**：

- 若 `casioid` 是**商品 id**，当 `VariantId` 用会让加购请求带错标识
- **而那种错不报错** —— 一个合法但错误的 id 会照常发出去

> **这比"现在用 sku"更糟：至少 `sku` 是明确的变体概念。**

**判据是「改完之后出错的方式会不会更糟」：**
R782 那个改动有 fallback，最坏等于没改；这一个没有，最坏是**静默发错 id**。

### 仍然 Unknown

**`casioid` 是商品 id 还是变体 id** —— 挡在 `FindVariantAsync` 前面的唯一问题。
"""

BACKLOG_ADD = """

## 核心 — Casio `casioid` 的悬案（R783）

**已知（Observation）**：`casioid` 是 Casio 商品对象上的**属性名**。
`sub_14094AF90`（187 B）按键取它并带默认；`sub_140952790`（893 B）把它作成员名挂到构造对象上。

**未知**：它是**商品 id** 还是**变体 id**。

| 决定 | 理由 |
|---|---|
| **不改 `FindVariantAsync`** | 若 `casioid` 是商品 id，当 `VariantId` 用会**静默发错 id** —— 比现状更糟 |

**需要什么才能改**：一条能区分「商品 id」与「变体 id」的证据 ——
例如读 `sub_140952790` 里那个对象的其余成员，或找到把 `casioid` 与 `sku` 一起用到的调用点。

**判据**：改动后最坏情况是否会**更糟且不报错**。会 → 不改。
"""


def main():
    for p, marker, text in ((P1, "R783", BLOCKER), (P3, "R783", BLOCKER), (P2, "第 783 轮", VERDICT)):
        body = io.open(p, encoding="utf-8").read()
        if marker in body:
            print("  %s already has %s" % (p.split("\\")[-1], marker))
            continue
        io.open(p, "a", encoding="utf-8").write(text)
        print("  %s += %s" % (p.split("\\")[-1], marker))

    body = io.open(B, encoding="utf-8").read()
    if "R783" in body:
        print("  BINDING_BACKLOG already updated")
    else:
        io.open(B, "a", encoding="utf-8").write(BACKLOG_ADD)
        print("  BINDING_BACKLOG += casioid 悬案")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R783: casioid is a property name, and that is not enough to justify changing code\n\n"
         "Both functions that reference casioid are now read. The 187-byte one is a keyed lookup with a default, and\n"
         "the object it compares against at off_146FC1E80 is casioid itself -- twelve bytes before the string in the\n"
         "pool. The 893-byte one attaches casioid as a member name to an object it constructs. So casioid is a property\n"
         "on the Casio product object.\n\n"
         "What that does not establish is whether it is the product id or the variant id, and the tempting change --\n"
         "offer casioid as another candidate for Session.VariantId alongside the current sku regex -- fails on the\n"
         "failure mode. If it is the product id, the add-to-cart request carries a valid but wrong identifier, and\n"
         "nothing reports an error. That is worse than the status quo, where at least sku names a variant concept.\n\n"
         "The test I have been applying for three rounds is whether a change makes the way things can go wrong worse.\n"
         "R782's fallback scores well: if the JSON is not there, behaviour is exactly what it was. This one scores\n"
         "badly: silent wrongness with no signal. So it stays unbuilt until something distinguishes product from\n"
         "variant -- reading the rest of the object built in the larger function, or finding a call site that uses\n"
         "both names together.\n\n"
         "Three rounds of mostly recording looks like standing still; what it actually is: R781 established the path,\n"
         "R782 used it with a guard, and R783 declined a change that would have looked like progress.\n\n"
         "No product code changed; suite remains 1757 pass / 0 fail."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
