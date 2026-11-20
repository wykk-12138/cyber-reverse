using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Services.Auth;
using Cybersole.Services.Captcha;
using Cybersole.Services.Licensing;
using Cybersole.Services.Mail;

namespace Cybersole.Services;

/// <summary>
/// Composition root. Mirrors the original's dependency wiring (DI container is
/// constructed once at startup and handed to the Avalonia App).
/// </summary>
public sealed class AppServices : IDisposable
{
    public ConfigurationStore Config { get; }
    public EventBus Bus { get; }
    public HttpAnalytics Analytics { get; }
    public NetClient Http { get; }
    public AuthService Auth { get; }
    public LicenseService License { get; }
    public ClockService Clock { get; }
    public ProxyTester ProxyTester { get; }
    public CaptchaSolverService Captcha { get; }
    public StoreRegistry Stores { get; }
    public TaskEngine Tasks { get; }
    public MailCodeService Mail { get; }
    public NotificationService Notify { get; }
    public SmartActionEngine SmartActions { get; }
    public CheckoutStats Stats { get; }
    public BackupScheduler Backups { get; }

    private AppServices(ConfigurationStore config, EventBus bus, HttpAnalytics analytics,
        NetClient http, AuthService auth, LicenseService license, ClockService clock,
        ProxyTester proxyTester, CaptchaSolverService captcha, StoreRegistry stores,
        TaskEngine tasks, MailCodeService mail, NotificationService notify, SmartActionEngine smartActions,
        CheckoutStats stats, BackupScheduler backups)
    {
        Config = config;
        Bus = bus;
        Analytics = analytics;
        Http = http;
        Auth = auth;
        License = license;
        Clock = clock;
        ProxyTester = proxyTester;
        Captcha = captcha;
        Stores = stores;
        Tasks = tasks;
        Mail = mail;
        Notify = notify;
        SmartActions = smartActions;
        Stats = stats;
        Backups = backups;
    }

    public static AppServices Create(Action<StoreRegistry, Cybersole.Core.Settings.GlobalSettings>? registerStores = null,
        string? dataRoot = null)
     {
        var bus = new EventBus();

        // R1168: a caller-supplied root keeps this instance off the shared on-disk settings.
        // See ConfigurationStore(string?) for why the suite needed it.
        var config = new ConfigurationStore(dataRoot);
        config.Load();

        // settings.maxLogRetention / maxLogSize keep the in-memory log bounded
        bus.MaxRetention = config.Settings.MaxLogRetention;
        if (config.Settings.MaxLogSize > 0) bus.MaxTotalChars = config.Settings.MaxLogSize * 1024 * 1024;

        var analytics = new HttpAnalytics();
        var http = new NetClient(analytics);
        var auth = new AuthService(http, bus, config.Settings);
        var license = new LicenseService(http, bus, config.Settings, auth);
        var clock = new ClockService(bus);
        var proxyTester = new ProxyTester(bus);
        var captcha = new CaptchaSolverService(http, bus);
        var stores = new StoreRegistry();
        registerStores?.Invoke(stores, config.Settings);
        var mail = new MailCodeService(http, config, bus);
        var tasks = new TaskEngine(http, bus, stores, config.Settings, config, captcha, clock, mail);

        // The engine raises its own event; everything downstream (Smart Actions, analytics,
        // desktop notifications, CSV history) listens on the bus. Without this bridge a real
        // checkout would never reach any of them.
        tasks.CheckoutCompleted += (_, evt) => bus.RaiseCheckout(evt);
        var notify = new NotificationService(bus, config.Settings, http);
        var smartActions = new SmartActionEngine(config, bus, notify, http);
        var backups = new BackupScheduler(config.Settings.BackupInterval, config.Backup);

        var stats = new CheckoutStats(bus,
            System.IO.Path.Combine(config.Root, "checkoutHistory.json"));

        HttpDebug.Attach(analytics);
        bus.Info("App", "services initialised");

        return new AppServices(config, bus, analytics, http, auth, license, clock,
            proxyTester, captcha, stores, tasks, mail, notify, smartActions, stats, backups);
    }

    public void Dispose()
    {
        Tasks.StopAll();
        SmartActions.Dispose();
        Stats.Dispose();
        Backups.Dispose();
        Clock.Dispose();
        Http.Dispose();
        Analytics.Dispose();
    }
}
