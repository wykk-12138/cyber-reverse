import io
R = r'D:\projects\cyber-reverse\replica'

# 1) StoreGroupModal is now constructed by EditStoreGroup
p = R + r'\tests\Cybersole.Tests\UnreachedUiTypesTests.cs'
t = io.open(p, encoding='utf-8').read()
old = '        "StaggerStartView", "StoreGroupModal", "UtilitiesView", "YoutubeWindow",'
new = '''        // R231: StoreGroupModal is constructed by UtilitiesView.EditStoreGroup (the bound EditStoreGroup command).
        "StaggerStartView", "UtilitiesView", "YoutubeWindow",'''
assert old in t, 'baseline line'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('baseline: StoreGroupModal removed')

# 2) the guide count follows the scan
p2 = R + r'\docs\VERDICT.md'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace('| UI 类 | 97 个，**36 个不可达**（37%） | `UnreachedUiTypesTests` |',
                '| UI 类 | 97 个，**35 个不可达**（36%） | `UnreachedUiTypesTests` |')
io.open(p2, 'w', encoding='utf-8', newline='').write(t2)
print('guide: 97 / 35')
