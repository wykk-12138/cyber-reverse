"""R1293: finish the correction by naming the line that settles TLS 1.3 in the default path.

NetClient's handler sets EnabledSslProtocols = Tls12 | Tls13, so the default transport negotiates 1.3 and R1291's "the
replica is 1.2 only" is true only of the OwnTls fallback. Six handler properties are now listed in one place so the HTTP
layer does not have to be re-measured from scratch next time.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Http/BouncyTls.cs'
text = io.open(P, encoding='utf-8').read()

anchor = '    // This class is the OwnTls fallback.'
extra = """    // R1293 closes the question: NetClient's handler sets EnabledSslProtocols = Tls12 | Tls13, MaxAutomaticRedirections
    // = 10, CipherSuitesPolicy from the profile, ApplicationProtocols from the profile's ALPN, AutomaticDecompression =
    // All and UseCookies = true — six properties, each the platform's own name for the same thing the image uses, so the
    // default path already matches on TLS version, TLS policy, ALPN, redirect cap, decompression and cookies.
    //
"""

if anchor not in text:
    raise SystemExit('anchor missing')
text = text.replace(anchor, extra + anchor, 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('note extended')
