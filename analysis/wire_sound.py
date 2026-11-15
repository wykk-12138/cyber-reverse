import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Services\NotificationService.cs"
t = io.open(p, encoding="utf-8").read()

old_ctor = '''    private readonly EventBus _bus;
    private readonly GlobalSettings _settings;
    private readonly NetClient _http;

    public NotificationService(EventBus bus, GlobalSettings settings, NetClient http)
    {
        _bus = bus;
        _settings = settings;
        _http = http;
    }'''
new_ctor = '''    private readonly EventBus _bus;
    private readonly GlobalSettings _settings;
    private readonly NetClient _http;
    private readonly ISoundPlayer _sound;

    public NotificationService(EventBus bus, GlobalSettings settings, NetClient http,
        ISoundPlayer? sound = null)
    {
        _bus = bus;
        _settings = settings;
        _http = http;
        _sound = sound ?? new PlatformSoundPlayer();
    }'''
if old_ctor not in t:
    raise SystemExit("ctor anchor missing")
t = t.replace(old_ctor, new_ctor, 1)

old_pub = '''        if (opts.Centre || opts.Desktop)
            Shown?.Invoke(this, new Notification(kind, title, body));'''
new_pub = '''        if (opts.Centre || opts.Desktop)
            Shown?.Invoke(this, new Notification(kind, title, body));

        // R78: Sound and Path had no reader at all. The Notifications page has been offering a
        // Sounds switch, a sound file and a Play button since it was written, and nothing ever
        // played. The switch gates the sound, and an empty path means the platform default — which
        // is what the page's "Default" button shows.
        if (opts.Sound)
            _sound.Play(opts.Path);'''
if old_pub not in t:
    raise SystemExit("publish anchor missing")
t = t.replace(old_pub, new_pub, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("NotificationService now plays the sound it was configured with")
