import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 327 轮（**标记 blocked**：可用内存连续 20+ 轮低于 8 GB 硬线，需用户重启才能继续编码/测试）。

---

## 为什么停在这里（具体、可核验）

| 事实 | 值 |
|---|---|
| 可用物理内存 | **4.56 GB**（硬线 8 GB） |
| Commit | 44.4 GB |
| 连续低于硬线的轮次 | **20+**（自 R301 起） |
| 本侧残留进程 | 无（dotnet / chrome / Cybersole / ida 均为 0） |
| 已尝试 | `dotnet build-server shutdown`（每轮都跑）、改用 `--no-build` 跑套件、纯文档/脚本轮次 |
| 剩余工作全部需要编译 | ① `GoatAccountApi` 四端点实现 ② 全量 mutation-check（29 条） ③ GUI 交叉验证 |

**轻活已做尽**：五份权威文档、七个工具、三组机器对账（账本↔棘轮 / 简报↔产物 / 文档↔源码）、
三份控件设计稿、两份功能设计稿、GOAT 四端点施工图（已修正虚构依赖）。

## 重启后的执行顺序（不要改）

1. `python tools/mutation-audit.py`（29 锚点是否还活）→ `python tools/mutation-check.py`（全量，约 15 分钟）；
2. `dotnet test --filter "Speed!=Slow"` —— 确认 **1474+**；
3. 按 `docs/CONTROL_DESIGN_GoatAccount.md` 实现 GOAT 的 `login` / `send_otp_token` / `addresses` / `billing_infos`
   （路径全有出处，请求体标 `inferred`）。

## 交接数字

```
完整套件   1474 通过 / 0 失败 / 2 跳过（R322）
绑定缺口   17（real = ceiling = 账本标题）；A 类清零
UI 类      104 声明 / 31 不可达（PARITY.md 的 84 是另一个分母）
mutation   29 条 / 锚点 29/29
端点账     89 = 67 有证据 + 18 标推断（10 条真发送）
流水线     18 条 / 141 步；8 条复刻件流全部字面量可对账
```

'''
out = lf[:i] + head + lf[i:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE: blocker recorded', len(out))
