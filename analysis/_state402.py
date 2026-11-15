import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 402 轮：把 `SESSION_STATE.md` 从 3676 行清成 46 行

### 一、发现的问题

`SESSION_STATE.md` 里有 **176 个"最后更新"块** —— 每一轮我都往顶部插一段，
旧的从没删过。3676 行的"会话状态"，实际上已经没人能读。

### 二、处置

1. 原件整体留档：`docs/SESSION_STATE.archive.md`；
2. 重写成 46 行，只保留**当前**有效信息：

```
当前状态（套件 / UI 类 / 三类缺口）
数据目录（复刻件 vs 原版，R387 的教训）
证据可信度（哪些能信、哪些被污染过）
工具清单（9 个）
阻塞项（ida MCP / GUI 登录）
下一步（按价值排序的 4 条）
```

### 三、验证

```
文档守卫   61 通过 / 0 失败
```

### 四、这一轮的一句话

> 一份 3676 行的"状态文件"，和没有状态文件，效果差不多。

> **交接文档的价值与它的长度成反比。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')
