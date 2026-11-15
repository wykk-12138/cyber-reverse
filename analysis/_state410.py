import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 410 轮：`ProfileCsv` 一整族 39 条文案一次收进表里

### 一、做法

不再一条条加常量，而是把**整族**放进一张表：

```csharp
public static readonly IReadOnlyDictionary<string, string> Copy = new(StringComparer.Ordinal)
{
    ["Title"] = "CSV Editor",                 // ProfileCsv.Title
    ["Apply"] = "Apply Changes",              // ProfileCsv.Apply
    ...
    ["SummaryNone"] = "No changes",           // ProfileCsv.Summary.None
};

public static string Text(string name) => Copy.TryGetValue(name, out var text) ? text : string.Empty;
```

每行注释写着它来自哪个 locale 键 —— **文案与出处绑在一起**。

### 二、结果

```
before  ProfileCsv: 33 values not present
after   ProfileCsv: 2 values not present    ← 只有两条"值在池子里被截断"
```

剩下两条：`ProfileCsv.Error.UnknownCountry` / `.UnknownState`，池子里的值结尾是反斜杠（`Unknown country \\`），
**后面的部分不在字符串表里**。写半句就是编，所以留白并注明原因。

### 三、验证

```
ProfileCsvCopyTests（表格 39 条 / 8 条逐字 / 未知键返回空）
PageCopyTests
合计 31 通过 / 0 失败
```

### 四、这一轮的一句话

> 33 条文案，如果一条条加常量要写 33 段；放进一张表只写 39 行，**而且出处不会丢**。

> **成族的文案用表格，散落的文案用常量。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('**ProfileCsv 33 条 / Utilities 12 条待补**', 'ProfileCsv 已收 39 条（剩 2 条池中截断）/ Utilities 12 条待补')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
