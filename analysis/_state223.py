import io
p = r'D:\projects\cyber-reverse\replica\docs\SESSION_STATE.md'
t = io.open(p, encoding='utf-8').read()
lf = t.replace('\r\n', '\n')
i = lf.index('最后更新：')
j = lf.index('## 已测出的几何账本')
head = '''最后更新：第 223 轮（Billing 五列比例 1.00/1.28/1.29/1.00 实测得出；复刻件原来是五个等分；1411 绿）。

---

'''.replace('\\\\', '\\')
t2 = lf[:i] + head + lf[j:]
# refresh the geometry ledger with the billing row + the open question
t2 = t2.replace('| Tasks 表 Status 列 | **量不出来**（空表时吸收余量） | 已写进注释与测试 |',
'''| Tasks 表 Status 列 | **量不出来**（空表时吸收余量） | 已写进注释与测试 |
| Billing 五列 | Profile 1.00 : Email 1.28 : Card Holder 1.29 : Card 1.00 : Shipping（余量） | 两个窗口宽度读表头左边界 |

**待查（有观测无结论）**：Billing 表整张在窗口变窄时右移约 54 px，与"左栏固定 + 星号分列"的预期不符，
怀疑某列有 `MinWidth` 导致溢出重排。没有证据前不动。''')
io.open(p, 'w', encoding='utf-8', newline='').write(t2)
print('state updated', len(t2))
