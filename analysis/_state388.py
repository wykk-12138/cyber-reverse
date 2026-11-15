import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 388 轮：用"格式指纹"判定文件作者，把证据重新分了类

### 一、指纹

| 文件 | 缩进 | 换行 | 键风格 | 判定 |
|---|---|---|---|---|
| `settings.json` `tasks.json` `solvers.json` `accounts.json` `billing.json` `proxies.json` `analytics.json` `smartActions.json` | 2 空格 | **CRLF** | camelCase，冒号后有空格 | **复刻件写的**（Newtonsoft `Indented` 的 Windows 输出） |
| `checkoutHistory.json` | 无 | 无 | **PascalCase**，无空格 | 与复刻件同风格（`JsonConvert.SerializeObject` 裸调用）→ **可能也是复刻件** |
| `Backups\\*.cyb`（13 Nov） | **无** | **无** | camelCase，无空格 | **原版**（复刻件的备份是缩进版，不可能写出这种字节） |

### 二、结论

1. 我上一轮担心的"循环论证"**成立**：设置/任务/解算器那几份"实机文件"就是我自己写的；
2. **`.cyb` 备份是原版写的**（紧凑、camelCase）→ R384 的九个键**仍然成立**；
3. `checkoutHistory.json` 的 PascalCase 紧凑风格与复刻件的裸 `JsonConvert` 一致 → 不能当原版证据。

### 三、因此改了一处

备份现在也**紧凑写出**（`Formatting.None`），与 13 Nov 那批原版备份同字节风格：

```
{"proxies":[{"id":"…","name":"…",…
```

### 四、验证

```
完整套件   1545 通过 / 0 失败 / 2 跳过
```

（其中一次运行出现过 `HomePageParityTests` 单条失败，单独跑与重跑都通过 —— 记为可疑 flaky，继续观察。）

### 五、这一轮的一句话

> 同一个目录里混着两个程序写出来的文件，**我用缩进和大小写把它们分开了。**

> **证据要能追溯来源；不能追溯的"证据"，只是看起来像证据。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
lf = t2.replace('\r\n', '\n')
i = lf.index('最后更新：')
head = '''最后更新：第 388 轮（格式指纹判定文件作者；备份改为紧凑写出；证据重新分类）。

---

## 证据来源判定（用格式指纹）

| 证据 | 判定 | 结论 |
|---|---|---|
| `settings/tasks/solvers/accounts/billing/proxies/analytics/smartActions.json` | **复刻件自己写的** | 不能用作"实机"证据 |
| `checkoutHistory.json` | 与复刻件同风格 | 不能用作证据 |
| `Backups\\*.cyb`（13 Nov，紧凑 camelCase） | **原版写的** | `.cyb` 九键结论**成立** |
| 字符串池 / locale / 绑定表 | 从 exe 读的 | **始终可信** |

## 状态

```
完整套件   1545 通过 / 0 失败 / 2 跳过
缺口       17（名字级）/ 12（类型级）
观察       HomePageParityTests 曾偶发 1 次失败，重跑通过
```

'''
out = lf[:i] + head + lf[i:]
io.open(p2, 'w', encoding='utf-8', newline='').write(out)
print('SESSION_STATE updated', len(out))
