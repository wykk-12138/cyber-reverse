import io, re
p = r"D:\projects\cyber-reverse\replica\docs\RESUME.md"
t = io.open(p, encoding='utf-8').read()

subs = [
    ('| 完整套件 | **1474 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R319 时点） |',
     '| 完整套件 | **1575 通过 / 0 失败 / 2 跳过** | `dotnet test --filter "Speed!=Slow"`（R405 时点；R403 起内存不足时只用相关用例） |'),
    ('| 不可达 UI 类 | **28**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |',
     '| 不可达 UI 类 | **28**（104 个中，分母=Cybersole.Ui 所有 public class） | `UnreachedUiTypesTests` |\n| 类型级绑定缺口 | **11 个类型** | `python tools/bind_scope.py` |\n| 文案缺口 | Accounts/Proxies/Tasks/Profiles **四区清零**；Settings 21 条近似错误待核对 | `python tools/locale_text_gap.py` / `locale_near_miss.py` |'),
    ('1. **`python tools/mutation-check.py`** —— 全量 **24** 条，12–15 分钟，**期间不要做别的**。',
     '1. **`python tools/mutation-check.py`** —— 全量 **29** 条，12–15 分钟，**期间不要做别的**。'),
    ('2. **跑一次全套** 确认 1474+（R319 时点为 1474；条数会因为合并/新增断言而变，别把旧数当基准）。',
     '2. **跑一次全套** 确认 1575+（R405 时点为 1575；条数会因为合并/新增断言而变，别把旧数当基准）。'),
]
for old, new in subs:
    if old in t:
        t = t.replace(old, new, 1)
        print('updated:', old[:34])
    else:
        print('MISS:', old[:40])
io.open(p, 'w', encoding='utf-8', newline='').write(t)
