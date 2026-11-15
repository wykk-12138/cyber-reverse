using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Core.Store;
using Cybersole.Http;

namespace Cybersole.Services;

/// <summary>
/// Notification fan-out: in-app centre, desktop toast, sound and webhooks
/// (settings.notificationOptions + settings.webhooks).
/// </summary>
public sealed class NotificationService
{
    private readonly EventBus _bus;
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
    }

    public event EventHandler<Notification>? Shown;

    /// <summary>
    /// A notification as the fan-out hands it to the UI.
    /// </summary>
    /// <remarks>
    /// R634: the contract binds <c>Notification.Timestamp</c> and this record had only Kind/Title/Body, so the member
    /// was absent from the source entirely. The member is added here because the binding proves it exists; **what the
    /// original stores in it is Unknown** — this uses the moment the notification is raised, which matches the
    /// convention the rest of the codebase already follows (<c>EventBus.LogEntry</c> and the monitor's event both
    /// carry the time they were created).
    /// </remarks>
    public sealed record Notification(NotificationKind Kind, string Title, string Body, DateTime Timestamp);

    /// <summary>
    /// Plays a notification sound now — what the Notifications page's Play button does. It routes
    /// through the same player the fan-out uses, so the button demonstrates the real path instead
    /// of a second one that could drift.
    /// </summary>
    public void PlaySound(string? path) => _sound.Play(path);

    public NotificationOptions OptionsFor(NotificationKind kind) => kind switch
    {
        NotificationKind.Checkout => _settings.NotificationOptions.Checkout,
        NotificationKind.Decline => _settings.NotificationOptions.Decline,
        NotificationKind.Captcha => _settings.NotificationOptions.Captcha,
        NotificationKind.SmartAction => _settings.NotificationOptions.SmartAction,
        _ => _settings.NotificationOptions.Other,
    };

    public async Task PublishAsync(NotificationKind kind, string title, string body,
        CancellationToken ct = default)
    {
        // The page's "Enable Notifications" switch is settings.notifications — a master gate above
        // the five per-category "Allow ... Notifications" switches. R78 found it read by nobody.
        if (!_settings.Notifications) return;

        var opts = OptionsFor(kind);
        if (!opts.Enabled) return;

        if (opts.Centre || opts.Desktop)
            Shown?.Invoke(this, new Notification(kind, title, body, DateTime.Now));

        // R78: Sound and Path had no reader at all. The Notifications page has been offering a
        // Sounds switch, a sound file and a Play button since it was written, and nothing ever
        // played. The switch gates the sound, and an empty path means the platform default — which
        // is what the page's "Default" button shows.
        if (opts.Sound)
            _sound.Play(opts.Path);

        _bus.Log(LogLevel.Info, "Notify", $"[{kind}] {title} — {body}");

        foreach (var hook in _settings.Webhooks.Where(w => w.Enabled))
            await SendWebhookAsync(hook, kind, title, body, ct).ConfigureAwait(false);
    }

    private async Task SendWebhookAsync(Webhook hook, NotificationKind kind, string title, string body,
        CancellationToken ct)
    {
        try
        {
            var payload = Newtonsoft.Json.JsonConvert.SerializeObject(new
            {
                username = "Cybersole",
                content = $"**{title}**\n{body}\n`{kind}`",
                embeds = new[]
                {
                    new
                    {
                        title,
                        description = body,
                        color = kind == NotificationKind.Checkout ? 0x2EA043 : 0xF85149,
                        timestamp = DateTime.UtcNow.ToString("O"),
                    },
                },
            });
            await _http.PostJsonAsync(hook.Url, payload, new RequestOptions { Tag = "webhook" }, ct)
                .ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            _bus.Warn("Notify", $"webhook failed: {ex.Message}");
        }
    }
}
