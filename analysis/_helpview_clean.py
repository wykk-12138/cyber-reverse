import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding='utf-8').read()
start = t.index('        void OpenLegacy(string url)')
# find the end of that local function: matching braces from the first '{' after start
depth = 0
i = start
while True:
    if t[i] == '{':
        depth += 1
    elif t[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1
# also drop the trailing newline
while end < len(t) and t[end] in '\r\n':
    end += 1
print('removing', repr(t[start:end])[:120])
t = t[:start] + t[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('dead local removed')
