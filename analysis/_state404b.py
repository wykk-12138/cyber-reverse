import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 404 轮·勘误：文件根本没乱码，是**控制台**在乱码

### 一、我错了

上一段我写"整份文件是乱码（早期脚本用非 UTF-8 写出）"。**这是错的。**

用字节级检查：

```
BINDING_BACKLOG.md   bytes: 3324  BOM: False   WHOLE FILE DECODES AS UTF-8 OK
line1 codepoints: 0x23 0x20 0x7ed1 0x5b9a 0x7f3a 0x53e3   ← "# 绑定缺口"
```

`0x7ed1 0x5b9a 0x7f3a 0x53e3` 就是"绑定缺口"。文件一直是**合法 UTF-8**。

### 二、为什么会看错

`Get-Content` 在这个控制台里把 UTF-8 中文渲染成 GBK 乱码 —— 连**从来没被我改过**的
`docs/METHOD.md`、`docs/GUI_BASELINE.md` 用同样方式读出来也是乱码。

**所以"看到乱码"只证明我的终端坏，不证明文件坏。**

### 三、这一轮真正修好的是什么

不是编码，是**内容过时**：旧账本里 `TaskView` 还列 6 项、`GroupSummary` 写着"三个语义未定"，
而这些从 R345 起就陆续落地了。重写后按 17 / 11 两个当前数字组织，并补了"已清零的类型 13 行"。

### 四、教训（并入 METHOD）

1. **判断文件编码只看字节**（`raw.decode('utf-8')`），不看终端显示；
2. 写中文文档不写 `-Encoding UTF8` 的 PowerShell 管道也可能在**显示**层出问题，但**写入**层是好的；
3. 我差点因为一次误诊，去"修"一个没坏的东西 —— **这也是本程第 N 次"证据来源没搞清"**。
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT corrigendum appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\METHOD.md'
t2 = io.open(p2, encoding='utf-8').read()
add2 = '''

### §16 终端显示乱码 ≠ 文件乱码（R404）

这个控制台把 UTF-8 中文渲染成 GBK 乱码，**连没被改过的文件也一样**。
我在 R404 因此误判"账本乱码"，差点去修一个没坏的文件。

规则：判断编码只看字节 —— `io.open(p,'rb').read().decode('utf-8')`；终端输出只当渲染结果。
'''
io.open(p2, 'w', encoding='utf-8', newline='').write(t2 + add2)
print('METHOD §16 added')
