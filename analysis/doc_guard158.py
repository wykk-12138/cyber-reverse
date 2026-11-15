import io

p = r"D:\projects\cyber-reverse\replica\docs\ENDPOINT_FAMILIES.md"
t = io.open(p, encoding="utf-8").read()

section = '''
## 三次同一个死因，该造一把尺子了（第 158 轮）

| 轮 | 错在哪 | 后果 |
|---|---|---|
| R149 | `applySurface(W)` 形参与体内 `const W` 重名 | SyntaxError，浏览器吞掉，整份脚本不执行 |
| R156 | 调用被插到 `apply` 闭合 `};` **之后**，多一个 `};` | 同上 |
| R157 | 转义拼接，`\\n` 落成字面反斜杠+n 跑到字符串外 | 同上 |

三次不同的错，同一个死因：**注入脚本的语法错误是不可见的**。

### 一、静态半边：`JsGuard`

对每一份生成的 body 检查四件事：

1. 没有字面 `\\n` / `\\t`（逃了两次的痕迹）；
2. **在字符串之外**统计 `{}` `()` `[]` 的净余额必须为 0；
3. 语句行数 ≥ 3 —— 「一整行长条」正是转义 bug 的形状；
4. 不能是空体 —— 空的 stub 在这份代码里从来等于「组合掉了」。

`AllBodies()` 覆盖五份：WebAssembly / Mobile / Engine / Touches / WebAssembly wrapper。
**新增一份 body 而忘了登记，`TheGuardCoversFiveBodies` 会红。**

### 二、动态半边：真 JS 解析器

```js
new Function('G', body)   // 编译，不执行
```

一条断言就能问出「这是不是一段程序」。并配**对照组**：

```
控制组：  try { … } catch (e) {}  ['a'].forEach(y);}      →  SyntaxError
```

对照组很重要 —— 没有它，这条测试只证明了「`new Function` 没抛」。

### 三、结果

- 五份 body 全部 `clean`（说明除 R157 那一处外，其余本来就是多行未转义的）；
- 五份 body 全部 `ok`（真解析器通过）；
- 组合后的 `applySurface`（Engine + WASM + Mobile + Touches）解析 `ok`，并且落地后
  `navigator.maxTouchPoints == 5`。

### 四、这一轮的一句话

> 同一个死因出现三次，说明**缺的不是小心，是一把尺子**。
>
> **每一次「我又犯了同样的错」的背后，都有一个本该存在的检查没被写下来。**
'''

if "## 三次同一个死因，该造一把尺子了" not in t:
    t = t.rstrip() + "\n" + section
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("guard documented")
else:
    print("already present")
