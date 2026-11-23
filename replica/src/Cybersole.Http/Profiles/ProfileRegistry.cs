using System.Collections.ObjectModel;

namespace Cybersole.Http.Profiles;

/// <summary>Named fingerprint constants exposed by Cybersole.Http (0x145EF4D50..0x145EF4DD8).</summary>
public static class Fingerprints
{
    public const string CHROME_120 = "chrome_120";
    public const string CHROME_124 = "chrome_124";
    public const string CHROME_131 = "chrome_131";
    public const string CHROME_131_PSK = "chrome_131_PSK";
    public const string CHROME_133 = "chrome_133";
    public const string CHROME_133_PSK = "chrome_133_PSK";
    public const string CHROME_144 = "chrome_144";
    public const string CHROME_144_PSK = "chrome_144_PSK";
    public const string CHROME_146 = "chrome_146";
    public const string CHROME_146_PSK = "chrome_146_PSK";
    public const string CHROME_150 = "chrome_150";
    public const string CHROME_150_PSK = "chrome_150_PSK";
    public const string CHROME_152 = "chrome_152";
    public const string CHROME_152_PSK = "chrome_152_PSK";
    public const string IOS_17_0 = "safari_ios_17_0";
    public const string IOS_18_0 = "safari_ios_18_0";
    public const string IOS_18_5 = "safari_ios_18_5";
    public const string CHROME_IOS_26_1 = "chrome_ios_26_1";
    public const string DefaultFingerprint = CHROME_131;

    public static IReadOnlyList<string> All { get; } = Array.AsReadOnly(new[]
    {
        CHROME_120,
        CHROME_124,
        CHROME_131,
        CHROME_131_PSK,
        CHROME_133,
        CHROME_133_PSK,
        CHROME_144,
        CHROME_144_PSK,
        CHROME_146,
        CHROME_146_PSK,
        CHROME_150,
        CHROME_150_PSK,
        CHROME_152,
        CHROME_152_PSK,
        IOS_17_0,
        IOS_18_0,
        IOS_18_5,
        CHROME_IOS_26_1,
    });
}

/// <summary>
/// Case-sensitive registry mapping 84 string keys to 81 of the 82 UtlsPresets slots
/// (slot index 24 / ConfirmedAndroid2 is intentionally unmapped per sub_1412BAC30).
/// </summary>
public static class ProfileRegistry
{
    public const string DefaultFingerprint = Fingerprints.CHROME_131;
    public const string DefaultClientOptionsProfile = Fingerprints.CHROME_133;

    private static readonly Dictionary<string, ClientProfile> Mapped = BuildMappedDictionary();

    public static IReadOnlyDictionary<string, ClientProfile> MappedTlsClients { get; } =
        new ReadOnlyDictionary<string, ClientProfile>(Mapped);

    public static IReadOnlyList<ClientProfile> AllSlotProfiles { get; } = Array.AsReadOnly(new[]
    {
        UtlsPresets.Firefox_148, // slot 0 (binary #1)
        UtlsPresets.Firefox_147, // slot 1 (binary #2)
        UtlsPresets.Firefox_147_PSK, // slot 2 (binary #3)
        UtlsPresets.Firefox_146_PSK, // slot 3 (binary #4)
        UtlsPresets.Firefox_135, // slot 4 (binary #5)
        UtlsPresets.Firefox_133, // slot 5 (binary #6)
        UtlsPresets.Chrome_130_PSK, // slot 6 (binary #7)
        UtlsPresets.Chrome_131_PSK, // slot 7 (binary #8)
        UtlsPresets.Chrome_131, // slot 8 (binary #9)
        UtlsPresets.Firefox_132, // slot 9 (binary #10)
        UtlsPresets.Firefox_123, // slot 10 (binary #11)
        UtlsPresets.Firefox_120, // slot 11 (binary #12)
        UtlsPresets.ZalandoAndroidMobile, // slot 12 (binary #13)
        UtlsPresets.ZalandoIosMobile, // slot 13 (binary #14)
        UtlsPresets.NikeIosMobile, // slot 14 (binary #15)
        UtlsPresets.NikeAndroidMobile, // slot 15 (binary #16)
        UtlsPresets.CloudflareCustom, // slot 16 (binary #17)
        UtlsPresets.MMSIos, // slot 17 (binary #18)
        UtlsPresets.MeshIos, // slot 18 (binary #19)
        UtlsPresets.MeshAndroid, // slot 19 (binary #20)
        UtlsPresets.MeshIos2, // slot 20 (binary #21)
        UtlsPresets.MeshAndroid2, // slot 21 (binary #22)
        UtlsPresets.ConfirmedIos, // slot 22 (binary #23)
        UtlsPresets.ConfirmedAndroid, // slot 23 (binary #24)
        UtlsPresets.ConfirmedAndroid2, // slot 24 (binary #25)
        UtlsPresets.Okhttp4Android10, // slot 25 (binary #26)
        UtlsPresets.Okhttp4Android11, // slot 26 (binary #27)
        UtlsPresets.Okhttp4Android12, // slot 27 (binary #28)
        UtlsPresets.Okhttp4Android13, // slot 28 (binary #29)
        UtlsPresets.Okhttp4Android9, // slot 29 (binary #30)
        UtlsPresets.Okhttp4Android8, // slot 30 (binary #31)
        UtlsPresets.Okhttp4Android7, // slot 31 (binary #32)
        UtlsPresets.Chrome_152_PSK, // slot 32 (binary #33)
        UtlsPresets.Chrome_152, // slot 33 (binary #34)
        UtlsPresets.Chrome_150_PSK, // slot 34 (binary #35)
        UtlsPresets.Chrome_150, // slot 35 (binary #36)
        UtlsPresets.Chrome_146_PSK, // slot 36 (binary #37)
        UtlsPresets.Chrome_146, // slot 37 (binary #38)
        UtlsPresets.Chrome_144_PSK, // slot 38 (binary #39)
        UtlsPresets.Chrome_144, // slot 39 (binary #40)
        UtlsPresets.Chrome_133_PSK, // slot 40 (binary #41)
        UtlsPresets.Chrome_133, // slot 41 (binary #42)
        UtlsPresets.Chrome_117, // slot 42 (binary #43)
        UtlsPresets.Chrome_124, // slot 43 (binary #44)
        UtlsPresets.Chrome_120, // slot 44 (binary #45)
        UtlsPresets.Chrome_112, // slot 45 (binary #46)
        UtlsPresets.Chrome_116_PSK, // slot 46 (binary #47)
        UtlsPresets.Chrome_116_PSK_PQ, // slot 47 (binary #48)
        UtlsPresets.Chrome_111, // slot 48 (binary #49)
        UtlsPresets.Chrome_110, // slot 49 (binary #50)
        UtlsPresets.Chrome_109, // slot 50 (binary #51)
        UtlsPresets.Chrome_108, // slot 51 (binary #52)
        UtlsPresets.Chrome_107, // slot 52 (binary #53)
        UtlsPresets.Chrome_106, // slot 53 (binary #54)
        UtlsPresets.Chrome_105, // slot 54 (binary #55)
        UtlsPresets.Chrome_104, // slot 55 (binary #56)
        UtlsPresets.Chrome_103, // slot 56 (binary #57)
        UtlsPresets.Safari_15_6_1, // slot 57 (binary #58)
        UtlsPresets.Safari_16_0, // slot 58 (binary #59)
        UtlsPresets.Safari_Ipad_15_6, // slot 59 (binary #60)
        UtlsPresets.Safari_IOS_17_0, // slot 60 (binary #61)
        UtlsPresets.Safari_IOS_26_0, // slot 61 (binary #62)
        UtlsPresets.Safari_IOS_18_5, // slot 62 (binary #63)
        UtlsPresets.Safari_IOS_18_0, // slot 63 (binary #64)
        UtlsPresets.Safari_IOS_16_0, // slot 64 (binary #65)
        UtlsPresets.Safari_IOS_15_5, // slot 65 (binary #66)
        UtlsPresets.Safari_IOS_15_6, // slot 66 (binary #67)
        UtlsPresets.Firefox_117, // slot 67 (binary #68)
        UtlsPresets.Firefox_110, // slot 68 (binary #69)
        UtlsPresets.Firefox_108, // slot 69 (binary #70)
        UtlsPresets.Firefox_106, // slot 70 (binary #71)
        UtlsPresets.Firefox_105, // slot 71 (binary #72)
        UtlsPresets.Firefox_104, // slot 72 (binary #73)
        UtlsPresets.Firefox_102, // slot 73 (binary #74)
        UtlsPresets.Opera_90, // slot 74 (binary #75)
        UtlsPresets.Opera_91, // slot 75 (binary #76)
        UtlsPresets.Opera_89, // slot 76 (binary #77)
        UtlsPresets.Brave_146, // slot 77 (binary #78)
        UtlsPresets.Brave_146_PSK, // slot 78 (binary #79)
        UtlsPresets.Chrome_IOS_26_1, // slot 79 (binary #80)
        UtlsPresets.MMSIos2, // slot 80 (binary #81)
        UtlsPresets.MMSIos3, // slot 81 (binary #82)
    });

    public static IReadOnlyList<string> RegisteredKeys { get; } = Array.AsReadOnly(new[]
    {
        "firefox_148",
        "firefox_147",
        "firefox_147_PSK",
        "firefox_146_PSK",
        "firefox_135",
        "firefox_133",
        "chrome_130_PSK",
        "chrome_131_PSK",
        "chrome_131",
        "firefox_132",
        "firefox_123",
        "firefox_120",
        "zalando_android_mobile",
        "zalando_ios_mobile",
        "nike_ios_mobile",
        "nike_android_mobile",
        "cloudscraper",
        "mms_ios",
        "mms_ios_1",
        "mesh_ios",
        "mesh_ios_1",
        "mesh_android",
        "mesh_android_1",
        "mesh_ios_2",
        "mesh_android_2",
        "confirmed_ios",
        "confirmed_android",
        "okhttp4_android_10",
        "okhttp4_android_11",
        "okhttp4_android_12",
        "okhttp4_android_13",
        "okhttp4_android_9",
        "okhttp4_android_8",
        "okhttp4_android_7",
        "chrome_152_PSK",
        "chrome_152",
        "chrome_150_PSK",
        "chrome_150",
        "chrome_146_PSK",
        "chrome_146",
        "chrome_144_PSK",
        "chrome_144",
        "chrome_133_PSK",
        "chrome_133",
        "chrome_117",
        "chrome_124",
        "chrome_120",
        "chrome_112",
        "chrome_116_PSK",
        "chrome_116_PSK_PQ",
        "chrome_111",
        "chrome_110",
        "chrome_109",
        "chrome_108",
        "chrome_107",
        "chrome_106",
        "chrome_105",
        "chrome_104",
        "chrome_103",
        "safari_15_6_1",
        "safari_16_0",
        "safari_ipad_15_6",
        "safari_ios_17_0",
        "safari_ios_26_0",
        "safari_ios_18_5",
        "safari_ios_18_0",
        "safari_ios_16_0",
        "safari_ios_15_5",
        "safari_ios_15_6",
        "firefox_117",
        "firefox_110",
        "firefox_108",
        "firefox_106",
        "firefox_105",
        "firefox_104",
        "firefox_102",
        "opera_90",
        "opera_91",
        "opera_89",
        "brave_146",
        "brave_146_PSK",
        "chrome_ios_26_1",
        "mms_ios_2",
        "mms_ios_3",
    });

    public static bool TryGet(string? name, out ClientProfile? profile)
    {
        if (string.IsNullOrEmpty(name))
        {
            profile = null;
            return false;
        }

        return Mapped.TryGetValue(name, out profile);
    }

    public static ClientProfile GetOrDefault(string? name)
        => TryGet(name, out ClientProfile? profile) && profile is not null
            ? profile
            : UtlsPresets.Chrome_131;

    public static ClientProfile GetRequired(string name)
    {
        if (!TryGet(name, out ClientProfile? profile) || profile is null)
        {
            throw new UnknownProfileException(name);
        }

        return profile;
    }

    private static Dictionary<string, ClientProfile> BuildMappedDictionary()
    {
        var map = new Dictionary<string, ClientProfile>(84, StringComparer.Ordinal)
        {
            ["firefox_148"] = UtlsPresets.Firefox_148,
            ["firefox_147"] = UtlsPresets.Firefox_147,
            ["firefox_147_PSK"] = UtlsPresets.Firefox_147_PSK,
            ["firefox_146_PSK"] = UtlsPresets.Firefox_146_PSK,
            ["firefox_135"] = UtlsPresets.Firefox_135,
            ["firefox_133"] = UtlsPresets.Firefox_133,
            ["chrome_130_PSK"] = UtlsPresets.Chrome_130_PSK,
            ["chrome_131_PSK"] = UtlsPresets.Chrome_131_PSK,
            ["chrome_131"] = UtlsPresets.Chrome_131,
            ["firefox_132"] = UtlsPresets.Firefox_132,
            ["firefox_123"] = UtlsPresets.Firefox_123,
            ["firefox_120"] = UtlsPresets.Firefox_120,
            ["zalando_android_mobile"] = UtlsPresets.ZalandoAndroidMobile,
            ["zalando_ios_mobile"] = UtlsPresets.ZalandoIosMobile,
            ["nike_ios_mobile"] = UtlsPresets.NikeIosMobile,
            ["nike_android_mobile"] = UtlsPresets.NikeAndroidMobile,
            ["cloudscraper"] = UtlsPresets.CloudflareCustom,
            ["mms_ios"] = UtlsPresets.MMSIos,
            ["mms_ios_1"] = UtlsPresets.MMSIos,
            ["mesh_ios"] = UtlsPresets.MeshIos,
            ["mesh_ios_1"] = UtlsPresets.MeshIos,
            ["mesh_android"] = UtlsPresets.MeshAndroid,
            ["mesh_android_1"] = UtlsPresets.MeshAndroid,
            ["mesh_ios_2"] = UtlsPresets.MeshIos2,
            ["mesh_android_2"] = UtlsPresets.MeshAndroid2,
            ["confirmed_ios"] = UtlsPresets.ConfirmedIos,
            ["confirmed_android"] = UtlsPresets.ConfirmedAndroid,
            ["okhttp4_android_10"] = UtlsPresets.Okhttp4Android10,
            ["okhttp4_android_11"] = UtlsPresets.Okhttp4Android11,
            ["okhttp4_android_12"] = UtlsPresets.Okhttp4Android12,
            ["okhttp4_android_13"] = UtlsPresets.Okhttp4Android13,
            ["okhttp4_android_9"] = UtlsPresets.Okhttp4Android9,
            ["okhttp4_android_8"] = UtlsPresets.Okhttp4Android8,
            ["okhttp4_android_7"] = UtlsPresets.Okhttp4Android7,
            ["chrome_152_PSK"] = UtlsPresets.Chrome_152_PSK,
            ["chrome_152"] = UtlsPresets.Chrome_152,
            ["chrome_150_PSK"] = UtlsPresets.Chrome_150_PSK,
            ["chrome_150"] = UtlsPresets.Chrome_150,
            ["chrome_146_PSK"] = UtlsPresets.Chrome_146_PSK,
            ["chrome_146"] = UtlsPresets.Chrome_146,
            ["chrome_144_PSK"] = UtlsPresets.Chrome_144_PSK,
            ["chrome_144"] = UtlsPresets.Chrome_144,
            ["chrome_133_PSK"] = UtlsPresets.Chrome_133_PSK,
            ["chrome_133"] = UtlsPresets.Chrome_133,
            ["chrome_117"] = UtlsPresets.Chrome_117,
            ["chrome_124"] = UtlsPresets.Chrome_124,
            ["chrome_120"] = UtlsPresets.Chrome_120,
            ["chrome_112"] = UtlsPresets.Chrome_112,
            ["chrome_116_PSK"] = UtlsPresets.Chrome_116_PSK,
            ["chrome_116_PSK_PQ"] = UtlsPresets.Chrome_116_PSK_PQ,
            ["chrome_111"] = UtlsPresets.Chrome_111,
            ["chrome_110"] = UtlsPresets.Chrome_110,
            ["chrome_109"] = UtlsPresets.Chrome_109,
            ["chrome_108"] = UtlsPresets.Chrome_108,
            ["chrome_107"] = UtlsPresets.Chrome_107,
            ["chrome_106"] = UtlsPresets.Chrome_106,
            ["chrome_105"] = UtlsPresets.Chrome_105,
            ["chrome_104"] = UtlsPresets.Chrome_104,
            ["chrome_103"] = UtlsPresets.Chrome_103,
            ["safari_15_6_1"] = UtlsPresets.Safari_15_6_1,
            ["safari_16_0"] = UtlsPresets.Safari_16_0,
            ["safari_ipad_15_6"] = UtlsPresets.Safari_Ipad_15_6,
            ["safari_ios_17_0"] = UtlsPresets.Safari_IOS_17_0,
            ["safari_ios_26_0"] = UtlsPresets.Safari_IOS_26_0,
            ["safari_ios_18_5"] = UtlsPresets.Safari_IOS_18_5,
            ["safari_ios_18_0"] = UtlsPresets.Safari_IOS_18_0,
            ["safari_ios_16_0"] = UtlsPresets.Safari_IOS_16_0,
            ["safari_ios_15_5"] = UtlsPresets.Safari_IOS_15_5,
            ["safari_ios_15_6"] = UtlsPresets.Safari_IOS_15_6,
            ["firefox_117"] = UtlsPresets.Firefox_117,
            ["firefox_110"] = UtlsPresets.Firefox_110,
            ["firefox_108"] = UtlsPresets.Firefox_108,
            ["firefox_106"] = UtlsPresets.Firefox_106,
            ["firefox_105"] = UtlsPresets.Firefox_105,
            ["firefox_104"] = UtlsPresets.Firefox_104,
            ["firefox_102"] = UtlsPresets.Firefox_102,
            ["opera_90"] = UtlsPresets.Opera_90,
            ["opera_91"] = UtlsPresets.Opera_91,
            ["opera_89"] = UtlsPresets.Opera_89,
            ["brave_146"] = UtlsPresets.Brave_146,
            ["brave_146_PSK"] = UtlsPresets.Brave_146_PSK,
            ["chrome_ios_26_1"] = UtlsPresets.Chrome_IOS_26_1,
            ["mms_ios_2"] = UtlsPresets.MMSIos2,
            ["mms_ios_3"] = UtlsPresets.MMSIos3,
        };
        return map;
    }
}
