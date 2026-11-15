import io
p = r"D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding='utf-8').read()
first = t.index('最后更新：')
second = t.find('最后更新：', first + 1)
newest = t[first:second if second > 0 else len(t)]

clean = '''# 会话状态（第 402 轮重写；此前 175 个状态块已归档到 `SESSION_STATE.archive.md`）

本文件只保留**当前**状态。历史逐轮叙述在 `docs/VERDICT.md`，被替换掉的旧状态块在
`docs/SESSION_STATE.archive.md`。

## 当前状态

```
完整套件   1575 通过 / 0 失败 / 2 跳过
UI 类      104 声明 / 28 不可达
名字级缺口 17（tools/bind_diff.py）
类型级缺口 12（tools/bind_scope.py）
成员形状   272 处差异，已接受（tools/shape_audit.py）
文案缺口   Accounts/Proxies/Tasks/Profiles 四区清零；Settings 有 21 条"近似错误"待核对
```

## 数据目录（重要）

```
复刻件   %APPDATA%\\CybersoleReplica      （CYBERSOLE_DATA_ROOT 可覆盖）
原版     %APPDATA%\\Cybersole             （只读证据，永不写入）
```

R387 之前两者共用一个目录，导致"用实机文件核对模型"变成循环论证。

## 证据可信度

| 证据 | 状态 |
|---|---|
| 字符串池 / locale / 绑定表（`analysis/pe_strings.txt`） | ✅ 始终可信 |
| 原版 `.cyb` 备份（紧凑 camelCase） | ✅ 可信（R388 用格式指纹判定） |
| `settings.json` / `tasks.json` / `solvers.json` 等 | ❌ 曾被复刻件写入，不可作为"实机"证据 |
| GUI 实测记录（`docs/GUI_BASELINE.md`） | ✅ 可信（十个界面） |

## 工具（都在 `replica/tools/`）

| 工具 | 作用 |
|---|---|
| `bind_diff.py` | 名字级绑定缺口 |
| `bind_scope.py` | 类型级绑定缺口 |
| `bind_shape.py` / `shape_audit.py` | 成员形状（属性 vs 方法） |
| `locale_coverage.py` / `locale_text_gap.py` | 界面文案缺口（可归零） |
| `locale_near_miss.py` | "几乎对但不相等"的文案（需人工三分类） |
| `live_schema_diff.py` | 落盘 JSON 与模型的字段差 |
| `wire_candidates.py` | 未被构造的 UI 类 ↔ 绑定成员 |
| `snapshot.py` | 改结构前的源码快照 |

## 阻塞项

| 项 | 恢复条件 |
|---|---|
| ida MCP（`PROXY MISSING`） | 用户重启 DSH 或重开 IDA + 载入库 |
| 主界面 GUI 核对 | 需要登录账号；目前只能核对登录窗口 |

## 下一步（按价值排序）

1. 用 IDA 恢复后复核 `docs/DEVIATIONS.md` 第八节那四个"多余设置项"；
2. Settings 区 21 条近似错误逐条核对位置后修改；
3. 把前四个页面的文案常量接到控件上（TaskGroup 已示范）；
4. 12 个类型级缺口里，`TaskView.Toggle` 等仍无定论的项。

---

'''
io.open(p, 'w', encoding='utf-8', newline='').write(clean + newest.split('## 状态')[0].strip()[:0])
print('SESSION_STATE rewritten, bytes:', len(clean))
