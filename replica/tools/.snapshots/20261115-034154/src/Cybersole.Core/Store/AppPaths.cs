using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Cybersole.Core.Models;

namespace Cybersole.Core.Store;

/// <summary>Well-known paths (mirrors %APPDATA%\Cybersole layout of the original).</summary>
public static class AppPaths
{
    public const string AppName = "Cybersole";

    /// <summary>
    /// Where this replica keeps its JSON. **Deliberately not the original's directory.**
    ///
    /// <para>
    /// R387: this used to be <c>%APPDATA%\Cybersole</c> — the same folder the real 5.18.32 writes. Two consequences, both
    /// bad: running the replica overwrote the user's live configuration, and every "does my model match the original's
    /// file?" check became circular, because the file it read may have been written by the replica itself. The default is
    /// now <c>%APPDATA%\CybersoleReplica</c>; <c>CYBERSOLE_DATA_ROOT</c> overrides it for tests.
    /// </para>
    /// </summary>
    public static string DataRoot { get; } =
        Environment.GetEnvironmentVariable("CYBERSOLE_DATA_ROOT") is { Length: > 0 } overridden
            ? overridden
            : Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppName + "Replica");

    /// <summary>The directory the real application uses — read-only evidence, never written here.</summary>
    public static string OriginalDataRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), AppName);

    /// <summary>
    /// The real application's local install/cache directory — **read only**. R405: the only reader is the version panel,
    /// which counts cached packages there; nothing in this replica writes under it. Kept separate from
    /// <see cref="DataRoot"/> so "look at the vendor's files" and "write our own" can never be the same call.
    /// </summary>
    public static string LocalRoot { get; } = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), AppName);

    /// <summary>Every path this replica writes to. A test asserts they all sit under <see cref="DataRoot"/>.</summary>
    public static IReadOnlyList<string> WritablePaths { get; } = new[]
    {
        Settings, Accounts, Tasks, Proxies, Billing, Solvers, Analytics, Sessions,
        SmartActions, SmartActionUtilities, BackupsDir, LogsDir, BrowserDataDir, ChromiumDir, TelemetryDir,
    };

    public static string Settings => Path.Combine(DataRoot, "settings.json");
    public static string Accounts => Path.Combine(DataRoot, "accounts.json");
    public static string Tasks => Path.Combine(DataRoot, "tasks.json");
    public static string Proxies => Path.Combine(DataRoot, "proxies.json");
    public static string Billing => Path.Combine(DataRoot, "billing.json");
    public static string Solvers => Path.Combine(DataRoot, "solvers.json");
    public static string Analytics => Path.Combine(DataRoot, "analytics.json");
    public static string Sessions => Path.Combine(DataRoot, "sessions.json");
    public static string SmartActions => Path.Combine(DataRoot, "smartActions.json");
    public static string SmartActionUtilities => Path.Combine(DataRoot, "smartActionUtilities.json");
    public static string BackupsDir => Path.Combine(DataRoot, "Backups");
    public static string LogsDir => Path.Combine(DataRoot, "Logs");
    public static string BrowserDataDir => Path.Combine(DataRoot, "BrowserData");
    public static string ChromiumDir => Path.Combine(DataRoot, "Chromium");
    public static string TelemetryDir => Path.Combine(DataRoot, "telemetry");

    public static void EnsureCreated()
    {
        foreach (var dir in new[] { DataRoot, BackupsDir, LogsDir })
            Directory.CreateDirectory(dir);
    }
}

/// <summary>Serialization policy shared by every on-disk document.</summary>
public static class Json
{
    public static readonly JsonSerializerSettings Default = new()
    {
        ContractResolver = new DefaultContractResolver
        {
            NamingStrategy = new CamelCaseNamingStrategy { ProcessDictionaryKeys = false },
        },
        Formatting = Formatting.Indented,
        NullValueHandling = NullValueHandling.Ignore,
        DateTimeZoneHandling = DateTimeZoneHandling.Utc,
        Converters =
        {
            new Newtonsoft.Json.Converters.StringEnumConverter(new CamelCaseNamingStrategy()),
            new TimeSpanJsonConverter(),
        },
    };

    public static string Serialize(object value) => JsonConvert.SerializeObject(value, Default);

    public static T? Deserialize<T>(string json) => JsonConvert.DeserializeObject<T>(json, Default);
}

/// <summary>TimeSpan as "HH:mm:ss" (settings uses "03:00:00" / "1.00:00:00").</summary>
public sealed class TimeSpanJsonConverter : JsonConverter<TimeSpan>
{
    public override TimeSpan ReadJson(JsonReader reader, Type objectType, TimeSpan existingValue,
        bool hasExistingValue, JsonSerializer serializer)
    {
        if (reader.TokenType == JsonToken.Null) return TimeSpan.Zero;
        var s = reader.Value?.ToString();
        return TimeSpan.TryParse(s, out var ts) ? ts : TimeSpan.Zero;
    }

    public override void WriteJson(JsonWriter writer, TimeSpan value, JsonSerializer serializer)
        => writer.WriteValue(value.ToString());
}

/// <summary>Loads / saves a single JSON document with atomic replace.</summary>
public sealed class JsonFileStore
{
    private readonly string _path;

    public JsonFileStore(string path) => _path = path;

    public bool Exists => File.Exists(_path);

    public T LoadOrDefault<T>(Func<T> factory) where T : class
    {
        try
        {
            if (!File.Exists(_path)) return factory();
            var json = File.ReadAllText(_path);
            if (string.IsNullOrWhiteSpace(json)) return factory();
            return Json.Deserialize<T>(json) ?? factory();
        }
        catch
        {
            return factory();
        }
    }

    public void Save<T>(T value) where T : class
    {
        Directory.CreateDirectory(Path.GetDirectoryName(_path)!);
        var tmp = _path + ".tmp";
        File.WriteAllText(tmp, Json.Serialize(value));

        // R438: this used to be `if (File.Exists(_path)) File.Delete(_path); File.Move(tmp, _path);` — two
        // calls with a window between them, and the Delete is the one that threw. The R438 full suite caught
        // it for real: CustomStoresRowsTests hit
        //   System.IO.IOException: tasks.json ... being used by another process
        // because something else held the file open for an instant (an indexer, an antivirus scan, another
        // writer). Two consequences, both fixed here:
        //   1. Move(overwrite: true) replaces the file in ONE call, so there is no "deleted but not yet
        //      written" window in which a crash loses the document;
        //   2. a bounded retry absorbs the transient share violation. Five attempts with growing back-off
        //      covers the scans that took the original run down; a genuinely stuck handle still throws, which
        //      is right — silently swallowing it would hide a real failure.
        for (var attempt = 0; ; attempt++)
        {
            try
            {
                File.Move(tmp, _path, overwrite: true);
                return;
            }
            catch (IOException) when (attempt < 5)
            {
                System.Threading.Thread.Sleep(20 * (attempt + 1));
            }
        }
    }
}
