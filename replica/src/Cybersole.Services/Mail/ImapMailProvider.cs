using Cybersole.Core.Models;
using Cybersole.Core.Store;
using Cybersole.Http;
using Cybersole.Http.Stores;
using MailKit;
using MailKit.Net.Imap;
using MailKit.Search;
using MailKit.Security;
using MimeKit;

namespace Cybersole.Services.Mail;

public enum ImapConnectionStatus
{
    Disconnected = 0,
    Connecting = 1,
    Connected = 2,
    Error = 3,
}

/// <summary>
/// IMAP mailbox reader (<c>Cybersole.Services.ImapProvider</c>), aligning connect/IDLE cadence,
/// <c>IdentifyAsync</c>, <c>SemaphoreSlim</c> locking, and <see cref="WaitImapAsync"/> filtering
/// with the shipped MailKit/MimeKit implementation.
/// </summary>
public sealed class ImapMailProvider : IDisposable
{
    public const int DefaultPort = 993;
    public static readonly TimeSpan DisconnectedRetryDelay = TimeSpan.FromSeconds(5);
    public static readonly TimeSpan OAuthDisconnectedRetryDelay = TimeSpan.FromSeconds(300);
    public static readonly TimeSpan IdleWindowMax = TimeSpan.FromSeconds(300);
    public static readonly TimeSpan FetchDebounceDelay = TimeSpan.FromMilliseconds(150);
    public static readonly TimeSpan ErrorBackoffDelay = TimeSpan.FromMilliseconds(5000);

    private static readonly string[] OutlookOAuthHosts =
    {
        "outlook.office365.com",
        "outlook.office.com",
        "imap-mail.outlook.com",
        "imap.outlook.com",
    };

    private readonly SemaphoreSlim _gate = new(1, 1);
    private ImapClient? _client;

    public ImapMailProvider()
    {
    }

    public ImapMailProvider(string host, string username, string? password = null)
    {
        ArgumentNullException.ThrowIfNull(host);
        ArgumentNullException.ThrowIfNull(username);
        Host = host;
        Username = username;
        _ = password;
    }

    public string Host { get; private set; } = string.Empty;
    public string Username { get; private set; } = string.Empty;
    public int MessageCount { get; private set; }
    public ImapConnectionStatus Status { get; private set; } = ImapConnectionStatus.Disconnected;
    public string? LastError { get; private set; }

    public bool IsConnected => Status == ImapConnectionStatus.Connected && _client is { IsConnected: true };

    public event EventHandler<int>? CountChanged;

    public static bool IsOutlookOAuthHost(string? host) =>
        !string.IsNullOrWhiteSpace(host) &&
        OutlookOAuthHosts.Any(h => string.Equals(h, host.Trim(), StringComparison.OrdinalIgnoreCase));

    public ImapMailProvider WithAccount(ImapAccount account)
    {
        ArgumentNullException.ThrowIfNull(account);
        Host = account.Host;
        Username = account.User;
        return this;
    }

    /// <summary>Open the mailbox. Returns false and records <see cref="LastError"/> on failure.</summary>
    public async Task<bool> ConnectAsync(ImapAccount account, CancellationToken ct = default)
    {
        await _gate.WaitAsync(ct).ConfigureAwait(false);
        try
        {
            Host = account.Host;
            Username = account.User;
            Status = ImapConnectionStatus.Connecting;
            LastError = null;

            try
            {
                _client?.Dispose();
                var client = new ImapClient();
                client.Disconnected += (_, _) => Status = ImapConnectionStatus.Disconnected;
                _client = client;

                var port = account.Port > 0 ? account.Port : DefaultPort;
                var socket = account.UseSsl
                    ? SecureSocketOptions.SslOnConnect
                    : SecureSocketOptions.Auto;

                await client.ConnectAsync(account.Host, port, socket, ct).ConfigureAwait(false);
                await client.AuthenticateAsync(account.User, account.Password, ct).ConfigureAwait(false);

                try
                {
                    await client.IdentifyAsync(new ImapImplementation
                    {
                        Name = "Cybersole",
                        Version = "1.0",
                        SupportUrl = "https://cybersole.io",
                    }, ct).ConfigureAwait(false);
                }
                catch (Exception)
                {
                    // IMAP ID (RFC 2971) is optional on some servers
                }

                client.Inbox.CountChanged += (_, _) =>
                {
                    MessageCount = client.Inbox.Count;
                    CountChanged?.Invoke(this, MessageCount);
                };

                await client.Inbox.OpenAsync(FolderAccess.ReadOnly, ct).ConfigureAwait(false);
                MessageCount = client.Inbox.Count;
                account.InboxCount = MessageCount;
                Status = ImapConnectionStatus.Connected;
                return true;
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
                Status = ImapConnectionStatus.Error;
                return false;
            }
        }
        finally
        {
            _gate.Release();
        }
    }

    public async Task DisconnectAsync(CancellationToken ct = default)
    {
        if (_client is null) return;
        try
        {
            if (_client.IsConnected)
                await _client.DisconnectAsync(true, ct).ConfigureAwait(false);
        }
        catch (Exception)
        {
            // a dropped socket is already "disconnected"
        }
        finally
        {
            Status = ImapConnectionStatus.Disconnected;
        }
    }

    /// <summary>Refresh the mailbox count without re-authenticating.</summary>
    public async Task<int> RefreshCountAsync(CancellationToken ct = default)
    {
        if (!IsConnected) return MessageCount;
        try
        {
            await _client!.Inbox.StatusAsync(StatusItems.Count, ct).ConfigureAwait(false);
            MessageCount = _client.Inbox.Count;
        }
        catch (Exception ex)
        {
            LastError = ex.Message;
        }
        return MessageCount;
    }

    /// <summary>The newest <paramref name="limit"/> messages, newest first.</summary>
    public async Task<IReadOnlyList<MimeMessage>> FetchRecentAsync(int limit = 10,
        CancellationToken ct = default)
    {
        if (!IsConnected) return Array.Empty<MimeMessage>();

        var inbox = _client!.Inbox;
        var count = inbox.Count;
        if (count == 0) return Array.Empty<MimeMessage>();

        var results = new List<MimeMessage>();
        var take = Math.Min(limit, count);
        for (var i = count - 1; i >= count - take; i--)
        {
            ct.ThrowIfCancellationRequested();
            try
            {
                results.Add(await inbox.GetMessageAsync(i, ct).ConfigureAwait(false));
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
            }
        }
        return results;
    }

    /// <summary>Search the mailbox for a code matching filters/elements after <paramref name="request.Since"/>.</summary>
    public async Task<MailCodeResult> FindCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        if (!IsConnected)
        {
            if (request.Imap is null) return MailCodeResult.Fail("no imap account", "imap");
            if (!await ConnectAsync(request.Imap, ct).ConfigureAwait(false))
                return MailCodeResult.Fail(LastError ?? "connect failed", "imap");
        }

        var inbox = _client!.Inbox;
        var search = SearchQuery.All;

        if (request.Since is { } since)
            search = search.And(SearchQuery.DeliveredAfter(since.UtcDateTime));

        if (!string.IsNullOrEmpty(request.SenderContains))
            search = search.And(SearchQuery.FromContains(request.SenderContains!));

        if (!string.IsNullOrEmpty(request.SubjectContains))
            search = search.And(SearchQuery.SubjectContains(request.SubjectContains!));

        IList<UniqueId> uids;
        try
        {
            uids = await inbox.SearchAsync(search, ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return MailCodeResult.Fail($"search failed: {ex.Message}", "imap");
        }

        if (uids.Count == 0)
            uids = await inbox.SearchAsync(SearchQuery.All, ct).ConfigureAwait(false);

        var snapshots = new List<MailMessageSnapshot>();
        foreach (var uid in uids.Reverse().Take(25))
        {
            ct.ThrowIfCancellationRequested();
            try
            {
                var message = await inbox.GetMessageAsync(uid, ct).ConfigureAwait(false);
                snapshots.Add(ToSnapshot(message));
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
            }
        }

        var matched = MailMessageMatcher.EvaluateMessages(snapshots, request, "imap");
        return matched ?? MailCodeResult.Fail("no code found in mailbox", "imap");
    }

    /// <summary>Block until a code arrives or the request times out.</summary>
    public Task<MailCodeResult> WaitForCodeAsync(MailCodeRequest request, CancellationToken ct = default)
        => WaitImapAsync(request, ct);

    /// <summary>Poll/search an IMAP mailbox matching <c>0x140f40490</c> until filters + elements match.</summary>
    public async Task<MailCodeResult> WaitImapAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        var deadline = DateTimeOffset.UtcNow + request.Timeout;
        MailCodeResult last = MailCodeResult.Fail("not polled yet", "imap");
        var delay = request.PollInterval > TimeSpan.Zero ? request.PollInterval : FetchDebounceDelay;

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            last = await FindCodeAsync(request, ct).ConfigureAwait(false);
            if (last.Ok) return last;

            await Task.Delay(delay, ct).ConfigureAwait(false);
            if (IsConnected) await RefreshCountAsync(ct).ConfigureAwait(false);
        }

        return last.Ok ? last : MailCodeResult.Fail("timeout waiting for code", "imap");
    }

    public static MailMessageSnapshot ToSnapshot(MimeMessage message) => new(
        message.Subject,
        message.From.Mailboxes.Select(m => m.Address).ToArray(),
        message.To.Mailboxes.Select(m => m.Address).ToArray(),
        message.TextBody,
        message.HtmlBody,
        message.Date);

    public void Dispose()
    {
        try { _client?.Dispose(); }
        catch (Exception) { /* nothing to salvage */ }
        _client = null;
        _gate.Dispose();
        Status = ImapConnectionStatus.Disconnected;
    }
}

/// <summary>
/// Unified email-OTP orchestrator (<c>0x140f486c0</c>): races configured IMAP accounts and AYCD Inbox
/// concurrently via <see cref="Task.WhenAny{TResult}(IEnumerable{Task{TResult}})"/> and returns the first
/// matching code while cancelling sibling loops.
/// </summary>
public sealed class MailCodeService
{
    private readonly NetClient _http;
    private readonly ConfigurationStore? _config;
    private readonly EventBus? _bus;

    public MailCodeService(NetClient http) => _http = http;

    public MailCodeService(NetClient http, ConfigurationStore? config, EventBus? bus = null)
    {
        _http = http;
        _config = config;
        _bus = bus;
    }

    public async Task<(bool Ok, string? Error, int? Credits)> VerifyAycdAsync(
        string? apiKey = null,
        string? origin = null,
        CancellationToken ct = default)
    {
        var key = apiKey ?? _config?.Accounts.AycdInbox.ApiKey;
        if (string.IsNullOrWhiteSpace(key))
            return (false, "empty api key", null);

        var client = new AycdInboxClient(_http);
        return string.IsNullOrWhiteSpace(origin)
            ? await client.VerifyAsync(key!, ct).ConfigureAwait(false)
            : await client.VerifyAsync(key!, origin!, ct).ConfigureAwait(false);
    }

    public async Task<(bool Ok, int MessageCount, string? Error)> VerifyImapAsync(
        ImapAccount account,
        CancellationToken ct = default)
    {
        if (account is null || string.IsNullOrWhiteSpace(account.Host) || string.IsNullOrWhiteSpace(account.User))
            return (false, 0, "imap host and username are required");

        using var provider = new ImapMailProvider();
        var ok = await provider.ConnectAsync(account, ct).ConfigureAwait(false);
        var count = provider.MessageCount;
        var err = provider.LastError;
        await provider.DisconnectAsync(ct).ConfigureAwait(false);
        return (ok, count, err);
    }

    public async Task<MailCodeAnswer> ResolveForInquiryAsync(
        MailCodeInquiry inquiry,
        Account? account = null,
        CancellationToken ct = default)
    {
        var accounts = _config?.Accounts;
        var imapList = accounts?.Imap ?? new List<ImapAccount>();
        var aycd = accounts?.AycdInbox is { Enabled: true, ApiKey.Length: > 0 } configuredAycd
            ? configuredAycd
            : null;

        var elements = string.IsNullOrWhiteSpace(inquiry.CodeRegex)
            ? Array.Empty<MailElement>()
            : new[]
            {
                new MailElement
                {
                    Name = "code",
                    Target = MailFilterTarget.Body,
                    Type = MailElementType.Numeric,
                    Regex = inquiry.CodeRegex,
                },
            };

        var req = new MailCodeRequest
        {
            ImapAccounts = imapList,
            Aycd = aycd,
            Recipient = inquiry.Recipient ?? account?.Email,
            SenderContains = inquiry.SenderContains,
            SubjectContains = inquiry.SubjectContains,
            Elements = elements,
            Since = inquiry.Since,
            Timeout = inquiry.Timeout,
            PollInterval = TimeSpan.FromMilliseconds(20),
            AycdBaseOriginOverride = inquiry.BaseOriginOverride,
        };

        var res = await GetCodeAsync(req, ct).ConfigureAwait(false);
        if (res.Ok)
            _bus?.Info("Mail", $"code resolved via {res.Source}");
        return new MailCodeAnswer(res.Ok, res.Code, res.Source, res.Values, res.Error);
    }

    public async Task<MailCodeResult> GetCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        var imapAccounts = new List<ImapAccount>();
        if (request.Imap is not null)
            imapAccounts.Add(request.Imap);
        if (request.ImapAccounts is not null)
        {
            foreach (var acc in request.ImapAccounts)
                if (!imapAccounts.Contains(acc))
                    imapAccounts.Add(acc);
        }

        var hasAycd = request.Aycd is { Enabled: true, ApiKey.Length: > 0 };
        if (imapAccounts.Count == 0 && !hasAycd)
            return MailCodeResult.Fail("no mailbox configured", "none");

        using var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        var tasks = new List<Task<MailCodeResult>>();

        foreach (var account in imapAccounts)
        {
            var singleRequest = new MailCodeRequest
            {
                Imap = account,
                Recipient = request.Recipient,
                SenderContains = request.SenderContains,
                SubjectContains = request.SubjectContains,
                Filters = request.Filters,
                Elements = request.Elements,
                AllowMultiple = request.AllowMultiple,
                Since = request.Since,
                Timeout = request.Timeout,
                PollInterval = request.PollInterval,
            };
            tasks.Add(RunImapAsync(singleRequest, linkedCts.Token));
        }

        if (hasAycd)
            tasks.Add(RunAycdAsync(request, linkedCts.Token));

        MailCodeResult? lastFailure = null;
        while (tasks.Count > 0)
        {
            var finished = await Task.WhenAny(tasks).ConfigureAwait(false);
            tasks.Remove(finished);

            MailCodeResult result;
            try
            {
                result = await finished.ConfigureAwait(false);
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception ex)
            {
                result = MailCodeResult.Fail(ex.Message, "mail");
            }

            if (result.Ok)
            {
                linkedCts.Cancel();
                return result;
            }

            lastFailure = result;
        }

        return lastFailure ?? MailCodeResult.Fail("no mailbox configured", "none");
    }

    private static async Task<MailCodeResult> RunImapAsync(MailCodeRequest request, CancellationToken ct)
    {
        using var imap = new ImapMailProvider();
        return await imap.WaitImapAsync(request, ct).ConfigureAwait(false);
    }

    private async Task<MailCodeResult> RunAycdAsync(MailCodeRequest request, CancellationToken ct)
    {
        var client = new AycdInboxClient(_http);
        return await client.WaitForCodeAsync(request, ct).ConfigureAwait(false);
    }
}
