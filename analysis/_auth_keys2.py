import io, re
raw = io.open('analysis/pe_strings.txt', encoding='utf-8', errors='replace').read()
for k in ('Auth.Login.Subtitle','Auth.Welcome','Auth.Login.UseCode','Auth.Login.Waiting','Auth.Login.CodePrompt','Auth.Login.Title'):
    m = re.search(r'"' + re.escape(k) + r'":\s*"([^"]{0,80})"', raw)
    print('%-26s => %s' % (k, m.group(1) if m else '(no value / key absent)'))
