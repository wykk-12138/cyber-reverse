import io
p = r"D:\projects\cyber-reverse\replica\tools\live_schema_diff.py"
t = io.open(p, encoding='utf-8').read()
old = "            props = sorted(set(re.findall(r'public\\s+[\\w<>,\\[\\]\\?\\.]+\\s+(\\w+)\\s*\\{\\s*get', body)))"
new = ("            # both property shapes: accessor blocks and expression-bodied (\"public int Running => …\");\n"
       "            # the first version of this tool only matched the former and reported a present member as missing.\n"
       "            props = sorted(set(re.findall(r'public\\s+[\\w<>,\\[\\]\\?\\.]+\\s+(\\w+)\\s*(?:\\{\\s*get|=>)', body)))")
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('tool now sees expression-bodied properties too')
