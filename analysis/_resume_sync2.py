import io
p = r'D:\projects\cyber-reverse\replica\docs\RESUME.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('| 完整套件 | **1443 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R290 时点） |',
              '| 完整套件 | **1446 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R292 时点） |')
t = t.replace('2. **跑一次全套**确认 1443+（R290 时点为 1443；条数会因为合并/新增断言而变，别把旧数字当基准）。',
              '2. **跑一次全套**确认 1446+（R292 时点为 1446；条数会因为合并/新增断言而变，别把旧数字当基准）。')
if '错误目录' not in t:
    t = t.replace('## 3. 三件待办（按顺序）', '## 3. 已逐字对齐的两处（可以直接引用）\n\n- **八条流的步骤表**：每条都有字面量地址，`StoreFlowDigestTests` 钉住；\n- **错误目录 13 条**：标题与详情 **13/13 + 13/13 在池子里逐字命中**，`ErrorCatalogDigestTests` 钉住。\n\n## 4. 三件待办（按顺序）')
    t = t.replace('## 4. 已确认做不了（别再试）', '## 5. 已确认做不了（别再试）')
    t = t.replace('## 5. 五条硬纪律（都是踩出来的）', '## 6. 五条硬纪律（都是踩出来的）')
    t = t.replace('## 6. 内存纪律（用户强调过四次）', '## 7. 内存纪律（用户强调过四次）')
    t = t.replace('## 7. 地图', '## 8. 地图')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('RESUME synced to 1446 + the two verbatim-aligned areas')
