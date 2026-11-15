import io
p = r'D:\projects\cyber-reverse\replica\docs\RESUME.md'
t = io.open(p, encoding='utf-8').read()
subs = [
 ('> 新会话从这里开始，不必翻 `VERDICT.md`（那是 97 万字节的编年史）。',
  '> 新会话从这里开始，不必翻 `VERDICT.md`（那是 124 万字节的编年史）。'),
 ('| 完整套件 | **1446 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R292 时点） |',
  '| 完整套件 | **1474 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R319 时点） |'),
 ('| 绑定缺口 | **33**（real = `MaxRealGap` = 账本标题） | whole-source + **剥注释** + 排除 `HasMultiple_NN`/`Value_NN` |',
  '| 绑定缺口 | **17**（real = `MaxRealGap` = 账本标题） | whole-source + **剥注释** + 排除 `HasMultiple_NN`/`Value_NN` |'),
 ('| 不可达 UI 类 | **29**（97 个中） | `UnreachedUiTypesTests` |',
  '| 不可达 UI 类 | **31**（104 个中） | `UnreachedUiTypesTests` |'),
 ('2. **跑一次全套**确认 1446+（R292 时点为 1446；条数会因为合并/新增断言而变，别把旧数字当基准）。',
  '2. **跑一次全套**确认 1474+（R319 时点为 1474；条数会因为合并/新增断言而变，别把旧数字当基准）。\n   低内存时用 `--no-build`（21 秒、内存只掉约 0.4 GB）。'),
 ('| `docs/BINDING_BACKLOG.md` | 33 个缺口按"A 类可做 / B 类结构"分类 |',
  '| `docs/BINDING_BACKLOG.md` | 17 个缺口（全部已判定：12 等价 / 3 不可得 / 2 内部） |\n| `docs/B_CLASS_DECISIONS.md` | 每个 B 类类型的判定 + 依据 |\n| `docs/CONTROL_DESIGN_*.md` | 已落地的控件设计稿（ComboBoxEdit / ProfileCsvRow / FilterRow 家族） |'),
]
for old, new in subs:
    assert old in t, old[:40]
    t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('RESUME synced to R319 numbers')
