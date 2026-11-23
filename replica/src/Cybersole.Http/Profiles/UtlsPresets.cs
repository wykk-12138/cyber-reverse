namespace Cybersole.Http.Profiles;

/// <summary>
/// All 82 browser fingerprint ClientProfile slots and all 68 ClientHelloSpec builders
/// from Cybersole.Http 0.10.0 (UtlsPresets, sub_1412B05A0..sub_14135AFD0).
/// </summary>
public static class UtlsPresets
{
    // ---- Shared immutable TLS arrays ----
    private static readonly IReadOnlyList<ushort> Ciphers_0 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_DHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_DHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_1 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_2 = Array.AsReadOnly(new ushort[] { CipherSuiteId.GreasePlaceholder, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_3 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_4 = Array.AsReadOnly(new ushort[] { CipherSuiteId.GreasePlaceholder, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_5 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_EMPTY_RENEGOTIATION_INFO_SCSV });
    private static readonly IReadOnlyList<ushort> Ciphers_6 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_3DES_EDE_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_7 = Array.AsReadOnly(new ushort[] { CipherSuiteId.GreasePlaceholder, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_8 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_9 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_10 = Array.AsReadOnly(new ushort[] { CipherSuiteId.GreasePlaceholder, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_3DES_EDE_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_11 = Array.AsReadOnly(new ushort[] { CipherSuiteId.GreasePlaceholder, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_3DES_EDE_CBC_SHA });
    private static readonly IReadOnlyList<ushort> Ciphers_12 = Array.AsReadOnly(new ushort[] { CipherSuiteId.TLS_AES_128_GCM_SHA256, CipherSuiteId.TLS_AES_256_GCM_SHA384, CipherSuiteId.TLS_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_128_GCM_SHA256, CipherSuiteId.TLS_RSA_WITH_AES_256_GCM_SHA384, CipherSuiteId.TLS_RSA_WITH_AES_128_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_AES_256_CBC_SHA, CipherSuiteId.TLS_RSA_WITH_3DES_EDE_CBC_SHA });

    private static readonly IReadOnlyList<ushort> Groups_0 = Array.AsReadOnly(new ushort[] { NamedGroupId.X25519MLKEM768, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1, NamedGroupId.Secp521r1, NamedGroupId.Ffdhe2048, NamedGroupId.Ffdhe3072 });
    private static readonly IReadOnlyList<ushort> Groups_1 = Array.AsReadOnly(new ushort[] { NamedGroupId.GreasePlaceholder, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1 });
    private static readonly IReadOnlyList<ushort> Groups_2 = Array.AsReadOnly(new ushort[] { NamedGroupId.GreasePlaceholder, NamedGroupId.X25519MLKEM768, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1 });
    private static readonly IReadOnlyList<ushort> Groups_3 = Array.AsReadOnly(new ushort[] { NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1, NamedGroupId.Secp521r1, NamedGroupId.Ffdhe2048, NamedGroupId.Ffdhe3072 });
    private static readonly IReadOnlyList<ushort> Groups_4 = Array.AsReadOnly(new ushort[] { NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1 });
    private static readonly IReadOnlyList<ushort> Groups_5 = Array.AsReadOnly(new ushort[] { NamedGroupId.GreasePlaceholder, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1, NamedGroupId.Secp521r1 });
    private static readonly IReadOnlyList<ushort> Groups_6 = Array.AsReadOnly(new ushort[] { NamedGroupId.Secp256r1 });
    private static readonly IReadOnlyList<ushort> Groups_7 = Array.AsReadOnly(new ushort[] { NamedGroupId.Secp256r1, NamedGroupId.Secp384r1, NamedGroupId.Secp521r1 });
    private static readonly IReadOnlyList<ushort> Groups_8 = Array.AsReadOnly(new ushort[] { NamedGroupId.GreasePlaceholder, NamedGroupId.X25519Kyber768Draft00, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1 });
    private static readonly IReadOnlyList<ushort> Groups_9 = Array.AsReadOnly(new ushort[] { NamedGroupId.GreasePlaceholder, NamedGroupId.X25519MLKEM768, NamedGroupId.X25519, NamedGroupId.Secp256r1, NamedGroupId.Secp384r1, NamedGroupId.Secp521r1 });

    private static readonly IReadOnlyList<ushort> SigAlgs_0 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.EcdsaSha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_1 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.EcdsaSha1, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_2 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512 });
    private static readonly IReadOnlyList<ushort> SigAlgs_3 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_4 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512 });
    private static readonly IReadOnlyList<ushort> SigAlgs_5 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_6 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSha1, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_7 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.Ed25519, SignatureSchemeId.Ed448, SignatureSchemeId.RsaPssPssSha256, SignatureSchemeId.RsaPssPssSha384, SignatureSchemeId.RsaPssPssSha512, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.EcdsaSha224, SignatureSchemeId.EcdsaSha1, SignatureSchemeId.RsaPkcs1Sha224, SignatureSchemeId.RsaPkcs1Sha1, SignatureSchemeId.DsaSha224, SignatureSchemeId.DsaSha1, SignatureSchemeId.DsaSha256, SignatureSchemeId.DsaSha384, SignatureSchemeId.DsaSha512 });
    private static readonly IReadOnlyList<ushort> SigAlgs_8 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_9 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.EcdsaSecp521r1Sha512, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPkcs1Sha224, SignatureSchemeId.EcdsaSha224, SignatureSchemeId.RsaPkcs1Sha1, SignatureSchemeId.EcdsaSha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_10 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.GreasePlaceholder, SignatureSchemeId.MlDsa44, SignatureSchemeId.MlDsa65, SignatureSchemeId.MlDsa87, SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512 });
    private static readonly IReadOnlyList<ushort> SigAlgs_11 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.MlDsa44, SignatureSchemeId.MlDsa65, SignatureSchemeId.MlDsa87, SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512 });
    private static readonly IReadOnlyList<ushort> SigAlgs_12 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });
    private static readonly IReadOnlyList<ushort> SigAlgs_13 = Array.AsReadOnly(new ushort[] { SignatureSchemeId.EcdsaSecp256r1Sha256, SignatureSchemeId.RsaPssRsaeSha256, SignatureSchemeId.RsaPkcs1Sha256, SignatureSchemeId.EcdsaSecp384r1Sha384, SignatureSchemeId.EcdsaSha1, SignatureSchemeId.RsaPssRsaeSha384, SignatureSchemeId.RsaPkcs1Sha384, SignatureSchemeId.RsaPssRsaeSha512, SignatureSchemeId.RsaPkcs1Sha512, SignatureSchemeId.RsaPkcs1Sha1 });

    private static readonly IReadOnlyList<ushort> Versions_0 = Array.AsReadOnly(new ushort[] { TlsVersion.Tls13, TlsVersion.Tls12 });
    private static readonly IReadOnlyList<ushort> Versions_1 = Array.AsReadOnly(new ushort[] { TlsExtensionType.GreasePlaceholder, TlsVersion.Tls13, TlsVersion.Tls12 });
    private static readonly IReadOnlyList<ushort> Versions_2 = Array.AsReadOnly(new ushort[] { TlsExtensionType.GreasePlaceholder, TlsVersion.Tls13, TlsVersion.Tls12, TlsVersion.Tls11, TlsVersion.Tls10 });

    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_0 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.X25519MLKEM768, 0), new KeyShareEntry(NamedGroupId.X25519, 0), new KeyShareEntry(NamedGroupId.Secp256r1, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_1 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.X25519MLKEM768, 0), new KeyShareEntry(NamedGroupId.X25519, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_2 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.GreasePlaceholder, 1), new KeyShareEntry(NamedGroupId.X25519, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_3 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.GreasePlaceholder, 1), new KeyShareEntry(NamedGroupId.X25519MLKEM768, 0), new KeyShareEntry(NamedGroupId.X25519, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_4 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.X25519, 0), new KeyShareEntry(NamedGroupId.Secp256r1, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_5 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.X25519, 0) });
    private static readonly IReadOnlyList<KeyShareEntry> KeyShares_6 = Array.AsReadOnly(new[] { new KeyShareEntry(NamedGroupId.GreasePlaceholder, 1), new KeyShareEntry(NamedGroupId.X25519Kyber768Draft00, 0), new KeyShareEntry(NamedGroupId.X25519, 0) });

    private static readonly IReadOnlyList<string> Alpn_0 = Array.AsReadOnly(new[] { "h2", "http/1.1" });
    private static readonly IReadOnlyList<string> Alpn_1 = Array.AsReadOnly(new[] { "h2" });
    private static readonly IReadOnlyList<string> Alpn_2 = Array.AsReadOnly(new[] { "http/1.1" });
    private static readonly IReadOnlyList<string> Alpn_3 = Array.AsReadOnly(Array.Empty<string>());
    private static readonly IReadOnlyList<string> Alpn_4 = Array.AsReadOnly(new[] { "h3", "h2" });
    private static readonly IReadOnlyList<string> Alpn_5 = Array.AsReadOnly(new[] { "h3", "h2", "http/1.1" });

    private static readonly IReadOnlyList<CertCompressionAlgorithm> CertComp_0 = Array.AsReadOnly(new[] { CertCompressionAlgorithm.Zlib, CertCompressionAlgorithm.Brotli, CertCompressionAlgorithm.Zstd });
    private static readonly IReadOnlyList<CertCompressionAlgorithm> CertComp_1 = Array.AsReadOnly(new[] { CertCompressionAlgorithm.Brotli });
    private static readonly IReadOnlyList<CertCompressionAlgorithm> CertComp_2 = Array.AsReadOnly(new[] { CertCompressionAlgorithm.Zlib });

    private static readonly IReadOnlyList<byte> Bytes_0 = Array.AsReadOnly(new byte[] { 0 });
    private static readonly IReadOnlyList<byte> Bytes_1 = Array.AsReadOnly(new byte[] { 1 });
    private static readonly IReadOnlyList<byte> Bytes_2 = Array.AsReadOnly(new byte[] { 0, 1, 2 });

    // ---- Shared immutable HTTP/2 arrays ----
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_0 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.EnablePush, 0u), (Http2SettingId.InitialWindowSize, 131072u), (Http2SettingId.MaxFrameSize, 16384u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_1 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.EnablePush, 0u), (Http2SettingId.InitialWindowSize, 6291456u), (Http2SettingId.MaxHeaderListSize, 262144u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_2 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.EnablePush, 0u), (Http2SettingId.InitialWindowSize, 131072u), (Http2SettingId.MaxFrameSize, 16384u), (Http2SettingId.NoRfc7540Priorities, 1u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_3 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.InitialWindowSize, 131072u), (Http2SettingId.MaxFrameSize, 16384u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_4 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 4096u), (Http2SettingId.MaxConcurrentStreams, 4294967295u), (Http2SettingId.InitialWindowSize, 16777216u), (Http2SettingId.MaxFrameSize, 16384u), (Http2SettingId.MaxHeaderListSize, 4294967295u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_5 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 4096u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.MaxFrameSize, 16384u), (Http2SettingId.MaxHeaderListSize, 4294967295u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_6 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 4096u), (Http2SettingId.EnablePush, 1u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.MaxFrameSize, 16384u), (Http2SettingId.MaxHeaderListSize, 4294967295u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_7 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.MaxConcurrentStreams, 1000u), (Http2SettingId.InitialWindowSize, 6291456u), (Http2SettingId.MaxHeaderListSize, 262144u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_8 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 4096u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.InitialWindowSize, 2097152u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_9 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.InitialWindowSize, 16777216u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_10 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.HeaderTableSize, 65536u), (Http2SettingId.EnablePush, 0u), (Http2SettingId.MaxConcurrentStreams, 1000u), (Http2SettingId.InitialWindowSize, 6291456u), (Http2SettingId.MaxHeaderListSize, 262144u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_11 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.InitialWindowSize, 4194304u), (Http2SettingId.MaxConcurrentStreams, 100u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_12 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.MaxConcurrentStreams, 100u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_13 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.EnablePush, 0u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.MaxConcurrentStreams, 100u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_14 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.EnablePush, 0u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.NoRfc7540Priorities, 1u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_15 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.EnablePush, 0u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.EnableConnectProtocol, 1u), (Http2SettingId.NoRfc7540Priorities, 1u) });
    private static readonly IReadOnlyList<(ushort Id, uint Value)> H2Settings_16 = Array.AsReadOnly(new (ushort, uint)[] { (Http2SettingId.EnablePush, 0u), (Http2SettingId.InitialWindowSize, 2097152u), (Http2SettingId.MaxConcurrentStreams, 100u), (Http2SettingId.NoRfc7540Priorities, 1u) });

    private static readonly IReadOnlyList<string> Pseudo_0 = Array.AsReadOnly(new[] { ":method", ":path", ":authority", ":scheme" });
    private static readonly IReadOnlyList<string> Pseudo_1 = Array.AsReadOnly(new[] { ":method", ":authority", ":scheme", ":path" });
    private static readonly IReadOnlyList<string> Pseudo_2 = Array.AsReadOnly(new[] { ":method", ":scheme", ":path", ":authority" });
    private static readonly IReadOnlyList<string> Pseudo_3 = Array.AsReadOnly(new[] { ":method", ":scheme", ":authority", ":path" });

    private static readonly IReadOnlyList<Http2PriorityFrame> PriorityFrames_0 = Array.AsReadOnly(new[] { new Http2PriorityFrame(3u, 0u, false, 200), new Http2PriorityFrame(5u, 0u, false, 100), new Http2PriorityFrame(7u, 0u, false, 0), new Http2PriorityFrame(9u, 7u, false, 0), new Http2PriorityFrame(11u, 3u, false, 0), new Http2PriorityFrame(13u, 0u, false, 240) });

    private static readonly SniExtension SharedSni = new();
    private static readonly ExtendedMasterSecretExtension SharedEms = new();
    private static readonly RenegotiationInfoExtension SharedReneg0 = new(ConstructorArg: 0);
    private static readonly RenegotiationInfoExtension SharedReneg1 = new(ConstructorArg: 1);
    private static readonly SessionTicketExtension SharedSessionTicket = new();
    private static readonly StatusRequestExtension SharedStatusRequest = new();
    private static readonly SignedCertificateTimestampExtension SharedSct = new();
    private static readonly PaddingExtension SharedBoringPadding = new(PaddingExtension.BoringPaddingTarget);
    private static readonly EncryptThenMacExtension SharedEncryptThenMac = new();
    private static readonly PreSharedKeyExtension SharedPreSharedKey = new();
    private static readonly GreaseExtension SharedGrease = new();

    // ---- GREASE & BoringPadding helpers ----
    public static GreaseSet GenerateGreaseSet(Random? random = null) => GreaseHelper.GenerateSet(random);
    public static ClientHelloSpec ResolveGrease(ClientHelloSpec spec, Random? random = null) => GreaseHelper.ResolveGrease(spec, random);
    public static int CalculateBoringPadding(int unpaddedHandshakeLength, int targetLength = PaddingExtension.BoringPaddingTarget)
        => PaddingExtension.CalculatePaddingBytes(unpaddedHandshakeLength, targetLength);

    // ---- All 68 ClientHelloSpec builders (5.1..5.68) ----
    /// <summary>Builder 5.1 (0x1412B9F20): Shared Chrome QUIC ClientHello.</summary>
    public static ClientHelloSpec BuildChromeQuicSpec() => ChromeQuicSpecs.CreateClientHelloSpec();

    /// <summary>Builder 5.2 (0x141340610): Firefox_148 (#1).</summary>
    public static ClientHelloSpec BuildFirefox_148Spec() => new(
        CipherSuites: Ciphers_0,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            SharedSct,
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.3 (0x141340FC0): Firefox_147 (#2).</summary>
    public static ClientHelloSpec BuildFirefox_147Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_2),
            SharedSct,
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_3),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.4 (0x141341980): Firefox_147_PSK (#3).</summary>
    public static ClientHelloSpec BuildFirefox_147_PSKSpec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_2),
            new KeyShareExtension(KeyShares_1),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_3),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.5 (0x141342360): Firefox_146_PSK (#4).</summary>
    public static ClientHelloSpec BuildFirefox_146_PSKSpec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            SharedSct,
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.6 (0x141342DB0): Firefox_135 (#5).</summary>
    public static ClientHelloSpec BuildFirefox_135Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            SharedSct,
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.7 (0x141343690): Firefox_133 (#6).</summary>
    public static ClientHelloSpec BuildFirefox_133Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.8 (0x141343F40): Chrome_130_PSK (#7).</summary>
    public static ClientHelloSpec BuildChrome_130_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            GreaseEchExtension.ChromePreset,
            SharedReneg1,
            SharedSct,
            new CompressCertificateExtension(CertComp_1),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SupportedGroupsExtension(Groups_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new EcPointFormatsExtension(Bytes_0),
            new KeyShareExtension(KeyShares_2),
            SharedSessionTicket,
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedSni,
            SharedEms,
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.9 (0x1413448B0): Chrome_131_PSK (#8).</summary>
    public static ClientHelloSpec BuildChrome_131_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            GreaseEchExtension.ChromePreset,
            SharedReneg1,
            SharedSct,
            new CompressCertificateExtension(CertComp_1),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SupportedGroupsExtension(Groups_2),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new EcPointFormatsExtension(Bytes_0),
            new KeyShareExtension(KeyShares_3),
            SharedSessionTicket,
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedSni,
            SharedEms,
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.10 (0x141345280): Chrome_131 (#9).</summary>
    public static ClientHelloSpec BuildChrome_131Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            GreaseEchExtension.ChromePreset,
            SharedReneg1,
            SharedSct,
            new CompressCertificateExtension(CertComp_1),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SupportedGroupsExtension(Groups_2),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new EcPointFormatsExtension(Bytes_0),
            new KeyShareExtension(KeyShares_3),
            SharedSessionTicket,
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedSni,
            SharedEms,
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.11 (0x141345C20): Firefox_132 (#10).</summary>
    public static ClientHelloSpec BuildFirefox_132Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_0),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_0),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new RecordSizeLimitExtension(16385),
            new CompressCertificateExtension(CertComp_0),
            GreaseEchExtension.Firefox132PlusPreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.12 (0x1413464D0): Firefox_123 (#11).</summary>
    public static ClientHelloSpec BuildFirefox_123Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            GreaseEchExtension.ChromePreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.13 (0x141346CE0): Firefox_120 (#12).</summary>
    public static ClientHelloSpec BuildFirefox_120Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new RecordSizeLimitExtension(16385),
            GreaseEchExtension.ChromePreset,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.14 (0x141347420): ZalandoAndroidMobile (#13).</summary>
    public static ClientHelloSpec BuildZalandoAndroidMobileSpec() => new(
        CipherSuites: Ciphers_3,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            SharedSct,
            new KeyShareExtension(KeyShares_5),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_0),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.15 (0x141347B30): ZalandoIosMobile (#14).</summary>
    public static ClientHelloSpec BuildZalandoIosMobileSpec() => new(
        CipherSuites: Ciphers_4,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.16 (0x1413483C0): NikeIosMobile (#15).</summary>
    public static ClientHelloSpec BuildNikeIosMobileSpec() => new(
        CipherSuites: Ciphers_4,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.17 (0x141348C50): NikeAndroidMobile (#16).</summary>
    public static ClientHelloSpec BuildNikeAndroidMobileSpec() => new(
        CipherSuites: Ciphers_3,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_0),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.18 (0x1413493C0): CloudflareCustom (#17).</summary>
    public static ClientHelloSpec BuildCloudflareCustomSpec() => new(
        CipherSuites: Ciphers_5,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            new EcPointFormatsExtension(Bytes_2),
            new SupportedGroupsExtension(Groups_6),
            SharedSessionTicket,
            new AlpnExtension(Alpn_2),
            SharedEncryptThenMac,
            SharedEms,
            new SignatureAlgorithmsExtension(SigAlgs_7),
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.19 (0x1413497D0): MMSIos (#18).</summary>
    public static ClientHelloSpec BuildMMSIosSpec() => new(
        CipherSuites: Ciphers_6,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            new KeyShareExtension(KeyShares_5),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_0),
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.20 (0x141349D40): MeshIos (#19).</summary>
    public static ClientHelloSpec BuildMeshIosSpec() => new(
        CipherSuites: Ciphers_4,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.21 (0x14134A5D0): MeshAndroid (#20).</summary>
    public static ClientHelloSpec BuildMeshAndroidSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_3),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.22 (0x14134AEC0): MeshIos2 (#21).</summary>
    public static ClientHelloSpec BuildMeshIos2Spec() => new(
        CipherSuites: Ciphers_7,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.23 (0x14134B750): MeshAndroid2 (#22).</summary>
    public static ClientHelloSpec BuildMeshAndroid2Spec() => new(
        CipherSuites: Ciphers_8,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg1,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            SharedStatusRequest,
            new AlpnExtension(Alpn_2),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_4),
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.24 (0x14134BB90): ConfirmedIos (#23).</summary>
    public static ClientHelloSpec BuildConfirmedIosSpec() => new(
        CipherSuites: Ciphers_4,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.25 (0x14134C420): ConfirmedAndroid (#24).</summary>
    public static ClientHelloSpec BuildConfirmedAndroidSpec() => new(
        CipherSuites: Ciphers_9,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg0,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_4),
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.26 (0x14134C870): ConfirmedAndroid2 (#25).</summary>
    public static ClientHelloSpec BuildConfirmedAndroid2Spec() => new(
        CipherSuites: Ciphers_9,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg0,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_4),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.27 (0x14134CDD0): Okhttp4Android10 (#26).</summary>
    public static ClientHelloSpec BuildOkhttp4Android10Spec() => new(
        CipherSuites: Ciphers_3,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg0,
            new SupportedGroupsExtension(Groups_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            new KeyShareExtension(KeyShares_5),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_0),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.28 (0x14134D4B0): Okhttp4Android11 (#27).</summary>
    public static ClientHelloSpec BuildOkhttp4Android11Spec() => BuildOkhttp4Android10Spec();

    /// <summary>Builder 5.29 (0x14134D4F0): Okhttp4Android12 (#28).</summary>
    public static ClientHelloSpec BuildOkhttp4Android12Spec() => BuildOkhttp4Android10Spec();

    /// <summary>Builder 5.30 (0x14134D530): Okhttp4Android13 (#29).</summary>
    public static ClientHelloSpec BuildOkhttp4Android13Spec() => BuildOkhttp4Android10Spec();

    /// <summary>Builder 5.31 (0x14134D570): Okhttp4Android9 (#30).</summary>
    public static ClientHelloSpec BuildOkhttp4Android9Spec() => new(
        CipherSuites: Ciphers_9,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg0,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_4),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.32 (0x14134DA50): Okhttp4Android8 (#31).</summary>
    public static ClientHelloSpec BuildOkhttp4Android8Spec() => new(
        CipherSuites: Ciphers_9,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg0,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_8),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_4),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.33 (0x14134DF30): Okhttp4Android7 (#32).</summary>
    public static ClientHelloSpec BuildOkhttp4Android7Spec() => new(
        CipherSuites: Ciphers_9,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedReneg0,
            SharedSni,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_9),
            new AlpnExtension(Alpn_0),
            new EcPointFormatsExtension(Bytes_0),
            new SupportedGroupsExtension(Groups_7),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.34 (0x14134E3E0): Chrome_152_PSK (#33).</summary>
    public static ClientHelloSpec BuildChrome_152_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSct,
            GreaseEchExtension.ChromePreset,
            new KeyShareExtension(KeyShares_3),
            new SignatureAlgorithmsExtension(SigAlgs_10),
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedEms,
            SharedSessionTicket,
            SharedSni,
            SharedReneg1,
            new PskKeyExchangeModesExtension(Bytes_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            TrustAnchorsExtension.Chrome152,
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.35 (0x14134EE20): Chrome_152 (#34).</summary>
    public static ClientHelloSpec BuildChrome_152Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new KeyShareExtension(KeyShares_3),
            SharedSni,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedReneg1,
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedSessionTicket,
            SharedStatusRequest,
            SharedEms,
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_10),
            SharedSct,
            new EcPointFormatsExtension(Bytes_0),
            GreaseEchExtension.ChromePreset,
            new AlpnExtension(Alpn_0),
            new PskKeyExchangeModesExtension(Bytes_1),
            TrustAnchorsExtension.Chrome152,
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.36 (0x14134F840): Chrome_150_PSK (#35).</summary>
    public static ClientHelloSpec BuildChrome_150_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSct,
            GreaseEchExtension.ChromePreset,
            new KeyShareExtension(KeyShares_3),
            new SignatureAlgorithmsExtension(SigAlgs_11),
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedEms,
            SharedSessionTicket,
            SharedSni,
            SharedReneg1,
            new PskKeyExchangeModesExtension(Bytes_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.37 (0x141350230): Chrome_150 (#36).</summary>
    public static ClientHelloSpec BuildChrome_150Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new KeyShareExtension(KeyShares_3),
            SharedSni,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedReneg1,
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedSessionTicket,
            SharedStatusRequest,
            SharedEms,
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_11),
            SharedSct,
            new EcPointFormatsExtension(Bytes_0),
            GreaseEchExtension.ChromePreset,
            new AlpnExtension(Alpn_0),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.38 (0x141350BE0): Chrome_146_PSK (#37).</summary>
    public static ClientHelloSpec BuildChrome_146_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSct,
            GreaseEchExtension.ChromePreset,
            new KeyShareExtension(KeyShares_3),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedEms,
            SharedSessionTicket,
            SharedSni,
            SharedReneg1,
            new PskKeyExchangeModesExtension(Bytes_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            TrustAnchorsExtension.Empty,
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.39 (0x141351650): Chrome_146 (#38).</summary>
    public static ClientHelloSpec BuildChrome_146Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new KeyShareExtension(KeyShares_3),
            SharedSni,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedReneg1,
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedSessionTicket,
            SharedStatusRequest,
            SharedEms,
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new EcPointFormatsExtension(Bytes_0),
            GreaseEchExtension.ChromePreset,
            new AlpnExtension(Alpn_0),
            new PskKeyExchangeModesExtension(Bytes_1),
            TrustAnchorsExtension.Empty,
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.40 (0x141352090): Chrome_144_PSK (#39).</summary>
    public static ClientHelloSpec BuildChrome_144_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSct,
            GreaseEchExtension.ChromePreset,
            new KeyShareExtension(KeyShares_3),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedEms,
            SharedSessionTicket,
            SharedSni,
            SharedReneg1,
            new PskKeyExchangeModesExtension(Bytes_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            new AlpnExtension(Alpn_0),
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.41 (0x141352A70): Chrome_144 (#40).</summary>
    public static ClientHelloSpec BuildChrome_144Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new KeyShareExtension(KeyShares_3),
            SharedSni,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedReneg1,
            new SupportedGroupsExtension(Groups_2),
            new CompressCertificateExtension(CertComp_1),
            SharedSessionTicket,
            SharedStatusRequest,
            SharedEms,
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new EcPointFormatsExtension(Bytes_0),
            GreaseEchExtension.ChromePreset,
            new AlpnExtension(Alpn_0),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.42 (0x141353410): Chrome_133_PSK (#41).</summary>
    public static ClientHelloSpec BuildChrome_133_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSct,
            SharedSni,
            GreaseEchExtension.ChromePreset,
            SharedReneg1,
            SharedEms,
            SharedStatusRequest,
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_4),
            new KeyShareExtension(KeyShares_3),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new SupportedGroupsExtension(Groups_2),
            new AlpnExtension(Alpn_5),
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new CompressCertificateExtension(CertComp_1),
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.43 (0x141353E20): Chrome_133 (#42).</summary>
    public static ClientHelloSpec BuildChrome_133Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_4),
            new KeyShareExtension(KeyShares_3),
            SharedSct,
            new EcPointFormatsExtension(Bytes_0),
            new SupportedVersionsExtension(Versions_1),
            SharedStatusRequest,
            new AlpnExtension(Alpn_5),
            SharedSni,
            GreaseEchExtension.ChromePreset,
            new CompressCertificateExtension(CertComp_1),
            new SupportedGroupsExtension(Groups_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedEms,
            SharedReneg1,
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.44 (0x1413547E0): Chrome_117 (#43).</summary>
    public static ClientHelloSpec BuildChrome_117Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedSni,
            new AlpnExtension(Alpn_0),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new SupportedVersionsExtension(Versions_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new SupportedGroupsExtension(Groups_1),
            SharedEms,
            SharedSessionTicket,
            new CompressCertificateExtension(CertComp_1),
            SharedSct,
            SharedStatusRequest,
            new KeyShareExtension(KeyShares_2),
            SharedReneg1,
            new EcPointFormatsExtension(Bytes_0),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.45 (0x141355120): Chrome_124 (#44).</summary>
    public static ClientHelloSpec BuildChrome_124Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new CompressCertificateExtension(CertComp_1),
            SharedSct,
            SharedEms,
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new AlpnExtension(Alpn_0),
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSni,
            SharedSessionTicket,
            new SupportedGroupsExtension(Groups_8),
            GreaseEchExtension.ChromePreset,
            SharedStatusRequest,
            SharedReneg1,
            new PskKeyExchangeModesExtension(Bytes_1),
            new KeyShareExtension(KeyShares_6),
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.46 (0x141355AC0): Chrome_120 (#45).</summary>
    public static ClientHelloSpec BuildChrome_120Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            SharedStatusRequest,
            SharedEms,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedReneg1,
            new AlpnExtension(Alpn_0),
            GreaseEchExtension.ChromePreset,
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new SupportedGroupsExtension(Groups_1),
            new EcPointFormatsExtension(Bytes_0),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new CompressCertificateExtension(CertComp_1),
            SharedGrease,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.47 (0x1412BD250): Chrome_112 (#46).</summary>
    public static ClientHelloSpec BuildChrome_112Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new PskKeyExchangeModesExtension(Bytes_1),
            new KeyShareExtension(KeyShares_2),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSni,
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            SharedEms,
            new AlpnExtension(Alpn_0),
            new SupportedGroupsExtension(Groups_1),
            SharedReneg1,
            new CompressCertificateExtension(CertComp_1),
            SharedSct,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.48 (0x1412C0DE0): Chrome_116_PSK (#47).</summary>
    public static ClientHelloSpec BuildChrome_116_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new PskKeyExchangeModesExtension(Bytes_1),
            new KeyShareExtension(KeyShares_2),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            new SupportedVersionsExtension(Versions_1),
            SharedSni,
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            SharedEms,
            new AlpnExtension(Alpn_0),
            new SupportedGroupsExtension(Groups_1),
            SharedReneg1,
            new CompressCertificateExtension(CertComp_1),
            SharedSct,
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedGrease,
            SharedBoringPadding,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.49 (0x1412C1770): Chrome_116_PSK_PQ (#48).</summary>
    public static ClientHelloSpec BuildChrome_116_PSK_PQSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_8),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new KeyShareExtension(KeyShares_6),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            SharedGrease,
            SharedBoringPadding,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.50 (0x1412BC910): Chrome_111 (#49).</summary>
    public static ClientHelloSpec BuildChrome_111Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            new CompressCertificateExtension(CertComp_1),
            new EcPointFormatsExtension(Bytes_0),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            SharedStatusRequest,
            new SupportedGroupsExtension(Groups_1),
            SharedSct,
            SharedEms,
            SharedSni,
            new PskKeyExchangeModesExtension(Bytes_1),
            new KeyShareExtension(KeyShares_2),
            new SupportedVersionsExtension(Versions_1),
            SharedSessionTicket,
            SharedReneg1,
            new AlpnExtension(Alpn_0),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.51 (0x1412BBFD0): Chrome_110 (#50).</summary>
    public static ClientHelloSpec BuildChrome_110Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedEms,
            new CompressCertificateExtension(CertComp_1),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            SharedSni,
            new AlpnExtension(Alpn_0),
            SharedSessionTicket,
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            SharedReneg1,
            new SupportedVersionsExtension(Versions_1),
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedGroupsExtension(Groups_1),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.52 (0x1412BB630): Chrome_109 (#51), Chrome_108 (#52), Chrome_107 (#53), Chrome_106 (#54), Chrome_105 (#55), Chrome_104 (#56), Chrome_103 (#57).</summary>
    public static ClientHelloSpec BuildChrome103To109Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: true,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.53 (0x1412C0540): Safari_15_6_1 (#58), Safari_16_0 (#59).</summary>
    public static ClientHelloSpec BuildSafari15_6_1To16_0Spec() => new(
        CipherSuites: Ciphers_10,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_2),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.54 (0x1412BFC80): Safari_Ipad_15_6 (#60), Safari_IOS_16_0 (#65), Safari_IOS_15_5 (#66), Safari_IOS_15_6 (#67).</summary>
    public static ClientHelloSpec BuildSafariMobile15_5To16_0Spec() => new(
        CipherSuites: Ciphers_10,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_2),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.55 (0x141356400): Safari_IOS_17_0 (#61).</summary>
    public static ClientHelloSpec BuildSafari_IOS_17_0Spec() => new(
        CipherSuites: Ciphers_10,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_2),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.56 (0x141356C90): Safari_IOS_26_0 (#62).</summary>
    public static ClientHelloSpec BuildSafari_IOS_26_0Spec() => new(
        CipherSuites: Ciphers_11,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_9),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_12),
            SharedSct,
            new KeyShareExtension(KeyShares_3),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.57 (0x141357520): Safari_IOS_18_5 (#63).</summary>
    public static ClientHelloSpec BuildSafari_IOS_18_5Spec() => new(
        CipherSuites: Ciphers_10,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_12),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_2),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.58 (0x141357DB0): Safari_IOS_18_0 (#64).</summary>
    public static ClientHelloSpec BuildSafari_IOS_18_0Spec() => new(
        CipherSuites: Ciphers_10,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_6),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_2),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.59 (0x141358640): Firefox_117 (#68).</summary>
    public static ClientHelloSpec BuildFirefox_117Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.60 (0x1412BEBE0): Firefox_110 (#69).</summary>
    public static ClientHelloSpec BuildFirefox_110Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new RecordSizeLimitExtension(16385),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.61 (0x1412BE3C0): Firefox_108 (#70), Firefox_106 (#71).</summary>
    public static ClientHelloSpec BuildFirefox106To108Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.62 (0x1412BDB90): Firefox_105 (#72), Firefox_104 (#73), Firefox_102 (#74).</summary>
    public static ClientHelloSpec BuildFirefox102To105Spec() => new(
        CipherSuites: Ciphers_1,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_3),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new DelegatedCredentialsExtension(SigAlgs_0),
            new KeyShareExtension(KeyShares_4),
            new SupportedVersionsExtension(Versions_0),
            new SignatureAlgorithmsExtension(SigAlgs_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            new RecordSizeLimitExtension(16385),
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.63 (0x1412BF320): Opera_90 (#75), Opera_91 (#76), Opera_89 (#77).</summary>
    public static ClientHelloSpec BuildOpera89To91Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_1),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettings, Alpn_1),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    /// <summary>Builder 5.64 (0x141358E50): Brave_146 (#78).</summary>
    public static ClientHelloSpec BuildBrave_146Spec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSessionTicket,
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedReneg1,
            new AlpnExtension(Alpn_0),
            new SupportedGroupsExtension(Groups_2),
            SharedEms,
            GreaseEchExtension.ChromePreset,
            SharedSni,
            new KeyShareExtension(KeyShares_3),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedSct,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            SharedGrease,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.65 (0x1413597F0): Brave_146_PSK (#79).</summary>
    public static ClientHelloSpec BuildBrave_146_PSKSpec() => new(
        CipherSuites: Ciphers_2,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSessionTicket,
            new SupportedVersionsExtension(Versions_1),
            new PskKeyExchangeModesExtension(Bytes_1),
            SharedReneg1,
            new AlpnExtension(Alpn_0),
            new SupportedGroupsExtension(Groups_2),
            SharedEms,
            GreaseEchExtension.ChromePreset,
            SharedSni,
            new KeyShareExtension(KeyShares_3),
            new CompressCertificateExtension(CertComp_1),
            new ApplicationSettingsExtension(TlsExtensionType.ApplicationSettingsNew, Alpn_1),
            SharedSct,
            new SignatureAlgorithmsExtension(SigAlgs_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedStatusRequest,
            SharedGrease,
            SharedPreSharedKey,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.66 (0x14135A1D0): Chrome_IOS_26_1 (#80).</summary>
    public static ClientHelloSpec BuildChrome_IOS_26_1Spec() => new(
        CipherSuites: Ciphers_11,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_9),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_12),
            SharedSct,
            new KeyShareExtension(KeyShares_3),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.67 (0x14135AA60): MMSIos2 (#81).</summary>
    public static ClientHelloSpec BuildMMSIos2Spec() => new(
        CipherSuites: Ciphers_12,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_4),
            new EcPointFormatsExtension(Bytes_0),
            SharedSessionTicket,
            new SignatureAlgorithmsExtension(SigAlgs_5),
            new KeyShareExtension(KeyShares_5),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_0),
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: false);

    /// <summary>Builder 5.68 (0x14135AFD0): MMSIos3 (#82).</summary>
    public static ClientHelloSpec BuildMMSIos3Spec() => new(
        CipherSuites: Ciphers_4,
        Extensions: Array.AsReadOnly(new TlsExtensionSpec[]
        {
            SharedGrease,
            SharedSni,
            SharedEms,
            SharedReneg1,
            new SupportedGroupsExtension(Groups_5),
            new EcPointFormatsExtension(Bytes_0),
            new AlpnExtension(Alpn_0),
            SharedStatusRequest,
            new SignatureAlgorithmsExtension(SigAlgs_13),
            SharedSct,
            new KeyShareExtension(KeyShares_2),
            new PskKeyExchangeModesExtension(Bytes_1),
            new SupportedVersionsExtension(Versions_1),
            new CompressCertificateExtension(CertComp_2),
            SharedGrease,
            SharedBoringPadding,
        }),
        ShuffleExtensions: false,
        BoringPaddingStyle: true);

    // ---- All 82 ClientProfile slots (0..81) ----
    public static ClientProfile Firefox_148 { get; } = new(
        Name: "Firefox_148",
        SlotIndex: 0,
        CreateClientHelloSpec: BuildFirefox_148Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, new Http2HeaderPriority(0u, false, 41), null),
        Http3Settings: ChromeQuicSpecs.CreateFirefoxHttp3Settings(),
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_147 { get; } = new(
        Name: "Firefox_147",
        SlotIndex: 1,
        CreateClientHelloSpec: BuildFirefox_147Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, new Http2HeaderPriority(0u, false, 41), null),
        Http3Settings: ChromeQuicSpecs.CreateFirefoxHttp3Settings(),
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_147_PSK { get; } = new(
        Name: "Firefox_147_PSK",
        SlotIndex: 2,
        CreateClientHelloSpec: BuildFirefox_147_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, new Http2HeaderPriority(0u, false, 41), null),
        Http3Settings: ChromeQuicSpecs.CreateFirefoxHttp3Settings(),
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_146_PSK { get; } = new(
        Name: "Firefox_146_PSK",
        SlotIndex: 3,
        CreateClientHelloSpec: BuildFirefox_146_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, new Http2HeaderPriority(0u, false, 41), null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_135 { get; } = new(
        Name: "Firefox_135",
        SlotIndex: 4,
        CreateClientHelloSpec: BuildFirefox_135Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_133 { get; } = new(
        Name: "Firefox_133",
        SlotIndex: 5,
        CreateClientHelloSpec: BuildFirefox_133Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_0, 12517377u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Chrome_130_PSK { get; } = new(
        Name: "Chrome_130_PSK",
        SlotIndex: 6,
        CreateClientHelloSpec: BuildChrome_130_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_131_PSK { get; } = new(
        Name: "Chrome_131_PSK",
        SlotIndex: 7,
        CreateClientHelloSpec: BuildChrome_131_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_131 { get; } = new(
        Name: "Chrome_131",
        SlotIndex: 8,
        CreateClientHelloSpec: BuildChrome_131Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Firefox_132 { get; } = new(
        Name: "Firefox_132",
        SlotIndex: 9,
        CreateClientHelloSpec: BuildFirefox_132Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_2, 12517377u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_123 { get; } = new(
        Name: "Firefox_123",
        SlotIndex: 10,
        CreateClientHelloSpec: BuildFirefox_123Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_120 { get; } = new(
        Name: "Firefox_120",
        SlotIndex: 11,
        CreateClientHelloSpec: BuildFirefox_120Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile ZalandoAndroidMobile { get; } = new(
        Name: "ZalandoAndroidMobile",
        SlotIndex: 12,
        CreateClientHelloSpec: BuildZalandoAndroidMobileSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_4, 15663105u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile ZalandoIosMobile { get; } = new(
        Name: "ZalandoIosMobile",
        SlotIndex: 13,
        CreateClientHelloSpec: BuildZalandoIosMobileSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_5, 15663105u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile NikeIosMobile { get; } = new(
        Name: "NikeIosMobile",
        SlotIndex: 14,
        CreateClientHelloSpec: BuildNikeIosMobileSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_5, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile NikeAndroidMobile { get; } = new(
        Name: "NikeAndroidMobile",
        SlotIndex: 15,
        CreateClientHelloSpec: BuildNikeAndroidMobileSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_4, 15663105u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile CloudflareCustom { get; } = new(
        Name: "CloudflareCustom",
        SlotIndex: 16,
        CreateClientHelloSpec: BuildCloudflareCustomSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_4, 15663105u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MMSIos { get; } = new(
        Name: "MMSIos",
        SlotIndex: 17,
        CreateClientHelloSpec: BuildMMSIosSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_6, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MeshIos { get; } = new(
        Name: "MeshIos",
        SlotIndex: 18,
        CreateClientHelloSpec: BuildMeshIosSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_6, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MeshAndroid { get; } = new(
        Name: "MeshAndroid",
        SlotIndex: 19,
        CreateClientHelloSpec: BuildMeshAndroidSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MeshIos2 { get; } = new(
        Name: "MeshIos2",
        SlotIndex: 20,
        CreateClientHelloSpec: BuildMeshIos2Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_8, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MeshAndroid2 { get; } = new(
        Name: "MeshAndroid2",
        SlotIndex: 21,
        CreateClientHelloSpec: BuildMeshAndroid2Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile ConfirmedIos { get; } = new(
        Name: "ConfirmedIos",
        SlotIndex: 22,
        CreateClientHelloSpec: BuildConfirmedIosSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_6, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile ConfirmedAndroid { get; } = new(
        Name: "ConfirmedAndroid",
        SlotIndex: 23,
        CreateClientHelloSpec: BuildConfirmedAndroidSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile ConfirmedAndroid2 { get; } = new(
        Name: "ConfirmedAndroid2",
        SlotIndex: 24,
        CreateClientHelloSpec: BuildConfirmedAndroid2Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android10 { get; } = new(
        Name: "Okhttp4Android10",
        SlotIndex: 25,
        CreateClientHelloSpec: BuildOkhttp4Android10Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android11 { get; } = new(
        Name: "Okhttp4Android11",
        SlotIndex: 26,
        CreateClientHelloSpec: BuildOkhttp4Android11Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android12 { get; } = new(
        Name: "Okhttp4Android12",
        SlotIndex: 27,
        CreateClientHelloSpec: BuildOkhttp4Android12Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android13 { get; } = new(
        Name: "Okhttp4Android13",
        SlotIndex: 28,
        CreateClientHelloSpec: BuildOkhttp4Android13Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android9 { get; } = new(
        Name: "Okhttp4Android9",
        SlotIndex: 29,
        CreateClientHelloSpec: BuildOkhttp4Android9Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android8 { get; } = new(
        Name: "Okhttp4Android8",
        SlotIndex: 30,
        CreateClientHelloSpec: BuildOkhttp4Android8Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Okhttp4Android7 { get; } = new(
        Name: "Okhttp4Android7",
        SlotIndex: 31,
        CreateClientHelloSpec: BuildOkhttp4Android7Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_9, 16711681u, Pseudo_0, Http2HeaderPriority.Suppressed, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Chrome_152_PSK { get; } = new(
        Name: "Chrome_152_PSK",
        SlotIndex: 32,
        CreateClientHelloSpec: BuildChrome_152_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_152 { get; } = new(
        Name: "Chrome_152",
        SlotIndex: 33,
        CreateClientHelloSpec: BuildChrome_152Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_150_PSK { get; } = new(
        Name: "Chrome_150_PSK",
        SlotIndex: 34,
        CreateClientHelloSpec: BuildChrome_150_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_150 { get; } = new(
        Name: "Chrome_150",
        SlotIndex: 35,
        CreateClientHelloSpec: BuildChrome_150Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_146_PSK { get; } = new(
        Name: "Chrome_146_PSK",
        SlotIndex: 36,
        CreateClientHelloSpec: BuildChrome_146_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_146 { get; } = new(
        Name: "Chrome_146",
        SlotIndex: 37,
        CreateClientHelloSpec: BuildChrome_146Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_144_PSK { get; } = new(
        Name: "Chrome_144_PSK",
        SlotIndex: 38,
        CreateClientHelloSpec: BuildChrome_144_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_144 { get; } = new(
        Name: "Chrome_144",
        SlotIndex: 39,
        CreateClientHelloSpec: BuildChrome_144Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: ChromeQuicSpecs.CreateChromeHttp3Settings(),
        QuicSpec: ChromeQuicSpecs.DefaultTransportSpec,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_133_PSK { get; } = new(
        Name: "Chrome_133_PSK",
        SlotIndex: 40,
        CreateClientHelloSpec: BuildChrome_133_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_133 { get; } = new(
        Name: "Chrome_133",
        SlotIndex: 41,
        CreateClientHelloSpec: BuildChrome_133Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_117 { get; } = new(
        Name: "Chrome_117",
        SlotIndex: 42,
        CreateClientHelloSpec: BuildChrome_117Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_124 { get; } = new(
        Name: "Chrome_124",
        SlotIndex: 43,
        CreateClientHelloSpec: BuildChrome_124Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_120 { get; } = new(
        Name: "Chrome_120",
        SlotIndex: 44,
        CreateClientHelloSpec: BuildChrome_120Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_112 { get; } = new(
        Name: "Chrome_112",
        SlotIndex: 45,
        CreateClientHelloSpec: BuildChrome_112Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_116_PSK { get; } = new(
        Name: "Chrome_116_PSK",
        SlotIndex: 46,
        CreateClientHelloSpec: BuildChrome_116_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_116_PSK_PQ { get; } = new(
        Name: "Chrome_116_PSK_PQ",
        SlotIndex: 47,
        CreateClientHelloSpec: BuildChrome_116_PSK_PQSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_111 { get; } = new(
        Name: "Chrome_111",
        SlotIndex: 48,
        CreateClientHelloSpec: BuildChrome_111Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_110 { get; } = new(
        Name: "Chrome_110",
        SlotIndex: 49,
        CreateClientHelloSpec: BuildChrome_110Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_109 { get; } = new(
        Name: "Chrome_109",
        SlotIndex: 50,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_108 { get; } = new(
        Name: "Chrome_108",
        SlotIndex: 51,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_107 { get; } = new(
        Name: "Chrome_107",
        SlotIndex: 52,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_106 { get; } = new(
        Name: "Chrome_106",
        SlotIndex: 53,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_10, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_105 { get; } = new(
        Name: "Chrome_105",
        SlotIndex: 54,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_104 { get; } = new(
        Name: "Chrome_104",
        SlotIndex: 55,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Chrome_103 { get; } = new(
        Name: "Chrome_103",
        SlotIndex: 56,
        CreateClientHelloSpec: BuildChrome103To109Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: true,
        DisableHttp2: false);

    public static ClientProfile Safari_15_6_1 { get; } = new(
        Name: "Safari_15_6_1",
        SlotIndex: 57,
        CreateClientHelloSpec: BuildSafari15_6_1To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_11, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_16_0 { get; } = new(
        Name: "Safari_16_0",
        SlotIndex: 58,
        CreateClientHelloSpec: BuildSafari15_6_1To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_11, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_Ipad_15_6 { get; } = new(
        Name: "Safari_Ipad_15_6",
        SlotIndex: 59,
        CreateClientHelloSpec: BuildSafariMobile15_5To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_12, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_17_0 { get; } = new(
        Name: "Safari_IOS_17_0",
        SlotIndex: 60,
        CreateClientHelloSpec: BuildSafari_IOS_17_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_13, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_26_0 { get; } = new(
        Name: "Safari_IOS_26_0",
        SlotIndex: 61,
        CreateClientHelloSpec: BuildSafari_IOS_26_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_14, 10420225u, Pseudo_3, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_18_5 { get; } = new(
        Name: "Safari_IOS_18_5",
        SlotIndex: 62,
        CreateClientHelloSpec: BuildSafari_IOS_18_5Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_14, 10420225u, Pseudo_3, new Http2HeaderPriority(0u, false, 255), null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_18_0 { get; } = new(
        Name: "Safari_IOS_18_0",
        SlotIndex: 63,
        CreateClientHelloSpec: BuildSafari_IOS_18_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_15, 10420225u, Pseudo_3, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_16_0 { get; } = new(
        Name: "Safari_IOS_16_0",
        SlotIndex: 64,
        CreateClientHelloSpec: BuildSafariMobile15_5To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_12, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_15_5 { get; } = new(
        Name: "Safari_IOS_15_5",
        SlotIndex: 65,
        CreateClientHelloSpec: BuildSafariMobile15_5To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_12, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Safari_IOS_15_6 { get; } = new(
        Name: "Safari_IOS_15_6",
        SlotIndex: 66,
        CreateClientHelloSpec: BuildSafariMobile15_5To16_0Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_12, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_117 { get; } = new(
        Name: "Firefox_117",
        SlotIndex: 67,
        CreateClientHelloSpec: BuildFirefox_117Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_110 { get; } = new(
        Name: "Firefox_110",
        SlotIndex: 68,
        CreateClientHelloSpec: BuildFirefox_110Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_108 { get; } = new(
        Name: "Firefox_108",
        SlotIndex: 69,
        CreateClientHelloSpec: BuildFirefox106To108Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_106 { get; } = new(
        Name: "Firefox_106",
        SlotIndex: 70,
        CreateClientHelloSpec: BuildFirefox106To108Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_105 { get; } = new(
        Name: "Firefox_105",
        SlotIndex: 71,
        CreateClientHelloSpec: BuildFirefox102To105Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_104 { get; } = new(
        Name: "Firefox_104",
        SlotIndex: 72,
        CreateClientHelloSpec: BuildFirefox102To105Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Firefox_102 { get; } = new(
        Name: "Firefox_102",
        SlotIndex: 73,
        CreateClientHelloSpec: BuildFirefox102To105Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_3, 12517377u, Pseudo_0, new Http2HeaderPriority(13u, false, 41), PriorityFrames_0),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Opera_90 { get; } = new(
        Name: "Opera_90",
        SlotIndex: 74,
        CreateClientHelloSpec: BuildOpera89To91Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Opera_91 { get; } = new(
        Name: "Opera_91",
        SlotIndex: 75,
        CreateClientHelloSpec: BuildOpera89To91Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Opera_89 { get; } = new(
        Name: "Opera_89",
        SlotIndex: 76,
        CreateClientHelloSpec: BuildOpera89To91Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_7, 15663105u, Pseudo_1, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Brave_146 { get; } = new(
        Name: "Brave_146",
        SlotIndex: 77,
        CreateClientHelloSpec: BuildBrave_146Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, new Http2HeaderPriority(0u, true, 255), null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Brave_146_PSK { get; } = new(
        Name: "Brave_146_PSK",
        SlotIndex: 78,
        CreateClientHelloSpec: BuildBrave_146_PSKSpec,
        Http2Settings: new Http2SettingsSpec(H2Settings_1, 15663105u, Pseudo_1, new Http2HeaderPriority(0u, true, 255), null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile Chrome_IOS_26_1 { get; } = new(
        Name: "Chrome_IOS_26_1",
        SlotIndex: 79,
        CreateClientHelloSpec: BuildChrome_IOS_26_1Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_16, 10485760u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: true);

    public static ClientProfile MMSIos2 { get; } = new(
        Name: "MMSIos2",
        SlotIndex: 80,
        CreateClientHelloSpec: BuildMMSIos2Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_6, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

    public static ClientProfile MMSIos3 { get; } = new(
        Name: "MMSIos3",
        SlotIndex: 81,
        CreateClientHelloSpec: BuildMMSIos3Spec,
        Http2Settings: new Http2SettingsSpec(H2Settings_6, 15663105u, Pseudo_2, null, null),
        Http3Settings: null,
        QuicSpec: null,
        ShuffleExtensions: false,
        DisableHttp2: false);

}
