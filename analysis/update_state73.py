import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\docs\SESSION_STATE.md"
t = io.open(p, encoding="utf-8").read()

subs = [
    ("最后更新：第 72 轮。", "最后更新：第 73 轮。"),
    ("| 测试（快，`Speed!=Slow`） | **792 通过 / 0 失败 / 2 跳过** | `dotnet test` |",
     "| 测试（快，`Speed!=Slow`） | **803 通过 / 0 失败 / 2 跳过** | `dotnet test` |"),
    ("| UI 类 | **88 个，41 个不可达** | `UnreachedUiTypesTests` |",
     "| UI 类 | **89 个，39 个不可达** | `UnreachedUiTypesTests` |"),
    ("**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R72）。",
     "**`verify.ps1 -Full` 是唯一的终判据。** 上一次跑：全 PASS（R73）。"),
    ("### C. 41 个不可达 UI 类", "### C. 39 个不可达 UI 类"),
]

for old, new in subs:
    if old not in t:
        raise SystemExit("missing: " + old[:50])
    t = t.replace(old, new, 1)

# Next steps: the three main pages are done; the remaining work is the details.
start = t.find("## 五、下一步候选（按价值排）")
end = t.find("## 六、命令")
if start < 0 or end < 0:
    raise SystemExit("next-step section not found")

new_next = """## 五、下一步候选（按价值排）

**三页（Accounts / Proxies / Tasks）的表都已按原版重做。** 剩下的不是「再来一页」，是**细节**：

1. **`PARITY.md` 里 R70–R73 记下的差额**：`Accounts.GroupsLoaded*`、`Accounts.EditPassword.*` 的文案、
   搜索无结果空态、`AccountSelectionMode.*`（Random / Match Profile + 两段说明）、
   `Tasks.Context.OpenBrowser`（没有浏览器桥）。
2. **`Tasks.Modals.*` 那四个弹窗**：`StaggerStartView`（已有类，未接 Context.StaggerStart）、
   `GroupSummary`、`TaskGroupView`、`TaskCreatorView` 的收尾。
3. **继续 GUI 走查没点过的页**：`Settings → Data`、`Settings → Advanced → Captcha Providers`、
   `Settings → Webhooks`。这三页一个都没点过。
4. **Nike 的 8 步结账** —— 仍然卡在段名，字符串 → xref 这条路在 NativeAOT 上不通（§三）。

"""
t = t[:start] + new_next + t[end:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("SESSION_STATE updated for R73")
