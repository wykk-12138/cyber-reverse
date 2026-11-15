using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;
using Cybersole.Services.Auth;
using Cybersole.Services.Captcha;
using Cybersole.Services.Licensing;

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
    public NotificationService Notify { get; }
    public SmartActionEngine SmartActions { get; }
    public CheckoutStats Stats { get; }
    public BackupScheduler Backups { get; }

    private AppServices(ConfigurationStore config, EventBus bus, HttpAnalytics analytics,
        NetClient http, AuthService auth, LicenseService license, ClockService clock,
        ProxyTester proxyTester, CaptchaSolverService captcha, StoreRegistry stores,
        TaskEngine tasks, NotificationService notify, SmartActionEngine smartActions,
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
        Notify = notify;
        SmartActions = smartActions;
        Stats = stats;
        Backups = backups;
    }

    public static AppServices Create(Action<StoreRegistry, Cybersole.Core.Settings.GlobalSettings>? registerStores = null)
     {
        var bus = new EventBus();

        var config = new ConfigurationStore();
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
        var tasks = new TaskEngine(http, bus, stores, config.Settings, config, captcha, clock);

        // The engine raises its own event; everything downstream (Smart Actions, analytics,
        // desktop notifications, CSV history) listens on the bus. Without this bridge a real
        // checkout would never reach any of them.
        tasks.CheckoutCompleted += (_, evt) => bus.RaiseCheckout(evt);
        var notify = new NotificationService(bus, config.Settings, http);
        var smartActions = new SmartActionEngine(config, bus, notify, http);
        var backups = new BackupScheduler(config.Settings.BackupInterval, config.Backup);

        var stats = new CheckoutStats(bus,
            System.IO.Path.Combine(Cybersole.Core.Store.AppPaths.DataRoot, "checkoutHistory.json"));

        HttpDebug.Attach(analytics);
        bus.Info("App", "services initialised");

        return new AppServices(config, bus, analytics, http, auth, license, clock,
            proxyTester, captcha, stores, tasks, notify, smartActions, stats, backups);
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
