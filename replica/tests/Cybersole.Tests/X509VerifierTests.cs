using System.Net;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using Cybersole.Http.X509;
using Xunit;

namespace Cybersole.Tests;

public sealed class X509VerifierTests
{
    private static readonly DateTimeOffset BaseNow = new(2026, 6, 15, 12, 0, 0, TimeSpan.Zero);

    [Fact]
    public void EmbeddedRootStoreParsesAll121CertificatesAndVerifiesRealSignatures()
    {
        var db = RootCertificateDatabase.Default;
        Assert.Equal(121, db.Count);

        foreach (var cert in db.Certificates)
        {
            Assert.True(cert.IsCa, $"Expected embedded root '{cert.SubjectText}' to have CA=true.");
            Assert.False(cert.SubjectRaw.IsEmpty);
            Assert.Equal(32, cert.SpkiSha256.Length);
            Assert.StartsWith("pin-sha256=", cert.PinSha256, StringComparison.Ordinal);
            Assert.Empty(cert.UnhandledCriticalExtensions);
            Assert.True(cert.IsSelfSigned, $"Expected embedded root '{cert.SubjectText}' to be self-issued.");
            Assert.True(db.Contains(cert));
        }

        Assert.Contains("COMODO ECC Certification Authority", db.Certificates[0].SubjectText, StringComparison.Ordinal);
        Assert.Contains("Telia RSA TLS Root CA v3", db.Certificates[120].SubjectText, StringComparison.Ordinal);

        // Verify self-signatures across all real-world algorithm/curve families present in RootCertificates.bin
        var representativeIndices = new[] { 0, 1, 8, 28, 38, 45, 116, 120 };
        foreach (var idx in representativeIndices)
        {
            var root = db.Certificates[idx];
            Assert.True(root.VerifySignature(root), $"Self-signature failed for embedded root[{idx}] '{root.SubjectText}'.");
        }
    }

    [Fact]
    public void Asn1ReaderRejectsIndefiniteLengthNonMinimalLengthAndTrailingGarbage()
    {
        // Indefinite length SEQUENCE: 30 80 05 00 00 00
        Assert.Throws<FormatException>(() => Asn1Reader.ReadSingle(new byte[] { 0x30, 0x80, 0x05, 0x00, 0x00, 0x00 }));

        // Non-minimal long-form length (< 128 encoded as 0x81 0x01)
        Assert.Throws<FormatException>(() => Asn1Reader.ReadSingle(new byte[] { 0x04, 0x81, 0x01, 0x41 }));

        // Non-minimal long-form length with leading 0x00 octet (0x82 0x00 0x01)
        Assert.Throws<FormatException>(() => Asn1Reader.ReadSingle(new byte[] { 0x04, 0x82, 0x00, 0x01, 0x41 }));

        // Trailing bytes after root TLV
        Assert.Throws<FormatException>(() => Asn1Reader.ReadSingle(new byte[] { 0x05, 0x00, 0xFF }));

        // Trailing garbage inside container cursor
        var seqNode = Asn1Reader.ReadSingle(new byte[] { 0x30, 0x04, 0x05, 0x00, 0x05, 0x00 });
        var cursor = new Asn1Cursor(seqNode.Content);
        _ = cursor.ReadUniversal(Asn1Tag.TagNull, false);
        Assert.Throws<FormatException>(() => cursor.ExpectEnd());

        // UTCTime RFC 5280 rule: < 50 => 20xx, >= 50 => 19xx
        var utc2049 = Asn1Reader.ReadSingle(BuildPrimitiveTlv(0x17, Encoding.ASCII.GetBytes("491231235959Z")));
        Assert.Equal(new DateTimeOffset(2049, 12, 31, 23, 59, 59, TimeSpan.Zero), Asn1Reader.ParseTime(utc2049));

        var utc1950 = Asn1Reader.ReadSingle(BuildPrimitiveTlv(0x17, Encoding.ASCII.GetBytes("500101000000Z")));
        Assert.Equal(new DateTimeOffset(1950, 1, 1, 0, 0, 0, TimeSpan.Zero), Asn1Reader.ParseTime(utc1950));

        var gen2046 = Asn1Reader.ReadSingle(BuildPrimitiveTlv(0x18, Encoding.ASCII.GetBytes("20461006083956Z")));
        Assert.Equal(new DateTimeOffset(2046, 10, 6, 8, 39, 56, TimeSpan.Zero), Asn1Reader.ParseTime(gen2046));
    }

    [Fact]
    public void ValidRsaPkcs1RsaPssAndEcdsaP256ThreeTierChainsPassVerification()
    {
        // RSA PKCS#1 v1.5 chain
        using (var rootKey = RSA.Create(2048))
        using (var midKey = RSA.Create(2048))
        using (var leafKey = RSA.Create(2048))
        {
            using var rootCert = CreateCa("CN=RSA Test Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            using var midCert = CreateCa("CN=RSA Test Mid", midKey, rootCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            using var leafCert = CreateLeaf("CN=shop.example.com", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "shop.example.com" });

            var db = CreateCustomDb(rootCert);
            var verified = CertificateVerifier.VerifyChain(
                new[] { leafCert.RawData, midCert.RawData },
                "shop.example.com",
                CustomOptions(db));

            Assert.Equal(3, verified.Count);
            Assert.Equal("CN=shop.example.com", verified[0].SubjectText);
            Assert.Equal("CN=RSA Test Mid", verified[1].SubjectText);
            Assert.Equal("CN=RSA Test Root", verified[2].SubjectText);
        }

        // RSA-PSS chain
        using (var rootKey = RSA.Create(2048))
        using (var midKey = RSA.Create(2048))
        using (var leafKey = RSA.Create(2048))
        {
            using var rootCert = CreateCa("CN=PSS Test Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
            using var midCert = CreateCa("CN=PSS Test Mid", midKey, rootCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
            using var leafCert = CreateLeaf("CN=pss.example.com", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pss, dnsNames: new[] { "pss.example.com" });

            var db = CreateCustomDb(rootCert);
            var verified = CertificateVerifier.VerifyChain(
                new[] { leafCert.RawData, midCert.RawData },
                "pss.example.com",
                CustomOptions(db));

            Assert.Equal(3, verified.Count);
        }

        // ECDSA P-256 chain
        using (var rootKey = ECDsa.Create(ECCurve.NamedCurves.nistP256))
        using (var midKey = ECDsa.Create(ECCurve.NamedCurves.nistP256))
        using (var leafKey = ECDsa.Create(ECCurve.NamedCurves.nistP256))
        {
            using var rootCert = CreateEcCa("CN=EC Test Root", rootKey, null);
            using var midCert = CreateEcCa("CN=EC Test Mid", midKey, rootCert);
            using var leafCert = CreateEcLeaf("CN=ec.example.com", leafKey, midCert, dnsNames: new[] { "ec.example.com" });

            var db = CreateCustomDb(rootCert);
            var verified = CertificateVerifier.VerifyChain(
                new[] { leafCert.RawData, midCert.RawData },
                "ec.example.com",
                CustomOptions(db));

            Assert.Equal(3, verified.Count);
        }
    }

    [Fact]
    public void ExpiredLeafExpiredIntermediateAndNotYetValidLeafAreRejected()
    {
        using var rootKey = RSA.Create(2048);
        using var midKey = RSA.Create(2048);
        using var expiredMidKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);

        using var rootCert = CreateCa("CN=Expiry Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var midCert = CreateCa("CN=Expiry Valid Mid", midKey, rootCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var expiredMidCert = CreateCa(
            "CN=Expiry Old Mid",
            expiredMidKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            notBefore: BaseNow.AddDays(-30),
            notAfter: BaseNow.AddDays(-1));

        using var expiredLeaf = CreateLeaf(
            "CN=expired.example.com",
            leafKey,
            midCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "expired.example.com" },
            notBefore: BaseNow.AddDays(-10),
            notAfter: BaseNow.AddHours(-1));

        using var futureLeaf = CreateLeaf(
            "CN=future.example.com",
            leafKey,
            midCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "future.example.com" },
            notBefore: BaseNow.AddHours(1),
            notAfter: BaseNow.AddDays(10));

        using var leafUnderExpiredMid = CreateLeafWithRsaSigner(
            "CN=midexp.example.com",
            leafKey,
            expiredMidCert.SubjectName,
            expiredMidKey,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "midexp.example.com" },
            notBefore: BaseNow.AddDays(-5),
            notAfter: BaseNow.AddDays(5));

        var db = CreateCustomDb(rootCert);

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { expiredLeaf.RawData, midCert.RawData }, "expired.example.com", CustomOptions(db)));

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { futureLeaf.RawData, midCert.RawData }, "future.example.com", CustomOptions(db)));

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { leafUnderExpiredMid.RawData, expiredMidCert.RawData }, "midexp.example.com", CustomOptions(db)));
    }

    [Fact]
    public void UntrustedSelfSignedLeafRejectedUnlessInCustomRootsOrInsecureSkipVerify()
    {
        using var leafKey = RSA.Create(2048);
        var req = new CertificateRequest("CN=self.example.com", leafKey, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new("1.3.6.1.5.5.7.3.1") }, false));
        var san = new SubjectAlternativeNameBuilder();
        san.AddDnsName("self.example.com");
        req.CertificateExtensions.Add(san.Build());
        using var selfSigned = req.CreateSelfSigned(BaseNow.AddDays(-1), BaseNow.AddDays(10));

        // Fails against embedded default roots
        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { selfSigned.RawData }, "self.example.com", new CertificateVerifyOptions { VerificationTime = BaseNow }));

        // Passes when added as custom root
        var customDb = CreateCustomDb(selfSigned);
        var trusted = CertificateVerifier.VerifyChain(new[] { selfSigned.RawData }, "self.example.com", CustomOptions(customDb));
        Assert.Single(trusted);

        // Passes when InsecureSkipVerify = true
        var skipped = CertificateVerifier.VerifyChain(
            new[] { selfSigned.RawData },
            "wrong-host.example.com",
            new CertificateVerifyOptions { InsecureSkipVerify = true });
        Assert.Single(skipped);
        Assert.Equal("CN=self.example.com", skipped[0].SubjectText);
    }

    [Fact]
    public void BasicConstraintsNonCaKeyCertSignAndPathLenConstraintAreEnforced()
    {
        using var rootKey = RSA.Create(2048);
        using var nonCaKey = RSA.Create(2048);
        using var noKeyCertSignKey = RSA.Create(2048);
        using var mid0Key = RSA.Create(2048);
        using var mid1Key = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);

        using var rootNoPathLimit = CreateCa("CN=Root Unlimited", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var rootPathLen0 = CreateCa("CN=Root PathLen0", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, pathLen: 0);
        using var rootPathLen1 = CreateCa("CN=Root PathLen1", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, pathLen: 1);

        // Intermediate with BasicConstraints CA=false
        using var nonCaMid = CreateNonCaIntermediate("CN=Not A CA", nonCaKey, rootNoPathLimit);
        using var leafUnderNonCa = CreateLeafWithRsaSigner("CN=badca.example.com", leafKey, nonCaMid.SubjectName, nonCaKey, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "badca.example.com" }, notBefore: BaseNow.AddDays(-1), notAfter: BaseNow.AddDays(30));

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { leafUnderNonCa.RawData, nonCaMid.RawData }, "badca.example.com", CustomOptions(CreateCustomDb(rootNoPathLimit))));

        // Intermediate CA=true but KeyUsage lacks KeyCertSign
        using var midNoCertSign = CreateCa("CN=Mid No KeyCertSign", noKeyCertSignKey, rootNoPathLimit, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1,
            keyUsageFlags: X509KeyUsageFlags.DigitalSignature);
        using var leafUnderNoSign = CreateLeafWithRsaSigner("CN=nosign.example.com", leafKey, midNoCertSign.SubjectName, noKeyCertSignKey, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "nosign.example.com" }, notBefore: BaseNow.AddDays(-1), notAfter: BaseNow.AddDays(30));

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { leafUnderNoSign.RawData, midNoCertSign.RawData }, "nosign.example.com", CustomOptions(CreateCustomDb(rootNoPathLimit))));

        // PathLenConstraint = 0 allows leaf signed by root directly, rejects leaf -> mid -> root
        using var midUnderLen0 = CreateCa("CN=Mid Under Len0", mid0Key, rootPathLen0, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var leafUnderLen0 = CreateLeaf("CN=len0.example.com", leafKey, midUnderLen0, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "len0.example.com" });

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { leafUnderLen0.RawData, midUnderLen0.RawData }, "len0.example.com", CustomOptions(CreateCustomDb(rootPathLen0))));

        // PathLenConstraint = 1 allows leaf -> mid -> root (1 intermediate)
        using var midUnderLen1 = CreateCa("CN=Mid Under Len1", mid1Key, rootPathLen1, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var leafUnderLen1 = CreateLeaf("CN=len1.example.com", leafKey, midUnderLen1, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "len1.example.com" });

        var okChain = CertificateVerifier.VerifyChain(new[] { leafUnderLen1.RawData, midUnderLen1.RawData }, "len1.example.com", CustomOptions(CreateCustomDb(rootPathLen1)));
        Assert.Equal(3, okChain.Count);
    }

    [Fact]
    public void Rfc6125HostnameIpWildcardAndCnFallbackRules()
    {
        using var rootKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);
        using var rootCert = CreateCa("CN=Host Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var opts = CustomOptions(CreateCustomDb(rootCert));

        // Wildcard + exact + IPv4 + IPv6 SAN leaf (CN deliberately does not match SANs, verifying SAN suppresses CN)
        using var sanLeaf = CreateLeaf(
            "CN=cn-ignored.invalid",
            leafKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "*.example.com", "exact.other.test" },
            ipAddresses: new[] { IPAddress.Parse("192.0.2.10"), IPAddress.Parse("2001:db8::1") });

        Assert.Equal(2, CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "api.example.com", opts).Count);
        Assert.Equal(2, CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "EXACT.OTHER.TEST", opts).Count);
        Assert.Equal(2, CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "192.0.2.10", opts).Count);
        Assert.Equal(2, CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "2001:db8:0:0::1", opts).Count);

        // Multi-label mismatch, apex mismatch, wrong IP, and suppressed CN fallback
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "a.b.example.com", opts));
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "example.com", opts));
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "192.0.2.11", opts));
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { sanLeaf.RawData }, "cn-ignored.invalid", opts));

        // Zero SAN entries -> falls back to CN
        using var cnOnlyLeaf = CreateLeaf(
            "CN=legacy.example.com",
            leafKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: null,
            ipAddresses: null);

        Assert.Equal(2, CertificateVerifier.VerifyChain(new[] { cnOnlyLeaf.RawData }, "legacy.example.com", opts).Count);
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { cnOnlyLeaf.RawData }, "other.example.com", opts));
    }

    [Fact]
    public void NameConstraintsEnforcesPermittedAndExcludedDnsAndIpCidrs()
    {
        using var rootKey = RSA.Create(2048);
        using var midKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);

        using var rootCert = CreateCa("CN=NC Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);

        var ncExt = BuildNameConstraintsExtension(
            permittedDns: new[] { ".corp.example" },
            excludedDns: new[] { "bad.corp.example" },
            permittedIps: new[]
            {
                (IPAddress.Parse("10.0.0.0"), IPAddress.Parse("255.0.0.0")),
                (IPAddress.Parse("2001:db8::"), IPAddress.Parse("ffff:ffff::")),
            },
            excludedIps: new[]
            {
                (IPAddress.Parse("10.1.0.0"), IPAddress.Parse("255.255.0.0")),
            });

        using var midCert = CreateCa(
            "CN=NC Mid",
            midKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            extraExtensions: new[] { ncExt });

        var opts = CustomOptions(CreateCustomDb(rootCert));

        using var validLeaf = CreateLeaf(
            "CN=api.corp.example",
            leafKey,
            midCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "api.corp.example" },
            ipAddresses: new[] { IPAddress.Parse("10.2.3.4"), IPAddress.Parse("2001:db8::5") });

        Assert.Equal(3, CertificateVerifier.VerifyChain(new[] { validLeaf.RawData, midCert.RawData }, "api.corp.example", opts).Count);
        Assert.Equal(3, CertificateVerifier.VerifyChain(new[] { validLeaf.RawData, midCert.RawData }, "10.2.3.4", opts).Count);
        Assert.Equal(3, CertificateVerifier.VerifyChain(new[] { validLeaf.RawData, midCert.RawData }, "2001:db8::5", opts).Count);

        // Leading dot ".corp.example" rejects apex "corp.example"
        using var apexLeaf = CreateLeaf("CN=corp.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "corp.example" });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { apexLeaf.RawData, midCert.RawData }, "corp.example", opts));

        // Excluded DNS "bad.corp.example" rejected
        using var excludedDnsLeaf = CreateLeaf("CN=bad.corp.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "bad.corp.example" });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { excludedDnsLeaf.RawData, midCert.RawData }, "bad.corp.example", opts));

        // Outside permitted DNS rejected
        using var outsideDnsLeaf = CreateLeaf("CN=other.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "other.example" });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { outsideDnsLeaf.RawData, midCert.RawData }, "other.example", opts));

        // Excluded IPv4 10.1.2.3 inside 10.1.0.0/16 rejected
        using var excludedIpLeaf = CreateLeaf("CN=exip.corp.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "exip.corp.example" }, ipAddresses: new[] { IPAddress.Parse("10.1.2.3") });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { excludedIpLeaf.RawData, midCert.RawData }, "exip.corp.example", opts));

        // Outside permitted IPv4 192.168.1.1 rejected
        using var outsideIpv4Leaf = CreateLeaf("CN=out4.corp.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "out4.corp.example" }, ipAddresses: new[] { IPAddress.Parse("192.168.1.1") });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { outsideIpv4Leaf.RawData, midCert.RawData }, "out4.corp.example", opts));

        // Outside permitted IPv6 2001:db9::1 rejected
        using var outsideIpv6Leaf = CreateLeaf("CN=out6.corp.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "out6.corp.example" }, ipAddresses: new[] { IPAddress.Parse("2001:db9::1") });
        Assert.Throws<CertificateValidationException>(() => CertificateVerifier.VerifyChain(new[] { outsideIpv6Leaf.RawData, midCert.RawData }, "out6.corp.example", opts));
    }

    [Fact]
    public void MaxChainLength10AndMaxSignatureChecks100AreEnforced()
    {
        // Build a 10-intermediate chain (leaf + 9 intermediates + root = 11 certs -> exceeds MaxChainLength=10;
        // leaf + 8 intermediates + root = 10 certs -> passes MaxChainLength=10).
        var keys = new List<RSA>();
        var certs = new List<X509Certificate2>();
        try
        {
            var rootKey = RSA.Create(2048);
            keys.Add(rootKey);
            var rootCert = CreateCa("CN=Deep Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            certs.Add(rootCert);

            var parent = rootCert;
            for (var level = 1; level <= 9; level++)
            {
                var k = RSA.Create(2048);
                keys.Add(k);
                var mid = CreateCa($"CN=Deep Mid {level}", k, parent, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                certs.Add(mid);
                parent = mid;
            }

            var leafKey = RSA.Create(2048);
            keys.Add(leafKey);

            // Leaf under Deep Mid 8 => [leaf, mid8..mid1, root] = 10 certs (allowed)
            using var leaf10 = CreateLeaf("CN=len10.example.com", leafKey, certs[8], HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "len10.example.com" });
            var chain10Input = new List<byte[]> { leaf10.RawData };
            for (var i = 8; i >= 1; i--)
                chain10Input.Add(certs[i].RawData);

            var ok10 = CertificateVerifier.VerifyChain(chain10Input, "len10.example.com", CustomOptions(CreateCustomDb(rootCert)));
            Assert.Equal(10, ok10.Count);

            // Leaf under Deep Mid 9 => [leaf, mid9..mid1, root] = 11 certs (rejected > 10)
            using var leaf11 = CreateLeaf("CN=len11.example.com", leafKey, certs[9], HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "len11.example.com" });
            var chain11Input = new List<byte[]> { leaf11.RawData };
            for (var i = 9; i >= 1; i--)
                chain11Input.Add(certs[i].RawData);

            var exLen = Assert.Throws<CertificateValidationException>(() =>
                CertificateVerifier.VerifyChain(chain11Input, "len11.example.com", CustomOptions(CreateCustomDb(rootCert))));
            Assert.Contains("at most 10", exLen.Message, StringComparison.Ordinal);
        }
        finally
        {
            foreach (var c in certs) c.Dispose();
            foreach (var k in keys) k.Dispose();
        }

        // Branching graph to exceed MaxSignatureChecks = 100 (4 levels x 4 cross-issued certs sharing keys = 4 + 16 + 64 + 256 edges)
        using var k0 = RSA.Create(2048);
        using var k1 = RSA.Create(2048);
        using var k2 = RSA.Create(2048);
        using var k3 = RSA.Create(2048);
        using var k4 = RSA.Create(2048);
        using var kLeaf = RSA.Create(2048);
        using var graphRoot = CreateCa("CN=Graph Root", k4, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var missingAnchor = CreateCa("CN=Missing Anchor", k4, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var graphCerts = new List<X509Certificate2>();
        try
        {
            var levelParents = new[] { missingAnchor };
            var levelKeys = new[] { k3, k2, k1 };
            var levelNames = new[] { "CN=Graph L3", "CN=Graph L2", "CN=Graph L1" };

            for (var lvl = 0; lvl < 3; lvl++)
            {
                var nextLevel = new List<X509Certificate2>();
                for (var copy = 0; copy < 4; copy++)
                {
                    var mid = CreateCa(levelNames[lvl], levelKeys[lvl], levelParents[0], HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                    graphCerts.Add(mid);
                    nextLevel.Add(mid);
                }
                levelParents = nextLevel.ToArray();
            }

            // 4 intermediates at L0 signed by L1 (each verifiable by k1)
            using var l1Sample = CreateCa("CN=Graph L1", k1, missingAnchor, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            using var l0Signer = CreateCa("CN=Graph L0", k0, l1Sample, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            using var graphLeaf = CreateLeaf("CN=graph.example.com", kLeaf, l0Signer, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "graph.example.com" });

            var derChain = new List<byte[]> { graphLeaf.RawData };
            for (var copy = 0; copy < 4; copy++)
            {
                var mid0 = CreateCa("CN=Graph L0", k0, l1Sample, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
                graphCerts.Add(mid0);
                derChain.Add(mid0.RawData);
            }
            foreach (var gc in graphCerts)
                derChain.Add(gc.RawData);

            var exSig = Assert.Throws<CertificateValidationException>(() =>
                CertificateVerifier.VerifyChain(derChain, "graph.example.com", CustomOptions(CreateCustomDb(graphRoot))));
            Assert.Contains("signature check attempts limit reached", exSig.Message, StringComparison.Ordinal);
        }
        finally
        {
            foreach (var c in graphCerts) c.Dispose();
        }
    }

    [Fact]
    public void Ed25519RootAndLeafChainPassesVerification()
    {
        var rootDer = Convert.FromBase64String(
            "MIIBCTCBvKADAgECAgEBMAUGAytlcDAcMRowGAYDVQQDDBFFZDI1NTE5IFRlc3QgUm9vdDAeFw0yNjAxMDEwMDAwMDBaFw0yODAxMDEwMDAwMDBaMBwxGjAYBgNVBAMMEUVkMjU1MTkgVGVzdCBSb290MCowBQYDK2VwAyEALMdzO+rG7aEAoNaBdTtjBqa3fwFcuG4BkfaFvghjEnqjIzAhMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgEGMAUGAytlcANBAHVvJ4enmg5Xhgc6Z+W5CpCw6A7MXeYakg1urUk7BBSKutwCUOgtereygVbx4S4wauBL9ausyJ2N+8plF5hjegU=");
        var leafDer = Convert.FromBase64String(
            "MIIBLTCB4KADAgECAgECMAUGAytlcDAcMRowGAYDVQQDDBFFZDI1NTE5IFRlc3QgUm9vdDAeFw0yNjAxMDEwMDAwMDBaFw0yODAxMDEwMDAwMDBaMB4xHDAaBgNVBAMME2VkMjU1MTkuZXhhbXBsZS5jb20wKjAFBgMrZXADIQCLan3PTaCMY4TjJRxvxp6ecyuxzhB/4k7xTzSJf4rpuqNFMEMwDAYDVR0TAQH/BAIwADAeBgNVHREEFzAVghNlZDI1NTE5LmV4YW1wbGUuY29tMBMGA1UdJQQMMAoGCCsGAQUFBwMBMAUGAytlcANBAG1gSN/TSI3L1VF5DxnoGvd1lW3beVpIaHMJs+ajXjOhAnNBaSURRWecC0hAqxCivbuGUl2XtV8k5B6Tk8Wo5ww=");

        var rootCert = DerCertificate.Parse(rootDer);
        var leafCert = DerCertificate.Parse(leafDer);
        Assert.Equal("1.3.101.112", rootCert.PublicKeyAlgorithmOid);
        Assert.True(rootCert.VerifySignature(rootCert));
        Assert.True(leafCert.VerifySignature(rootCert));

        var db = new RootCertificateDatabase();
        db.AddDer(rootDer);
        var verified = CertificateVerifier.VerifyChain(new[] { leafDer }, "ed25519.example.com", CustomOptions(db));
        Assert.Equal(2, verified.Count);
        Assert.Equal("CN=ed25519.example.com", verified[0].SubjectText);
    }

    [Fact]
    public void CertificatePinnerPassesValidPinAndThrowsBadPinExceptionOnMismatch()
    {
        using var rootKey = RSA.Create(2048);
        using var midKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);

        using var rootCert = CreateCa("CN=Pin Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var midCert = CreateCa("CN=Pin Mid", midKey, rootCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        using var leafCert = CreateLeaf("CN=api.pinned.example", leafKey, midCert, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1, dnsNames: new[] { "*.pinned.example" });

        var parsedLeaf = DerCertificate.Parse(leafCert.RawData);
        var parsedMid = DerCertificate.Parse(midCert.RawData);
        var db = CreateCustomDb(rootCert);

        // Matching leaf pin using sha256/<base64>
        var pinnerLeaf = new CertificatePinner();
        pinnerLeaf.AddPin("api.pinned.example", "sha256/" + parsedLeaf.PinSha256Base64);
        var optsLeaf = CustomOptions(db, pinnerLeaf);
        Assert.Equal(3, CertificateVerifier.VerifyChain(new[] { leafCert.RawData, midCert.RawData }, "api.pinned.example", optsLeaf).Count);

        // Matching intermediate pin using wildcard pattern + raw base64
        var pinnerWildcard = new CertificatePinner();
        pinnerWildcard.AddPin("*.pinned.example", parsedMid.PinSha256Base64);
        var optsWildcard = CustomOptions(db, pinnerWildcard);
        Assert.Equal(3, CertificateVerifier.VerifyChain(new[] { leafCert.RawData, midCert.RawData }, "api.pinned.example", optsWildcard).Count);

        // Mismatched pin throws BadPinException
        var badPin = Convert.ToBase64String(new byte[32]);
        var pinnerBad = new CertificatePinner();
        pinnerBad.AddPin("*.pinned.example", "sha256/" + badPin);
        var optsBad = CustomOptions(db, pinnerBad);

        var ex = Assert.Throws<BadPinException>(() =>
            CertificateVerifier.VerifyChain(new[] { leafCert.RawData, midCert.RawData }, "api.pinned.example", optsBad));
        Assert.Contains("bad ssl pin detected, found pins:", ex.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void UnknownCriticalExtensionAndIncompatibleEkuAreRejected()
    {
        using var rootKey = RSA.Create(2048);
        using var leafKey = RSA.Create(2048);
        using var rootCert = CreateCa("CN=Ext Root", rootKey, null, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        var opts = CustomOptions(CreateCustomDb(rootCert));

        // Unknown critical extension 1.2.3.4.5.6.7 on leaf
        var unknownCriticalExt = new X509Extension(new Oid("1.2.3.4.5.6.7"), new byte[] { 0x05, 0x00 }, critical: true);
        using var critLeaf = CreateLeaf(
            "CN=crit.example.com",
            leafKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "crit.example.com" },
            extraExtensions: new[] { unknownCriticalExt });

        var parsedCrit = DerCertificate.Parse(critLeaf.RawData);
        Assert.Contains("1.2.3.4.5.6.7", parsedCrit.UnhandledCriticalExtensions);
        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { critLeaf.RawData }, "crit.example.com", opts));

        // Incompatible EKU (clientAuth only, no serverAuth)
        using var clientOnlyLeaf = CreateLeaf(
            "CN=clientonly.example.com",
            leafKey,
            rootCert,
            HashAlgorithmName.SHA256,
            RSASignaturePadding.Pkcs1,
            dnsNames: new[] { "clientonly.example.com" },
            ekuOids: new[] { "1.3.6.1.5.5.7.3.2" });

        Assert.Throws<CertificateValidationException>(() =>
            CertificateVerifier.VerifyChain(new[] { clientOnlyLeaf.RawData }, "clientonly.example.com", opts));
    }

    private static RootCertificateDatabase CreateCustomDb(params X509Certificate2[] roots)
    {
        var db = new RootCertificateDatabase();
        foreach (var root in roots)
            db.AddDer(root.RawData);
        return db;
    }

    private static CertificateVerifyOptions CustomOptions(RootCertificateDatabase db, CertificatePinner? pinner = null) =>
        new()
        {
            CustomRoots = db,
            UseEmbeddedDefaultRoots = false,
            VerificationTime = BaseNow,
            Pinner = pinner,
        };

    private static X509Certificate2 CreateCa(
        string subject,
        RSA key,
        X509Certificate2? issuer,
        HashAlgorithmName hashAlg,
        RSASignaturePadding padding,
        int? pathLen = null,
        X509KeyUsageFlags keyUsageFlags = X509KeyUsageFlags.KeyCertSign | X509KeyUsageFlags.CrlSign,
        DateTimeOffset? notBefore = null,
        DateTimeOffset? notAfter = null,
        IEnumerable<X509Extension>? extraExtensions = null)
    {
        var req = new CertificateRequest(subject, key, hashAlg, padding);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, pathLen.HasValue, pathLen ?? 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(keyUsageFlags, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        if (extraExtensions is not null)
        {
            foreach (var ext in extraExtensions)
                req.CertificateExtensions.Add(ext);
        }

        var nb = notBefore ?? BaseNow.AddDays(-60);
        var na = notAfter ?? BaseNow.AddDays(365);
        if (issuer is null)
            return req.CreateSelfSigned(nb, na);
        using var cert = req.Create(issuer, nb, na, NewSerial());
        return cert.CopyWithPrivateKey(key);
    }

    private static X509Certificate2 CreateNonCaIntermediate(string subject, RSA key, X509Certificate2 issuer)
    {
        var req = new CertificateRequest(subject, key, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature, true));
        using var cert = req.Create(issuer, BaseNow.AddDays(-60), BaseNow.AddDays(365), NewSerial());
        return cert.CopyWithPrivateKey(key);
    }

    private static X509Certificate2 CreateLeafWithRsaSigner(
        string subject,
        RSA key,
        X500DistinguishedName issuerSubject,
        RSA issuerKey,
        HashAlgorithmName hashAlg,
        RSASignaturePadding padding,
        IEnumerable<string>? dnsNames,
        DateTimeOffset notBefore,
        DateTimeOffset notAfter)
    {
        var req = new CertificateRequest(subject, key, hashAlg, padding);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, true));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new("1.3.6.1.5.5.7.3.1") }, false));
        if (dnsNames is not null)
        {
            var san = new SubjectAlternativeNameBuilder();
            foreach (var d in dnsNames)
                san.AddDnsName(d);
            req.CertificateExtensions.Add(san.Build());
        }
        return req.Create(issuerSubject, X509SignatureGenerator.CreateForRSA(issuerKey, padding), notBefore, notAfter, NewSerial());
    }

    private static X509Certificate2 CreateLeaf(
        string subject,
        RSA key,
        X509Certificate2 issuer,
        HashAlgorithmName hashAlg,
        RSASignaturePadding padding,
        IEnumerable<string>? dnsNames = null,
        IEnumerable<IPAddress>? ipAddresses = null,
        IEnumerable<string>? ekuOids = null,
        DateTimeOffset? notBefore = null,
        DateTimeOffset? notAfter = null,
        IEnumerable<X509Extension>? extraExtensions = null)
    {
        var req = new CertificateRequest(subject, key, hashAlg, padding);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, true));

        var oids = new OidCollection();
        foreach (var oid in ekuOids ?? new[] { "1.3.6.1.5.5.7.3.1" })
            oids.Add(new Oid(oid));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(oids, false));

        if (dnsNames is not null || ipAddresses is not null)
        {
            var san = new SubjectAlternativeNameBuilder();
            if (dnsNames is not null)
            {
                foreach (var d in dnsNames)
                    san.AddDnsName(d);
            }
            if (ipAddresses is not null)
            {
                foreach (var ip in ipAddresses)
                    san.AddIpAddress(ip);
            }
            req.CertificateExtensions.Add(san.Build());
        }

        if (extraExtensions is not null)
        {
            foreach (var ext in extraExtensions)
                req.CertificateExtensions.Add(ext);
        }

        return req.Create(issuer, notBefore ?? BaseNow.AddDays(-1), notAfter ?? BaseNow.AddDays(30), NewSerial());
    }

    private static X509Certificate2 CreateEcCa(string subject, ECDsa key, X509Certificate2? issuer)
    {
        var req = new CertificateRequest(subject, key, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(true, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.KeyCertSign | X509KeyUsageFlags.CrlSign, true));
        req.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(req.PublicKey, false));
        var nb = BaseNow.AddDays(-60);
        var na = BaseNow.AddDays(365);
        if (issuer is null)
            return req.CreateSelfSigned(nb, na);
        using var cert = req.Create(issuer, nb, na, NewSerial());
        return cert.CopyWithPrivateKey(key);
    }

    private static X509Certificate2 CreateEcLeaf(string subject, ECDsa key, X509Certificate2 issuer, IEnumerable<string> dnsNames)
    {
        var req = new CertificateRequest(subject, key, HashAlgorithmName.SHA256);
        req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, true));
        req.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature, true));
        req.CertificateExtensions.Add(new X509EnhancedKeyUsageExtension(new OidCollection { new("1.3.6.1.5.5.7.3.1") }, false));
        var san = new SubjectAlternativeNameBuilder();
        foreach (var d in dnsNames)
            san.AddDnsName(d);
        req.CertificateExtensions.Add(san.Build());
        return req.Create(issuer, BaseNow.AddDays(-1), BaseNow.AddDays(30), NewSerial());
    }

    private static byte[] NewSerial()
    {
        var serial = new byte[8];
        RandomNumberGenerator.Fill(serial);
        serial[0] = (byte)((serial[0] & 0x7F) | 0x01);
        return serial;
    }

    private static X509Extension BuildNameConstraintsExtension(
        IEnumerable<string>? permittedDns = null,
        IEnumerable<string>? excludedDns = null,
        IEnumerable<(IPAddress Net, IPAddress Mask)>? permittedIps = null,
        IEnumerable<(IPAddress Net, IPAddress Mask)>? excludedIps = null)
    {
        var fields = new List<byte[]>();

        var permittedSubtrees = BuildSubtrees(permittedDns, permittedIps);
        if (permittedSubtrees.Length > 0)
            fields.Add(BuildPrimitiveTlv(0xA0, permittedSubtrees));

        var excludedSubtrees = BuildSubtrees(excludedDns, excludedIps);
        if (excludedSubtrees.Length > 0)
            fields.Add(BuildPrimitiveTlv(0xA1, excludedSubtrees));

        var seq = BuildSequence(fields);
        return new X509Extension(new Oid("2.5.29.30"), seq, critical: true);
    }

    private static byte[] BuildSubtrees(
        IEnumerable<string>? dnsList,
        IEnumerable<(IPAddress Net, IPAddress Mask)>? ipList)
    {
        var items = new List<byte[]>();
        if (dnsList is not null)
        {
            foreach (var dns in dnsList)
            {
                var gn = BuildPrimitiveTlv(0x82, Encoding.ASCII.GetBytes(dns));
                items.Add(BuildSequence(new[] { gn }));
            }
        }
        if (ipList is not null)
        {
            foreach (var (net, mask) in ipList)
            {
                var n = net.GetAddressBytes();
                var m = mask.GetAddressBytes();
                var combined = new byte[n.Length + m.Length];
                n.CopyTo(combined, 0);
                m.CopyTo(combined, n.Length);
                var gn = BuildPrimitiveTlv(0x87, combined);
                items.Add(BuildSequence(new[] { gn }));
            }
        }

        var total = 0;
        foreach (var item in items) total += item.Length;
        var buf = new byte[total];
        var pos = 0;
        foreach (var item in items)
        {
            item.CopyTo(buf, pos);
            pos += item.Length;
        }
        return buf;
    }

    private static byte[] BuildSequence(IEnumerable<byte[]> children)
    {
        var total = 0;
        foreach (var c in children) total += c.Length;
        var inner = new byte[total];
        var pos = 0;
        foreach (var c in children)
        {
            c.CopyTo(inner, pos);
            pos += c.Length;
        }
        return BuildPrimitiveTlv(0x30, inner);
    }

    private static byte[] BuildPrimitiveTlv(byte tag, ReadOnlySpan<byte> content)
    {
        var lenBytes = content.Length switch
        {
            < 128 => new[] { (byte)content.Length },
            <= 255 => new byte[] { 0x81, (byte)content.Length },
            _ => new byte[] { 0x82, (byte)(content.Length >> 8), (byte)content.Length },
        };

        var result = new byte[1 + lenBytes.Length + content.Length];
        result[0] = tag;
        lenBytes.CopyTo(result, 1);
        content.CopyTo(result.AsSpan(1 + lenBytes.Length));
        return result;
    }
}
