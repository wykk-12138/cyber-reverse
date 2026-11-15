import io
p = r'D:\projects\cyber-reverse\replica\docs\XAML_BINDINGS.md'
t = io.open(p, encoding='utf-8').read()
t = t.replace('''**结论：真正需要"设计决策"的只有 C 类 12 个；B 类 30 个是照名字接线；A 类 12 个是噪音。**''',
'''**结论：真正需要"设计决策"的只有 C 类 12 个；B 类 30 个是照名字接线；A 类 12 个是噪音。**

`python tools\\bind_diff.py --buckets` 会直接给出这个分桶：

```
missing: 67     noise (HasMultiple_NN / Value_NN): 12     real gap: 55
```''')
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('doc notes the --buckets view')
