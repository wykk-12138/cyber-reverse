import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 71 轮。", "最后更新：第 72 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **777 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **792 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("| UI 类 | **87 个，41 个不可达** | `UnreachedUiTypesTests` |",
     "| UI 类 | **88 个，41 个不可达** | `UnreachedUiTypesTests` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R71）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R72）。"),
]

for old, new in subs:
    if old not in t:
        raise SystemExit("missing anchor: " + old[:50])
    t = t.replace(old, new, 1)

# Remaining work: proxies is done, tasks is next.
old_next = """## 五、下一步候选（按价值排）

1. **同一套拆分照搬到 Profiles / Proxies / Tasks**。R71 在 Accounts 上做的事（左栏分组 + 单组分页 +
   选择模型 + 表头排序 + 行内操作）在原版这三页是**同一个形状**，locale 里
   `Profiles.SelectedOne/Many`、`Proxies.SelectedOne/Many`、`Tasks.SelectedOne/Many` 都在。
   原版视图名见 `docs/ORIGINAL_VIEWS.md`。"""
new_next = """## 五、下一步候选（按价值排）

1. **Tasks 页**（最后一页）。`TASK GROUPS` 左栏 + 排序（`TaskGroups.Order.*` 六种）+ 计数 +
   `Tasks.Context.*` 十一个菜单项 + `Tasks.Column.Site/Product/Profile/Proxies/Status`。
   原版视图名 `Tasks.TaskView` / `Tasks.Modals.*`。Profiles 没有独立导航项，`Profiles.*` 大概率是
   Tasks 里的一个子页或弹窗，**先去 GUI 里确认它在哪再动手**。"""
if old_next not in t:
    raise SystemExit("next-step block missing")
t = t.replace(old_next, new_next, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE updated")
