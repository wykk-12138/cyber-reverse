import io
# Proxies: six strings
p1 = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Proxies\ProxyView.cs"
import os
if not os.path.exists(p1):
    p1 = None
    for dp, _d, fns in os.walk(r"D:\projects\cyber-reverse\replica\src"):
        for fn in fns:
            if fn == 'ProxyView.cs': p1 = os.path.join(dp, fn)
print('ProxyView:', p1)
t1 = io.open(p1, encoding='utf-8').read()
print('has class ProxyView:', 'class ProxyView' in t1, '| lines:', t1.count('\n'))
