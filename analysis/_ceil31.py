import io, re
p = r'D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\BindingGapRatchetTests.cs'
t = io.open(p, encoding='utf-8').read()
t = re.sub(r'private const int MaxRealGap = \d+;', 'private const int MaxRealGap = 31;', t)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
p2 = r'D:\projects\cyber-reverse\replica\docs\BINDING_BACKLOG.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('当前 32 = 1 可做 + 31 结构', '当前 31 = 0 可做 + 31 结构（A 类清零）')
t2 = t2.replace('| `CheckoutView` | `OpenTracking` | 需要运单跟踪链接的来源 |',
                '| ~~`CheckoutView`~~ | ~~`OpenTracking`~~ | **R303 已实现**：`CheckoutOutcome.TrackingUrl` → `CheckoutEvent.TrackingUrl` → `Launcher` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('ceiling 32 -> 31, A class now empty')
