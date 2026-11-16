"""Record R798: hypecommerce's builder found, its payload not -- and why the rewrite waits."""

import io
import subprocess

ROOT = r"D:\projects\cyber-reverse"
RBLOCK = ROOT + r"\docs\BLOCKERS.md"
RSTATUS = ROOT + r"\docs\DELIVERY_STATUS.md"
RVERDICT = ROOT + r"\replica\docs\VERDICT.md"
BACKLOG = ROOT + r"\replica\docs\BINDING_BACKLOG.md"

BLOCKER = """

---

## 224. hypecommerce 的四个 builder 找到了，**请求体不在里面** —— 第五次同一形状

> R798。未改产品代码。

### 一、四个端点各有一个调用者（Observation）

```
entries/create          sub_140CC63F0  (396 B)
entries/validate        sub_140CC9110  (393 B)
payment/methods/store   sub_140CC8DE0  (726 B)
settings                sub_140CC7E90  (373 B)
```

**一端点一函数，干净。**

### 二、`entries/create` 的形状

```c
v4 = new(unk_144BDF900);
sub_1408C22E0(v4, &off_147051048);            // 填入 entries/create 的 URL
v5 = new(unk_144FE9240);
sub_142FA9684(v5, v1);                        // 把 v1 序列化成请求体
v9[0] = sub_1408B6310(v3, v4, v2, v5, v9[0]); // (客户端, URL, 方法, 内容, …) 发出去
```

**`sub_1408B6310(client, url, method, content, …)` 是这个站用的发送器** ——
与 Poq / Hypris 那些构造器同形，只是内容是 JSON。

### 三、请求体为什么拿不到

**`v1` 是被序列化的那个对象，而它来自调用方。** 这个函数只知道"把它序列化并 POST 出去"。
**要拿字段名，得往上找到 `v1` 的构造点。**

**这是本会话第五次同一形状**：

| 站 | 端点 | 缺的 |
|---|---|---|
| casio | `/cart/add` 族 | 区域 token |
| warhammer | `/graphql`（已解决，靠池子里的原文） | — |
| goat | `build-reservation` | 请求体 |
| popmart | `/web/v2` | 请求体 |
| **hypecommerce** | `entries/create` | **请求体** |

**共同点：端点是字符串字面量（搜就有），请求体是运行时构造的对象（要读调用链）。**

### 四、为什么这一轮不改 `HypeCommerceFlow`

R797 立了项：要么按 entries 重写，要么降级成诚实失败。**这一轮查清了端点的形状，但没有请求体。**

**而重写意味着删掉 8 个 override、换成一个 validate→create 的链。**
**在一个轮次的后半段开始这种手术，是我这几十轮反复自伤的方式**（R766 拿方法头当锚点、R789 手抄字符串）。

**所以：先把形状查清、写在案上，下一轮整轮做那件事。**

**这不是拖延 —— 上一轮的立项说的是"改 8 个 override 的方向决定"，而方向现在有了（entries），材料还差一半（请求体）。**

### 五、验证

```
本轮未改产品代码
完整套件保持 1766 通过 / 0 失败
四项度量 4 / 0 / 17 / 78 / 0（未变）
```

### 六、仍然 Unknown

- **`entries/create` 的请求体字段**：**Unknown** —— 要往上追 `v1` 的构造点。
- **`entries/validate` 的请求体**：**Unknown**，同理。
- **`payment/methods/store` 与 `settings` 的用途**：**Unknown**。
- **`sub_1408B6310` 的签名**（五个参数各是什么）：**Inference（高）** 从调用处推断为
  (客户端, URL, 方法, 内容, 结果槽)，**未读函数体**。
"""

VERDICT = """

---

## 第 798 轮：hypecommerce 的 builder 找到了，请求体不在里面

### 四个端点各一个调用者

```
entries/create 396 B · entries/validate 393 B · payment/methods/store 726 B · settings 373 B
```

### `entries/create` 的形状

```c
sub_1408C22E0(v4, &off_147051048);            // 填 URL
sub_142FA9684(v5, v1);                        // 把 v1 序列化
sub_1408B6310(v3, v4, v2, v5, v9[0]);         // 发出去
```

**`v1` 来自调用方 —— 函数只知道「序列化它并 POST」。**

### 这是第五次同一形状

| 站 | 端点 | 缺的 |
|---|---|---|
| casio | `/cart/add` 族 | 区域 token |
| goat | `build-reservation` | 请求体 |
| popmart | `/web/v2` | 请求体 |
| **hypecommerce** | `entries/create` | **请求体** |

> **共同点：端点是字符串字面量（搜就有），请求体是运行时构造的对象（要读调用链）。**

### 为什么不在这轮改

R797 立了项。**方向现在有了（entries），材料还差一半（请求体）。**

**重写意味着删 8 个 override —— 在一个轮次的后半段开始这种手术，是我这几十轮反复自伤的方式。**

### 验证

```
产品代码未改 · 整套 1766 / 0 · 度量未变
```
"""

BACKLOG_ADD = """

## 核心 — hypecommerce（R798：端点形状清、请求体缺）

```
entries/create          sub_140CC63F0 (396 B)
entries/validate        sub_140CC9110 (393 B)
payment/methods/store   sub_140CC8DE0 (726 B)
settings                sub_140CC7E90 (373 B)
```

**`entries/create` 内是「填 URL → 序列化 v1 → 发送」，`v1` 来自调用方。**

**第五次「端点已知、请求体未知」**（前四次：casio 区域 token、goat build-reservation、popmart /web/v2）。

| 待做 | 缺什么 |
|---|---|
| 重写 `HypeCommerceFlow` 成 validate→create | **请求体字段**（追 `v1` 的构造点） |
| 或者降级成诚实失败 | — |

**下一轮整轮做这件事** —— 不在轮次后半段开始删 8 个 override 的手术。

**规律（值得记住）**：端点是字符串字面量，**搜池子就有**；
请求体是运行时构造的对象，**必须读调用链**。两者的取证成本差一个数量级。
"""


def ensure(path, marker, text):
    body = io.open(path, encoding="utf-8").read()
    if marker in body:
        print("  %-26s already has %s" % (path.split("\\")[-1], marker))
        return
    io.open(path, "a", encoding="utf-8").write(text)
    print("  %-26s appended %s" % (path.split("\\")[-1], marker))


def main():
    ensure(RBLOCK, "R798", BLOCKER)
    ensure(RSTATUS, "R798", BLOCKER)
    ensure(RVERDICT, "第 798 轮", VERDICT)
    ensure(BACKLOG, "R798", BACKLOG_ADD)

    ok = True
    for path in (RBLOCK, RSTATUS, RVERDICT, BACKLOG):
        body = io.open(path, encoding="utf-8").read()
        key = "第 798 轮" if path == RVERDICT else "R798"
        present = key in body
        ok = ok and present
        print("  verify %-24s %s" % (path.split("\\")[-1], present))

    if not ok:
        print("  REFUSING to commit: a record is missing")
        return 1

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R798: hypecommerce's four builders are located, their payloads are not -- the fifth time this shape appears\n\n"
         "Each of the four admin endpoints has exactly one caller: entries/create at 396 bytes, entries/validate at 393,\n"
         "payment/methods/store at 726 and settings at 373. The create builder reads as fill-in-the-url, serialise the\n"
         "object, send -- with the object arriving from its caller. So the function knows to POST a serialised payload\n"
         "and knows nothing about what is in it.\n\n"
         "That is the fifth time this session has hit the same asymmetry. Casio's cart needed a region token, goat's\n"
         "build-reservation and popmart's /web/v2 need request bodies, and now entries/create needs one too. The pattern\n"
         "is worth naming: an endpoint is a string literal and searching the pool finds it in one call, while a request\n"
         "body is an object assembled at run time and has to be traced through the call chain. The two cost an order of\n"
         "magnitude apart, and confusing the first for the second is how a round ends with an endpoint and no way to use\n"
         "it.\n\n"
         "No code this round, deliberately. R797 filed the HypeCommerceFlow rewrite as its own decision; the direction\n"
         "is now settled (entries, validate then create) and half the material is missing. Rewriting means deleting\n"
         "eight overrides, and starting surgery of that size late in a round is precisely the habit that produced the\n"
         "anchor-replacement and hand-transcription mistakes earlier in this session. The shape goes on the record and\n"
         "the rewrite gets a whole round.\n\n"
         "Unknown: the request bodies for create and validate, which need the construction site of the payload object;\n"
         "what payment/methods/store and settings are for; and the exact signature of the sender, inferred from its\n"
         "call site rather than read.\n\n"
         "Suite 1766 pass / 0 fail; four metrics unchanged."],
        cwd=ROOT, capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:160]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
