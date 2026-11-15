### 变异表从 5 条扩到 8 条，接进了 `verify.ps1 -Full`

R143 建了 `tools/mutation-check.py`，只有 5 条，全是 R136–R138 的。这一轮把
R124、R127、R133 三条也加进去，并把它接进了验证脚本。

### 三条新变异，每个打的是不同形状的守护

**一、R127 —— `Flush` 先出队再检查 sink**

```python
"find": "        if (SinkUrl is null) return;     // nothing to do, and nothing to lose\n",
"replace": ("        if (SinkUrl is null) { while (_requests.TryDequeue(out _)) { } return; }\n"
            "        if (SinkUrl is null) return;     // nothing to do, and nothing to lose\n"),
```

**还原成「空循环丢掉事件」的旧形状**，`Flush_WithNoSink_KeepsEveryEvent` 红了。

**二、R133 —— 一个 locale 丢掉 `WithCulture="false"`**

```python
"find": 'LogicalName="Cybersole.Locales.ja.json" WithCulture="false"',
"replace": 'LogicalName="Cybersole.Locales.ja.json"',
```

**这一条最狠：一次红了 5 个测试。**

因为 `ja.json` 一旦变成卫星程序集，`AllFourResourcesAreEmbedded`（数量 3≠4）、
`EveryDictionaryHasTheSameKeyCount`、`EveryDictionaryCoversTheSameKeys`、
`TranslationsDifferFromEnglish`、`ScriptIsCorrectForEachLanguage` **全部失效**——
那个字典读出来是空的。

**修一个属性，五个断言一起响。** 这是覆盖度的证明。

**三、R124 —— catch 消息被下一行覆盖**

```python
"replace": ("            status.Text = \"Saved.\";\n"
            "            try { throw new InvalidOperationException(\"x\"); }\n"
            "            catch (Exception ex) { status.Text = \"failed: \" + ex.Message; }\n"
            "            status.Text = \"Saved.\";"),
```

**在 `SettingsViews` 里造一个真的「后写赢」**：catch 写了错误，紧接着一行无条件改回成功。

`NoStatusWriteImmediatelyFollowsItsOwnCatch` 红了。

**这一条的意义和前两条不同**：前两条是「把修好的改回坏的」，
**这一条是「往一个本来没问题的文件里注入一个坏模式」**——
测的是判据能不能认出一个**新犯的**同类错误，而不只是记住旧的。

### 8/8

```
[guard fired] round 136 — the contentWindow replay route
[guard fired] round 136 — the createElement replay route
[guard fired] round 136 — replay a fresh realm through a bare global
[guard fired] round 137 — speechSynthesis voices
[guard fired] round 138 — one version reading
[guard fired] round 127 -- Flush dequeues before it checks for a sink
[guard fired] round 133 -- a locale dictionary loses its WithCulture=false
[guard fired] round 124 -- a catch message overwritten by the next line

restored tree: GREEN
```

### 接进 `verify.ps1`：只在 `-Full` 下跑

```powershell
if ($Full -and (Test-Path 'tools\mutation-check.py')) {
    $mut = & $py 'tools\mutation-check.py' 2>&1 | Out-String
    $decorative = ([regex]::Matches($mut, '\[GUARD IS DECORATIVE')).Count
    $fired      = ([regex]::Matches($mut, '\[guard fired\]')).Count
    $skipped    = ([regex]::Matches($mut, '\[skip\]')).Count
    …
    if ($decorative -gt 0) { Check 'mutation guards' $false $summary }
    elseif ($fired -eq 0)  { Warn  'mutation guards' "no guard fired — the anchors no longer match" }
    else                   { Check 'mutation guards' $true  $summary }
}
```

**三个分支，每个对应一种失败**：

| 情况 | 报告 | 含义 |
|---|---|---|
| `decorative > 0` | **FAIL** | 有守护是假的 |
| `fired == 0` | **WARN** | 锚点全失效了（源码改过，变异没跟上） |
| 其他 | **PASS** | 全部有效 |

**第二个分支是我写完才想到的**：如果哪天重命名了一个变量，所有 `find` 都会失配，
脚本会报 `0 fired`。**那看起来像「全都没问题」，实际是「全都没测」。**
`WARN` 让这个状态区别于 PASS。

### 一个自己踩的坑：计数翻倍

第一次接进去报 `16 fired`。因为脚本在两个地方打印：

```
[guard fired] round 136 — ...        ← 循环里，带方括号
guard fired          round 136 — ...  ← summary 里，不带
```

**数裸的 `guard fired` 就数了两遍。**

改成数 `\[guard fired\]`——**方括号只出现在循环里。**

**这跟 R143 那个装饰性断言是同一类错误**：我数的是「一个词出现过几次」，
而不是「几件事发生了」。**数词比数事简单，所以会不自觉地数词。**

### 验证

```
powershell -File tools\verify.ps1 -Full
  unit tests         PASS   exit 0
  mutation guards    PASS   8 fired, 0 decorative, 0 skipped
  VERDICT: all checks passed
```

---
