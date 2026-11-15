import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## Kasada 是**四条路**，replica 只有一条（第 136 轮）

回到反编译主线，把原版的 Kasada 状态字符串全捞出来 —— 立刻发现我建的东西只覆盖了四分之一。

### 一、字符串就是证据

```
IKasadaSolver                       ← 一个接口，所以求解器是可插拔的
Getting Kasada ( / (1) / (2)        ← 「取」：向服务要
Getting Kasada (MFC)                ← 移动回退路上取
Failed getting Kasada               ← 「取」失败
Failed getting Kasada (Rotating)    ← 取失败 + 代理正在轮换
Failed solving Kasada               ← 「解」失败（跑页面）
Failed solving Kasada (TL)          ← 解失败于 TL 环节
Failed Kasada (Retry limit reached) ← 整条策略放弃
Kasada API down (Contact staff)     ← 服务不可达 —— 这是**运维问题**
Kasada-Fallback / Kasada-Mobile-Fallback   ← 两个**具名**回退
```

### 二、两处纠正

**① 「getting」和「solving」是两个动词。** 取 = 向远端服务要；解 = 跑页面。
`Kasada API down (Contact staff)` 只在一个**存在远端服务**的世界里讲得通 ——
而 replica 只有本地浏览器求解（`ChromiumKasadaSolver`）。

**② 回退是具名的**，所以调用方**知道**自己拿到的是哪一路。replica 之前没有这个概念。

### 三、四种模式

| 模式 | 动词 | 依据 |
|---|---|---|
| `Api` | getting | `Getting Kasada (…)`、`Kasada API down` |
| `Local` | solving | `Failed solving Kasada` |
| `Fallback` | falling back to | `Kasada-Fallback` |
| `MobileFallback` | falling back to | `Kasada-Mobile-Fallback`、`(MFC)` |

配 `IKasadaSolver` 接口（镜像里就声明了它）—— `ChromiumKasadaSolver` 只是**其中一种实现**。

### 四、版本头是**每店一个**，不是一个常量

```
Nike-Kasada-Version   Footsites-Kasada-Version   Scheels-Kasada-Version
Converse-Kasada-Version   Crocs-Kasada-Version (+ EU / JP)
```

七个。所以它是表，不是常量 —— 这也解释了为什么 Nike 那个常量在 `NikeHeaders` 里而不是全局。

### 五、8 个协议头

`x-kpsdk-ct / cd / dt / dv / fc / h / im / st` —— 比之前记的多出 **`st`**。

### 六、这一轮的一句话

> 我一直以为「Kasada 求解」就是一件事。字符串告诉我它是一条**策略**：
> 先取、再解、再回退，回退还有两条。
>
> **我把一条策略实现成了一个函数，然后以为这就是全部。**
'''

if "## Kasada 是**四条路**" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("kasada strategy documented")
else:
    print("already present")
