"""R1292 (final): the default transport is already the platform's, so the gap is only on the fallback path.

Three readings in three rounds, each narrower than the last, and the file that settles it is NetClient.cs:
  * R1291 said the image runs BouncyCastle TLS and the replica is 1.2-only -> wrong library call;
  * R1292 first corrected it to "platform transport, so the replica is a hand-written stack" -> still wrong, because it
    ignored TransportMode;
  * NetClient.Transport defaults to SChannel, which builds a SocketsHttpHandler — the same stack the image ships.

What is actually true: production traffic in the replica already goes through SslStream + SocketsHttpHandler, so TLS 1.3,
GREASE and HTTP/2 come from the platform there, as they do in the image. The hand-written stack is reachable only by
opting into OwnTls, and that path offers 1.2.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Http/BouncyTls.cs'
text = io.open(P, encoding='utf-8').read()

start = text.find('    // R1292 corrects R1291.')
if start < 0:
    raise SystemExit('annotation not found')
end = text.find('    protected override ProtocolVersion[] GetSupportedVersions()', start)
if end < 0:
    raise SystemExit('method not found')

note = """    // R1292, third reading, and the one the file that decides it supports: NetClient.Transport defaults to
    // TransportMode.SChannel, which builds a SocketsHttpHandler — the same platform stack the image ships
    // (1432D5FE6 SocketsHttpHandler, 1433D4B8A SslStream, 1436F9152 Http2StreamWindowManager, 146EA88EC
    // SocketsHttpHandler.Http2Support). On that path TLS 1.3, GREASE and HTTP/2 all come from the platform, in the
    // replica as in the image, so there is no gap to close there.
    //
    // This class is the OwnTls fallback. It is a hand-written stack that offers 1.2 only, reachable solely by opting in,
    // and its handshake bytes will never equal the platform's. R1291 read a BouncyCastle string beside a suite name and
    // concluded the image used this library for TLS; the suite names (146EB3A24 / 146EB3A6C) are SslStream's.
"""

text = text[:start] + note + text[end:]
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('note replaced')
