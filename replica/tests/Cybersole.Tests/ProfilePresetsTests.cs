using Cybersole.Http.Profiles;
using Xunit;

namespace Cybersole.Tests;

public sealed class ProfilePresetsTests
{
    [Fact]
    public void RegistryContainsExact82Slots84KeysAndDefaults()
    {
        Assert.Equal("chrome_131", ProfileRegistry.DefaultFingerprint);
        Assert.Equal("chrome_131", Fingerprints.DefaultFingerprint);
        Assert.Equal("chrome_133", ProfileRegistry.DefaultClientOptionsProfile);

        Assert.Equal(82, ProfileRegistry.AllSlotProfiles.Count);
        Assert.Equal(84, ProfileRegistry.RegisteredKeys.Count);
        Assert.Equal(84, ProfileRegistry.MappedTlsClients.Count);
        Assert.Equal(18, Fingerprints.All.Count);

        var seenNames = new HashSet<string>(StringComparer.Ordinal);
        for (int i = 0; i < ProfileRegistry.AllSlotProfiles.Count; i++)
        {
            ClientProfile slotProfile = ProfileRegistry.AllSlotProfiles[i];
            Assert.Equal(i, slotProfile.SlotIndex);
            Assert.True(seenNames.Add(slotProfile.Name), $"Duplicate slot profile name: {slotProfile.Name}");
        }

        var seenKeys = new HashSet<string>(StringComparer.Ordinal);
        var mappedDistinctSlots = new HashSet<int>();
        foreach (string key in ProfileRegistry.RegisteredKeys)
        {
            Assert.True(seenKeys.Add(key), $"Duplicate registry key: {key}");
            Assert.True(ProfileRegistry.TryGet(key, out ClientProfile? resolved), $"Missing mapping for key: {key}");
            Assert.NotNull(resolved);
            mappedDistinctSlots.Add(resolved!.SlotIndex);
        }

        // 81 mapped slots; slot index 24 (binary #25 ConfirmedAndroid2) is unmapped in sub_1412BAC30.
        Assert.Equal(81, mappedDistinctSlots.Count);
        Assert.DoesNotContain(24, mappedDistinctSlots);
        Assert.Equal("ConfirmedAndroid2", ProfileRegistry.AllSlotProfiles[24].Name);
        Assert.False(ProfileRegistry.TryGet("confirmed_android_2", out _));
        Assert.False(ProfileRegistry.TryGet("ConfirmedAndroid2", out _));

        // Alias pairs share exact ClientProfile instances.
        Assert.Same(ProfileRegistry.GetRequired("mms_ios"), ProfileRegistry.GetRequired("mms_ios_1"));
        Assert.Same(ProfileRegistry.GetRequired("mesh_ios"), ProfileRegistry.GetRequired("mesh_ios_1"));
        Assert.Same(ProfileRegistry.GetRequired("mesh_android"), ProfileRegistry.GetRequired("mesh_android_1"));

        // Every Fingerprints constant resolves in the registry.
        foreach (string fp in Fingerprints.All)
        {
            Assert.True(ProfileRegistry.TryGet(fp, out ClientProfile? p) && p is not null);
        }
    }

    [Fact]
    public void RegistryLookupIsCaseSensitiveAndThrowsExactUnknownProfileException()
    {
        Assert.True(ProfileRegistry.TryGet("chrome_131_PSK", out ClientProfile? psk));
        Assert.Same(UtlsPresets.Chrome_131_PSK, psk);
        Assert.False(ProfileRegistry.TryGet("chrome_131_psk", out _));
        Assert.False(ProfileRegistry.TryGet(null, out _));
        Assert.False(ProfileRegistry.TryGet(string.Empty, out _));

        Assert.Same(UtlsPresets.Chrome_131, ProfileRegistry.GetOrDefault(null));
        Assert.Same(UtlsPresets.Chrome_131, ProfileRegistry.GetOrDefault("does_not_exist"));
        Assert.Same(UtlsPresets.Chrome_152, ProfileRegistry.GetOrDefault("chrome_152"));

        var ex = Assert.Throws<UnknownProfileException>(() => ProfileRegistry.GetRequired("nonexistent_profile"));
        Assert.Equal("Unknown profile \"nonexistent_profile\"", ex.Message);
        Assert.Equal(unchecked((int)0x80070057), ex.HResult);
    }

    [Fact]
    public void EverySlotProducesValidClientHelloSpecAndConsistentSessionResumption()
    {
        var expectedPskNames = new HashSet<string>(StringComparer.Ordinal)
        {
            "Firefox_147_PSK",
            "Firefox_146_PSK",
            "Chrome_130_PSK",
            "Chrome_131_PSK",
            "Chrome_152_PSK",
            "Chrome_150_PSK",
            "Chrome_146_PSK",
            "Chrome_144_PSK",
            "Chrome_133_PSK",
            "Chrome_116_PSK",
            "Chrome_116_PSK_PQ",
            "Brave_146_PSK",
        };

        foreach (ClientProfile profile in ProfileRegistry.AllSlotProfiles)
        {
            ClientHelloSpec spec = profile.CreateClientHelloSpec();
            Assert.NotNull(spec);
            Assert.NotEmpty(spec.CipherSuites);
            Assert.Single(spec.CompressionMethods);
            Assert.Equal(0, spec.CompressionMethods[0]);
            Assert.NotEmpty(spec.Extensions);
            Assert.True(spec.MinVersion >= TlsVersion.Tls10 && spec.MinVersion <= spec.MaxVersion);
            Assert.True(spec.MaxVersion is TlsVersion.Tls12 or TlsVersion.Tls13);
            Assert.True(profile.Tls12Supported);
            Assert.Equal(spec.MaxVersion == TlsVersion.Tls13, profile.Tls13Supported);
            Assert.NotEmpty(profile.Http2Settings.PseudoHeaderOrder);

            bool hasPsk = spec.HasExtension(TlsExtensionType.PreSharedKey);
            bool expectedPsk = expectedPskNames.Contains(profile.Name);
            Assert.Equal(expectedPsk, profile.SupportsSessionResumption);
            Assert.Equal(expectedPsk, hasPsk);

            if (profile.SupportsSessionResumption)
            {
                Assert.IsType<PreSharedKeyExtension>(spec.Extensions[^1]);
                for (int i = 0; i < spec.Extensions.Count - 1; i++)
                {
                    Assert.IsNotType<PreSharedKeyExtension>(spec.Extensions[i]);
                }
            }
        }
    }

    [Fact]
    public void PostQuantumKeySharesMatchExactBrowserGenerations()
    {
        // Modern Chrome 131+ and 144..152 advertise X25519MLKEM768 (0x11EC)
        string[] mlkemChrome =
        {
            "chrome_131", "chrome_131_PSK", "chrome_133", "chrome_133_PSK",
            "chrome_144", "chrome_144_PSK", "chrome_146", "chrome_146_PSK",
            "chrome_150", "chrome_150_PSK", "chrome_152", "chrome_152_PSK",
            "brave_146", "brave_146_PSK", "chrome_ios_26_1", "safari_ios_26_0",
        };
        foreach (string key in mlkemChrome)
        {
            ClientHelloSpec spec = ProfileRegistry.GetRequired(key).CreateClientHelloSpec();
            KeyShareExtension? ks = spec.GetExtension<KeyShareExtension>();
            SupportedGroupsExtension? sg = spec.GetExtension<SupportedGroupsExtension>();
            Assert.NotNull(ks);
            Assert.NotNull(sg);
            Assert.Contains(ks!.Entries, e => e.Group == NamedGroupId.X25519MLKEM768);
            Assert.Contains(NamedGroupId.X25519MLKEM768, sg!.Groups);
        }

        // Legacy PQ Chrome 116_PSK_PQ and 124 advertise X25519Kyber768Draft00 (0x6399); 130_PSK has only X25519
        foreach (string key in new[] { "chrome_116_PSK_PQ", "chrome_124" })
        {
            ClientHelloSpec spec = ProfileRegistry.GetRequired(key).CreateClientHelloSpec();
            KeyShareExtension? ks = spec.GetExtension<KeyShareExtension>();
            SupportedGroupsExtension? sg = spec.GetExtension<SupportedGroupsExtension>();
            Assert.NotNull(ks);
            Assert.NotNull(sg);
            Assert.Contains(ks!.Entries, e => e.Group == NamedGroupId.X25519Kyber768Draft00);
            Assert.Contains(NamedGroupId.X25519Kyber768Draft00, sg!.Groups);
        }

        KeyShareExtension? chrome130Ks = UtlsPresets.Chrome_130_PSK.CreateClientHelloSpec().GetExtension<KeyShareExtension>();
        Assert.NotNull(chrome130Ks);
        Assert.DoesNotContain(chrome130Ks!.Entries, e => e.Group is NamedGroupId.X25519MLKEM768 or NamedGroupId.X25519Kyber768Draft00);

        // Firefox 132..148 advertise X25519MLKEM768 (0x11EC)
        foreach (string key in new[] { "firefox_132", "firefox_133", "firefox_135", "firefox_146_PSK", "firefox_147", "firefox_147_PSK", "firefox_148" })
        {
            ClientHelloSpec spec = ProfileRegistry.GetRequired(key).CreateClientHelloSpec();
            KeyShareExtension? ks = spec.GetExtension<KeyShareExtension>();
            Assert.NotNull(ks);
            Assert.Contains(ks!.Entries, e => e.Group == NamedGroupId.X25519MLKEM768);
        }

        // Chrome QUIC shared spec also advertises X25519MLKEM768 + X25519
        ClientHelloSpec quicSpec = ChromeQuicSpecs.CreateClientHelloSpec();
        KeyShareExtension? quicKs = quicSpec.GetExtension<KeyShareExtension>();
        Assert.NotNull(quicKs);
        Assert.Equal(2, quicKs!.Entries.Count);
        Assert.Equal(NamedGroupId.X25519MLKEM768, quicKs.Entries[0].Group);
        Assert.Equal(NamedGroupId.X25519, quicKs.Entries[1].Group);
        Assert.IsType<PreSharedKeyExtension>(quicSpec.Extensions[^1]);
    }

    [Fact]
    public void TrustAnchors0xCa34MatchesExactChrome146AndChrome152Profiles()
    {
        foreach (ClientProfile profile in ProfileRegistry.AllSlotProfiles)
        {
            TrustAnchorsExtension? ta = profile.CreateClientHelloSpec().GetExtension<TrustAnchorsExtension>();
            if (profile.Name is "Chrome_146" or "Chrome_146_PSK")
            {
                Assert.NotNull(ta);
                Assert.Empty(ta!.AnchorIds);
                Assert.Equal(new byte[] { 0x00, 0x00 }, ta.RawPayload);
            }
            else if (profile.Name is "Chrome_152" or "Chrome_152_PSK")
            {
                Assert.NotNull(ta);
                Assert.Equal(28, ta!.AnchorIds.Count);
                Assert.Equal(186, ta.RawPayload.Length);
                Assert.Equal(0x00, ta.RawPayload[0]);
                Assert.Equal(0xB8, ta.RawPayload[1]);
            }
            else
            {
                Assert.Null(ta);
            }
        }
    }

    [Fact]
    public void Http3AndQuicSupportMatchesExactChrome146Chrome150AndFirefoxQuirks()
    {
        // Chrome_146 and Chrome_150 wire ChromeQuicSpecs (SupportsHttp3 == true) while Http3Settings remains null
        foreach (ClientProfile p in new[] { UtlsPresets.Chrome_146, UtlsPresets.Chrome_150 })
        {
            Assert.True(p.SupportsHttp3);
            Assert.NotNull(p.QuicSpec);
            Assert.NotNull(p.CreateQuicClientHelloSpec);
            Assert.Null(p.Http3Settings);
            IReadOnlyList<(ulong Id, ulong Value)> dyn = Http3SettingsSpec.BuildWireSettings(p.Http3Settings);
            Assert.Single(dyn);
            Assert.Equal((Http3SettingId.H3Datagram, 1UL), dyn[0]);
        }

        // Full H3 Chrome presets
        foreach (ClientProfile p in new[]
        {
            UtlsPresets.Chrome_144, UtlsPresets.Chrome_144_PSK,
            UtlsPresets.Chrome_146_PSK, UtlsPresets.Chrome_150_PSK,
            UtlsPresets.Chrome_152, UtlsPresets.Chrome_152_PSK,
        })
        {
            Assert.True(p.SupportsHttp3);
            Assert.NotNull(p.QuicSpec);
            Assert.NotNull(p.Http3Settings);
            Assert.Equal(65536UL, p.Http3Settings!.QpackMaxTableCapacity);
            Assert.Equal(100UL, p.Http3Settings.QpackBlockedStreams);
            Assert.Equal(262144UL, p.Http3Settings.MaxFieldSectionSize);
            Assert.True(p.Http3Settings.EnableH3Datagram);
            Assert.True(p.Http3Settings.SendGreaseSettings);
            Assert.True(p.Http3Settings.SendGreaseFrame);
            Assert.Equal(984832u, p.Http3Settings.ChromeH3Flag);
        }

        // Firefox 147 / 147_PSK / 148 populate Http3Settings while QuicSpec is null (SupportsHttp3 == false)
        foreach (ClientProfile p in new[] { UtlsPresets.Firefox_148, UtlsPresets.Firefox_147, UtlsPresets.Firefox_147_PSK })
        {
            Assert.False(p.SupportsHttp3);
            Assert.Null(p.QuicSpec);
            Assert.NotNull(p.Http3Settings);
            Assert.Equal(65536UL, p.Http3Settings!.QpackMaxTableCapacity);
            Assert.Equal(20UL, p.Http3Settings.QpackBlockedStreams);
            Assert.Null(p.Http3Settings.MaxFieldSectionSize);
            Assert.True(p.Http3Settings.EnableH3Datagram);
            Assert.True(p.Http3Settings.EnableConnectProtocol);
            Assert.False(p.Http3Settings.SendGreaseSettings);
            Assert.True(p.Http3Settings.SendGreaseFrame);
            Assert.Equal(new ulong[] { 1, 7, 0x2B603742, 0xFFD277, 51, 8 }, p.Http3Settings.SettingsOrder);
        }

        // Chrome_IOS_26_1 strips h2
        Assert.True(UtlsPresets.Chrome_IOS_26_1.DisableHttp2);
        Assert.False(UtlsPresets.Chrome_IOS_26_1.SupportsHttp3);
        Assert.Equal(new[] { "http/1.1" }, UtlsPresets.Chrome_IOS_26_1.GetEffectiveAlpn());
    }

    [Fact]
    public void GreaseResolverEnforcesDistinctGreaseExtensionsAndValidRfc8701Values()
    {
        for (int seed = 0; seed < 100; seed++)
        {
            var rng = new Random(seed);
            ClientHelloSpec resolved = GreaseHelper.ResolveGrease(UtlsPresets.Chrome_152_PSK.CreateClientHelloSpec(), rng);

            Assert.True(GreaseHelper.IsGrease(resolved.CipherSuites[0]));

            var greaseExts = resolved.Extensions.OfType<GreaseExtension>().ToArray();
            Assert.Equal(2, greaseExts.Length);
            Assert.True(GreaseHelper.IsGrease(greaseExts[0].ResolvedType));
            Assert.True(GreaseHelper.IsGrease(greaseExts[1].ResolvedType));
            Assert.NotEqual(greaseExts[0].ResolvedType, greaseExts[1].ResolvedType);

            SupportedGroupsExtension sg = resolved.GetExtension<SupportedGroupsExtension>()!;
            KeyShareExtension ks = resolved.GetExtension<KeyShareExtension>()!;
            Assert.True(GreaseHelper.IsGrease(sg.Groups[0]));
            Assert.Equal(sg.Groups[0], ks.Entries[0].Group);
        }

        // Explicitly force g2 == g3 collision using a constant-zero PRNG; XOR 0x1010 guarantees distinctness
        var zeroRng = new ConstantZeroRandom();
        GreaseSet forced = GreaseHelper.GenerateSet(zeroRng);
        Assert.Equal(0x0A0A, forced.Extension1);
        Assert.Equal(0x1A1A, forced.Extension2);
        Assert.NotEqual(forced.Extension1, forced.Extension2);

        // >2 GreaseExtension entries throw InvalidOperationException
        var invalidSpec = new ClientHelloSpec(
            CipherSuites: new[] { CipherSuiteId.TLS_AES_128_GCM_SHA256 },
            Extensions: new TlsExtensionSpec[]
            {
                new GreaseExtension(),
                new SniExtension(),
                new GreaseExtension(),
                new GreaseExtension(),
            });
        Assert.Throws<InvalidOperationException>(() => GreaseHelper.ResolveGrease(invalidSpec));
    }

    [Fact]
    public void ExtensionShufflerPreservesPinnedPositionsAndSniAcross20Runs()
    {
        ClientHelloSpec pskTemplate = UtlsPresets.Chrome_152_PSK.CreateClientHelloSpec();
        Assert.True(pskTemplate.ShuffleExtensions);
        int secondGreaseIdx = pskTemplate.Extensions.Count - 2;
        int pskIdx = pskTemplate.Extensions.Count - 1;
        Assert.IsType<GreaseExtension>(pskTemplate.Extensions[0]);
        Assert.IsType<GreaseExtension>(pskTemplate.Extensions[secondGreaseIdx]);
        Assert.IsType<PreSharedKeyExtension>(pskTemplate.Extensions[pskIdx]);

        var distinctOrders = new HashSet<string>(StringComparer.Ordinal);
        for (int run = 0; run < 20; run++)
        {
            ClientHelloSpec shuffled = pskTemplate.Materialize(new Random(1000 + run));
            Assert.Equal(pskTemplate.Extensions.Count, shuffled.Extensions.Count);
            Assert.IsType<GreaseExtension>(shuffled.Extensions[0]);
            Assert.IsType<GreaseExtension>(shuffled.Extensions[secondGreaseIdx]);
            Assert.IsType<PreSharedKeyExtension>(shuffled.Extensions[pskIdx]);
            Assert.Single(shuffled.Extensions.OfType<SniExtension>());

            distinctOrders.Add(string.Join(",", shuffled.Extensions.Select(e => e.ExtensionType.ToString("X4"))));
        }
        Assert.True(distinctOrders.Count > 1, "Expected Chrome ExtensionShuffler to permute interior extensions across runs.");

        // Verify PaddingExtension stays pinned on Chrome_117 across 20 runs
        ClientHelloSpec chrome117Template = UtlsPresets.Chrome_117.CreateClientHelloSpec();
        int padIndex = -1;
        for (int i = 0; i < chrome117Template.Extensions.Count; i++)
        {
            if (chrome117Template.Extensions[i] is PaddingExtension)
            {
                padIndex = i;
                break;
            }
        }
        Assert.Equal(17, padIndex);
        for (int run = 0; run < 20; run++)
        {
            ClientHelloSpec shuffled = chrome117Template.Materialize(new Random(2000 + run));
            Assert.IsType<PaddingExtension>(shuffled.Extensions[padIndex]);
            Assert.Single(shuffled.Extensions.OfType<SniExtension>());
        }

        // Profiles with ShuffleExtensions=false preserve exact template order
        ClientHelloSpec firefoxSpec = UtlsPresets.Firefox_148.CreateClientHelloSpec();
        Assert.False(firefoxSpec.ShuffleExtensions);
        ClientHelloSpec materialized = firefoxSpec.Materialize(new Random(42));
        Assert.Equal(
            firefoxSpec.Extensions.Select(e => e.ExtensionType),
            materialized.Extensions.Select(e => e.ExtensionType));
    }

    [Fact]
    public void BoringPaddingAndSniSanitizationMatchIdaRules()
    {
        Assert.Equal(0, PaddingExtension.CalculatePaddingBytes(255));
        Assert.Equal(252, PaddingExtension.CalculatePaddingBytes(256)); // 256 + 4 + 252 == 512
        Assert.Equal(208, PaddingExtension.CalculatePaddingBytes(300)); // 300 + 4 + 208 == 512
        Assert.Equal(1, PaddingExtension.CalculatePaddingBytes(507));   // 507 + 4 + 1 == 512
        Assert.Equal(1, PaddingExtension.CalculatePaddingBytes(508));
        Assert.Equal(1, PaddingExtension.CalculatePaddingBytes(511));
        Assert.Equal(0, PaddingExtension.CalculatePaddingBytes(512));

        Assert.Equal("example.com", SniExtension.SanitizeHostName("example.com."));
        Assert.Null(SniExtension.SanitizeHostName("1.1.1.1"));
        Assert.Null(SniExtension.SanitizeHostName("[2001:db8::1%eth0]"));
        Assert.Null(SniExtension.SanitizeHostName("  "));
    }

    [Fact]
    public void Http2HeaderPrioritySuppressionAndStartupFramesMatchSpec()
    {
        Assert.True(UtlsPresets.ConfirmedAndroid.Http2Settings.IsHeaderPrioritySuppressed);
        Assert.True(UtlsPresets.Okhttp4Android10.Http2Settings.IsHeaderPrioritySuppressed);
        Assert.False(UtlsPresets.ConfirmedAndroid2.Http2Settings.IsHeaderPrioritySuppressed);

        Http2SettingsSpec ff123 = UtlsPresets.Firefox_123.Http2Settings;
        Assert.Equal(6, ff123.PriorityFrames.Count);
        Assert.Equal(15u, ff123.EffectiveInitialNextStreamId);
        Assert.Equal(new Http2HeaderPriority(13u, false, 41), ff123.EffectiveHeaderPriority);
        Assert.True(UtlsPresets.Firefox_132.Http2Settings.NoRfc7540Priorities);
        Assert.True(UtlsPresets.Chrome_IOS_26_1.Http2Settings.NoRfc7540Priorities);
    }

    private sealed class ConstantZeroRandom : Random
    {
        public override int Next(int maxValue) => 0;
        public override int Next(int minValue, int maxValue) => minValue;
    }
}
