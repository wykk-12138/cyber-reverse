import io
# refresh the status numbers in SESSION_STATE with the green full-suite run
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
i = t.index('## 当前状态')
j = t.index('## 数据目录')
block = '''## 当前状态（R426，机器重启后全量跑通）

```
完整套件   1606 通过 / 0 失败 / 2 跳过（-m:1，59 秒）
UI 类      105 声明 / 29 不可达
名字级缺口 17（tools/bind_diff.py）
类型级缺口 10 个类型（tools/bind_scope.py）
成员形状   272 处差异，已接受（tools/shape_audit.py）
文案       19 个区已清；剩 5 条池中截断（ProfileCsv 2 / Utilities 2 / Settings 1）
落盘格式   settings / tasks / solvers / checkoutHistory / .cyb 全部对齐并钉住
```

'''
t = t[:i] + block + t[j:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('SESSION_STATE refreshed')

p2 = r"D:\projects\cyber-reverse\replica\docs\VERDICT.md"
t2 = io.open(p2, encoding='utf-8').read()
add = '''
---

## 第 426 轮：机器重启后全量跑通，并把两个守卫的"过宽/过窄"修正

### 一、全量（这台机器第一次在无内存压力下跑）

```
1606 通过 / 0 失败 / 2 跳过（-m:1，59 秒）
```

### 二、两处守卫修正

1. `DocsConsistencyTests.TheErrorTextCountInVerdictMatchesTheCatalogue`：
   正则 `(\\d+)\\s*条(?:：|逐字|错误文案|文案|错误)` **太宽** —— 它把 R410–R415 的"39 条文案 / 8 条逐字"
   当成错误文案计数，报了 4 条假失败。收窄为 `(\\d+)\\s*条(?:错误文案|错误文本)`。
2. `OriginalViewClassParityTests`：`MonitorView` 现在按名字存在，于是原版那个类的归类从
   *renamed* 变成 *same* → `same 75 → 76`、`renamed 12 → 11`。数字随事实改。

### 三、顺带发现：原版的 `MonitorView` 绑着五个成员

```
MonitorView   LinkChange, OpenFilter, OpenUrl, Quicktask, View
```

`bind_scope` 因为我的新类同名而把它们归到了我这边 —— 这**不是缺陷**，是"原版这个页面还有五个绑定"的信息。
已记入 backlog，等有 GUI/反编译证据再落地。

### 四、这一轮的一句话

> 全量跑通只用了 59 秒；这台机器卡了整整 20 轮，卡的不是代码。

> **先修环境，再修代码。**
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add)
print('VERDICT appended')
