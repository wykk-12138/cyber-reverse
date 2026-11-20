"""R1291: record the first measured difference in the HTTP layer — the replica offers TLS 1.2 only.

Evidence in the artifact:
  * 146EB3A24  TLS_AES_128_GCM_SHA256
  * 146EB3A6C  TLS_AES_256_GCM_SHA384      <- TLS 1.3 suites, so the original can negotiate 1.3
  * 14716EEAC  tls: at most 2 GREASE extensions are supported   <- RFC 8701 GREASE is implemented, capped at two
  * 143159CBB / 1431662D3  BouncyCastle.Cryptography(.dll)      <- the same library this layer already uses

The comment does not change behaviour: switching the base class to BouncyCastle's TLS 1.3 client is its own change and
needs the getters around it moved too.
"""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Http/BouncyTls.cs'
text = io.open(P, encoding='utf-8').read()

old = """    protected override ProtocolVersion[] GetSupportedVersions()
        => new[] { ProtocolVersion.TLSv12 };"""

new = """    // R1291: the image carries TLS 1.3 suite names — TLS_AES_128_GCM_SHA256 (146EB3A24) and
    // TLS_AES_256_GCM_SHA384 (146EB3A6C) — so the original negotiates 1.3 where the server offers it. This client
    // offers 1.2 only, which is a measured difference, not a decision: DefaultTlsClient is BouncyCastle's pre-1.3 base
    // class, and moving to the 1.3 client moves the cipher-suite and extension getters with it. Recorded here so the
    // gap is visible from the code that has it; the same library (BouncyCastle.Cryptography, 143159CBB) is already in
    // use, and its GREASE support matches the image's own cap of two extensions (14716EEAC).
    protected override ProtocolVersion[] GetSupportedVersions()
        => new[] { ProtocolVersion.TLSv12 };"""

if old not in text:
    raise SystemExit('anchor missing')
io.open(P, 'w', encoding='utf-8', newline='\n').write(text.replace(old, new))
print('BouncyTls annotated')
