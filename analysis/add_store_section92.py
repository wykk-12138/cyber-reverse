import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\IDB_EVIDENCE.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 店铺名的存放方式（第 92 轮）

店铺在二进制里以**类型名**形式出现，且带一个 `0x1b 0x08` 后缀（字符串池的长度/元数据标记）：

```
0x143271152  OffSpring\\u001b\\b
0x143327112  &OffSpringAppHandler\\u001b\\b
0x1433271ad   OffSpringHandler\\u001b\\b
```

所以 `^[A-Z]\\w+(Handler|Tester)$` 这种带 `$` 锚点的正则**匹配不到它们** ——
尾部控制字符会把 `$` 顶掉。要么去掉 `$`，要么用 `get_string` 按地址取。

### 店铺也出现在 User-Agent 里

同一个店的身份还写在 UA 字符串中，这比类型名更能说明「它是什么平台」：

```
Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 ...) OFFSPRING/3 (iPhone; iOS/18.3.2)
  CFNetwork/3826.400.120 Darwin/24.3.0 poq.ios/21.1.6 poq-webview/26.1.0
OFFSPRING/1 (iPhone; iOS/18.3.2) CFNetwork/3826.400.120 Darwin/24.3.0 poq.ios/21.1.6
```

`poq.ios` / `poq-webview` 是 **Poq**（一个移动电商 App 平台）。
也就是说 OffSpring 跑的是 Poq 的 App，而不是 Magento —— replica 里 `offspring` 挂
`MagentoFlow` 是**没有依据的**（VERDICT 里那条「offspring 平台未定 · C 级证据」由此有了方向）。

### 第 92 轮的查询账

| 事实 | 模式 | 命中 | `done` |
|---|---|---|---|
| 店铺类型名（带后缀） | `(bodega｜undefeated｜offspring｜scheels｜hbx｜converse)` | 137 | ✅ |
| `Handler`/`Tester` 结尾的类名 | `^[A-Z][A-Za-z0-9]+(Handler｜Tester)$` | 53 | ✅ |
| OffSpring 全部字面量 | `OffSpring` | 8 | ✅ |

53 条里绝大多数是框架类名（`EventHandler`、`PropertyChangedEventHandler`…），
真正是店铺的只有 `FootsitesTester`、`FunkoTester`、`OffSpringTester`、`OffWhiteTester` 等少数几条 ——
**这条路径不足以枚举全部店铺，只能用来确认某个店存在。**
'''

if "## 店铺名的存放方式" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("IDB_EVIDENCE: store-name section appended")
else:
    print("already present")
