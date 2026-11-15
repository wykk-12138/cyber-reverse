import io
p = r'D:\projects\cyber-reverse\replica\docs\VERDICT.md'
t = io.open(p, encoding='utf-8').read()
add = '''
---

## 第 408 轮：计数文案的**零态**（"No X Loaded"）—— 三个页面只有两个对

### 一、locale 里有三态

```
Proxies.LoadedNone    No Proxies Loaded
Proxies.LoadedOne     1 Proxy Loaded
Proxies.LoadedFormat  {0} Proxies Loaded

Profiles.LoadedNone   No Profiles Loaded
Profiles.LoadedOne    1 Profile Loaded
Profiles.LoadedFormat {0} Profiles Loaded

Accounts.LoadedOne    1 Account Loaded
Accounts.LoadedFormat {0} Accounts Loaded      ← 没有 None 态
```

### 二、复刻件的对照

| 页面 | 三态实现 | 判定 |
|---|---|---|
| Proxies | `0 => "No Proxies Loaded"` / `1 => …` / `_ => …` | ✅ 早就对 |
| Profiles | 只有二态（0 会输出 `0 Profiles Loaded`） | ❌ → **本轮补上零态** |
| Accounts | locale 本身没有 None 态 | ✅ 二态正确 |

```csharp
public static string Loaded(int count) => count switch
{
    0 => LoadedNone,          // "No Profiles Loaded"
    1 => LoadedOne,           // "1 Profile Loaded"
    _ => string.Format(LoadedFormat, count),
};
```

### 三、验证

```
PageCopyTests / AccountCopyTests / EmptyView / CustomSizes   37 通过 / 0 失败
```

### 四、这一轮的一句话

> "0 Profiles Loaded" 不算错，但它不是原版说的话 —— **复数机器不会自己说出零态**。

> **一个 `switch` 少一个分支，界面上就多一句英文病句。**
'''
io.open(p, 'w', encoding='utf-8', newline='').write(t + add)
print('VERDICT appended')

p2 = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('文案缺口   Accounts/Proxies/Tasks/Profiles 四区清零；Settings 有 21 条"近似错误"待核对',
                '文案缺口   Accounts/Proxies/Tasks/Profiles 四区清零；计数文案零态已补齐；Settings 21 条近似错误待核对')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('SESSION_STATE updated')
