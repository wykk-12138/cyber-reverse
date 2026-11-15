import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\BillingView.cs'
t = io.open(p, encoding='utf-8').read()
old = '''        }
        }
        finally { _refreshing = false; }
    }
'''
new = '''        }
    }
'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('guard tail removed')
