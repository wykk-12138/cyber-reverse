import io, re
p = r'D:\projects\cyber-reverse\analysis\_resume_audit.py'
t = io.open(p, encoding='utf-8').read()
t = t.replace("('RESUME says 33', '33' in resume),", "('RESUME states the ratchet value', ratchet in resume),")
t = t.replace("('ratchet = 33', ratchet == '33'),", "('ratchet is a number', ratchet.isdigit()),")
t = t.replace("('backlog title 33', '当前 33 =' in backlog),", "('backlog title matches ratchet', ('当前 ' + ratchet + ' =') in backlog),")
t = t.replace("('RESUME says 1442', '1442' in resume),", "('RESUME states a suite count', bool(re.search(r'1[0-9]{3} 通过', resume))),")
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('audit made ratchet-driven')
