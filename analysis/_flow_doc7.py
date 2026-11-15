import io
p = r'D:\projects\cyber-reverse\replica\docs\FLOW_SEQUENCES.md'
t = io.open(p, encoding='utf-8').read()
add = '''
## 十三、用"复刻件当字典"去找归属：只确认了已知两条（R276）

思路：拿 18 条流水线的步骤名，去复刻件源码里数命中，看命中最多的是哪个文件。

| 段 | 步数 | 命中最多 |
|---|---|---|
| `0x034b14b8` | 15 | **`StoreFlowSteps.cs` 15 / 15** ← 已知的 structure-token-multi |
| `0x034b23a5` | 12 | **`StoreFlowSteps.cs` 12 / 12** ← structure-token-single |
| `0x03388fd2` | 8 | `StoreFlowSteps.cs` 8（**待复核**，见下） |
| `0x3371cea` | 15 | `StoreFlowSteps.cs` 9 / `StoreFlowRunner.cs` 8 |
| 其余 14 条 | — | 命中最多的是 **`StoreFlowRunner.cs`** —— 那是**通用步骤执行器**，里面本来就有一堆通用动作名 |

**结论**：这条路线只确认了已知的两条；其余 14 条命中的是通用执行器的词汇，**不构成归属证据**。

### 一个待复核项（不敢下结论）

`0x03388fd2` 在扫描里报"命中 `StoreFlowSteps.cs` 8 个"，但我随后在 `row_groups_wide.json` 里
**没再定位到这个基址**（可能只存在于保守版 `row_groups.json`，或基址打印格式不同）。
**记下来待复核**，不当成结论用。

### 所以"再找可标 Literal 的流"这条待办 → **关闭（否证）**

恢复集里的 18 条，除已知两条外都与复刻件的命名体系不重合 ——
说明它们属于**复刻件还没建模的商店**，而不是"标错来源"。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('FLOW_SEQUENCES.md: the dictionary route is recorded as a negative + one open item')
