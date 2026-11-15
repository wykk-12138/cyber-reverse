import io
p = r'D:\projects\cyber-reverse\replica\docs\RESUME.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| 完整套件 | **1442 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`，R280/R281 两次 |',
              '| 完整套件 | **1443 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R290 时点） |')
t = t.replace('| 字面量流 | 2 条 | `FlowSource.Literal` |',
              '| 字面量流 | **8 条全部**（每条都有地址） | `FlowSource.Literal` + `StoreFlowDigestTests` |')
t = t.replace('| 恢复的流水线 | 18 条 / 141 步 | A+B 布局合并去重 |',
              '| 恢复的流水线 | 18 条 / 141 步（复刻件已建模 8 条，均字面量可对账） | A+B 布局合并去重 |')
t = t.replace('**`python tools/mutation-check.py`** —— 全量 **24** 条，12–15 分钟，**期间不要做别的**。\n   目前只冒烟过 5 条（全 fired）。',
              '**`python tools/mutation-check.py`** —— 全量 **24** 条，12–15 分钟，**期间不要做别的**。\n   R286 已全量跑过一次：**24/24 全部 fired**（改前先 `python tools/mutation-audit.py` 查锚点）。')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('RESUME.md synced: 1443 / 8 flows / mutation 24-of-24 done')
