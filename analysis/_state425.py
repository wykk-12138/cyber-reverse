import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 425 轮：给九张文案表加卫生检查；机器已经连 `dotnet build` 都跑不动

### 一、加了什么

`CopyTablesHygieneTests`（3 条）：

1. **九张表里没有空字符串**；
2. 九张表合计 **≥ 187** 条（这个数是**从源码数出来的**：39+19+18+16+54+14+13+9+5 = 187）；
3. 每张表内 short name 不重复。

### 二、机器状态（这一轮真正的主题）

```
第一次跑：     2 通过 / 1 失败（阈值 200 太高，实际 187）→ 已改成 187
改完再跑：     MSB4184 System.OutOfMemoryException（NuGet.DefaultFrameworkNameProvider 构造失败）
available:     1.35 GB / Commit 93.91 of 94.03 GB
```

**连 MSBuild 的目标框架推断都起不来了。** 所以：

- 我把阈值改成实测的 187，**但无法再跑一次确认**（`dotnet build` 已不可用）；
- 文件括号平衡我用 Python 数过（`{}` 10/10、`()` 37/37），这只是"没写坏"的最低保证，**不是编译通过的证明**。

### 三、必须说清的结论

> 本轮新增的三条测试：**写过、没跑成**。

这不是新问题 —— R424 已经因为内存跑不完全量套件；这一轮连单项目构建都不行了。
**这台机器需要一次重启**，之后按 `SESSION_STATE.md` 的顺序补跑：

```
dotnet build src/Cybersole.Ui/Cybersole.Ui.csproj -c Debug
dotnet test --filter "FullyQualifiedName~CopyTablesHygieneTests"
dotnet test --filter "Speed!=Slow"
python tools/mutation-check.py
```

### 四、这一轮的一句话

> 我已经在这一轮里三次把"没跑成"和"通过"分开写 —— 因为这台机器的余量，已经不足以让我用跑测试来确认任何事。

> **当验证手段本身不可用时，唯一诚实的产出是"待验证清单"，而不是"完成"。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('## 未完成（需要重启机器）')
head = '''## ⚠ 现在机器已无法 `dotnet build`（R425）

```
available 1.35 GB / Commit 93.91 of 94.03 GB
dotnet test → MSB4184 System.OutOfMemoryException
```

**先重启机器。** 重启后按顺序补跑（前两条是本轮新增/改动的验证）：

```
dotnet build src/Cybersole.Ui/Cybersole.Ui.csproj -c Debug
dotnet test --filter "FullyQualifiedName~CopyTablesHygieneTests"
dotnet test --filter "Speed!=Slow"
python tools/mutation-check.py
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE flagged')
