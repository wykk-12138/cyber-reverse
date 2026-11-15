import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()
old = """        "find": 'inferred: no image evidence (R297)',
        "replace": 'no marker here',"""
new = """        "find": 'inferred: no image evidence (R297)',
        "replace": 'no marker here', "all": True,"""
assert old in t
t = t.replace(old, new, 1)
old2 = """        "find": 'inferred: no image evidence (R298)',
        "replace": 'no marker here',"""
new2 = """        "find": 'inferred: no image evidence (R298)',
        "replace": 'no marker here', "all": True,"""
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('all:true added to both')
