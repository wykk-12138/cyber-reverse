import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 225 轮（挖出原版 XAML 绑定表 → `docs/xaml_bindings.json`：174 类型 / 819 成员；CustomBrowser 补齐 6 个成员；1417 绿）。

---

## 新证据源：XAML 绑定表（R225）

`docs/xaml_bindings.json` —— 从镜像 `0x0320b000` 区域的绑定描述符里抽出：
**174 个被 XAML 绑定的类型 + 819 个去重成员名**。格式 `Type,Cybersole.Member!Getter|Setter`。

- 和 locale 的区别：locale 说**显示**什么，这张表说**碰**什么。
- 已用它补全 `CustomBrowser`（原版 8 个成员，复刻件原有 2 个）。
- **待办清单**（按名字比对得出，改名实现的不算缺陷）：
  - `TaskView` 绑定 30 个，缺 `CopyUrl / CloneSelected / EditAll / DeleteSelected / CreateGroup / ForceStartSelected /
    LinkChange / MoveGroup / NextGroup / OpenBrowser / OpenGroupPopup / OpenSolvers / OpenStaggerStart /
    OpenTaskCreator / OpenTaskView / PinGroups / PreviousGroup / Quicktask / SetQuery / Toggle`
  - `ProxyView` 绑定 17 个，缺 `Test / TestAll / TestProxies / TestAllKeybind / ClearFailed / ClearOver /
    CloneProxies / CopyProxies / DeleteProxies / MoveGroup / OpenSettings / ProxyTesters`
- 守卫：`XamlBindingTableTests`（3 条）。

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('state updated', len(out))
