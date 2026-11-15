import io
p = r'D:\projects\cyber-reverse\replica\tools\backlog_report.py'
t = io.open(p, encoding='utf-8-sig').read()
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('BOM stripped')
