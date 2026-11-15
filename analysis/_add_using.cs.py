import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Services\SoundPlayer.cs'
t = io.open(p, encoding='utf-8').read()
if 'using System;' not in t:
    t = t.replace('using System.Runtime.InteropServices;', 'using System;\nusing System.Runtime.InteropServices;', 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('using System added')
else:
    print('using already present')
