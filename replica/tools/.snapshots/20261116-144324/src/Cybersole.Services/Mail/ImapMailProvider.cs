using Cybersole.Core.Models;
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
/// IMAP mailbox reader (Cybersole.Services.ImapProvider).
///
/// The shipped binary links MailKit/MimeKit — the recovered symbols
/// <c>MultipartScanEpilogueAsync</c>, <c>ParseMessageAsync</c>, <c>SaslMechanism*</c>,
/// <c>ArcMessageSignature</c>, <c>UUEncoder</c> are all MailKit internals. This is the same
/// dependency doing the same job: log in, read the newest message, hand back the code.
/// </summary>
public sealed class ImapMailProvider : IDisposable
{
    private ImapClient? _client;

    public string Host { get; private set; } = string.Empty;
    public string Username { get; private set; } = string.Empty;
    public int MessageCount { get; private set; }
    public ImapConnectionStatus Status { get; private set; } = ImapConnectionStatus.Disconnected;
    public string? LastError { get; private set; }

    public bool IsConnected => Status == ImapConnectionStatus.Connected && _client is { IsConnected: true };

    public ImapMailProvider WithAccount(ImapAccount account)
    {
        Host = account.Host;
        Username = account.User;
        return this;
    }

    /// <summary>Open the mailbox. Returns false and records <see cref="LastError"/> on failure.</summary>
    public async Task<bool> ConnectAsync(ImapAccount account, CancellationToken ct = default)
    {
        Host = account.Host;
        Username = account.User;
        Status = ImapConnectionStatus.Connecting;
        LastError = null;

        try
        {
            _client?.Dispose();
            _client = new ImapClient();

            var socket = account.UseSsl
                ? SecureSocketOptions.SslOnConnect
                : SecureSocketOptions.StartTlsWhenAvailable;

            await _client.ConnectAsync(account.Host, account.Port, socket, ct).ConfigureAwait(false);
            await _client.AuthenticateAsync(account.User, account.Password, ct).ConfigureAwait(false);

            await _client.Inbox.OpenAsync(FolderAccess.ReadOnly, ct).ConfigureAwait(false);
            MessageCount = _client.Inbox.Count;
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

    /// <summary>Search the mailbox for a code that arrived after <paramref name="since"/>.</summary>
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

        // newest first, bounded so a huge mailbox does not stall the flow
        foreach (var uid in uids.Reverse().Take(25))
        {
            ct.ThrowIfCancellationRequested();
            MimeMessage message;
            try
            {
                message = await inbox.GetMessageAsync(uid, ct).ConfigureAwait(false);
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
                continue;
            }

            if (request.Recipient is { Length: > 0 } to &&
                !message.To.Mailboxes.Any(m =>
                    m.Address.Contains(to, StringComparison.OrdinalIgnoreCase)))
                continue;

            var text = (message.Subject ?? string.Empty) + "\n" + (message.TextBody
                       ?? message.HtmlBody
                       ?? string.Empty);

            var code = VerificationCodeExtractor.Extract(text);
            if (code is null) continue;

            return new MailCodeResult
            {
                Ok = true,
                Code = code,
                Subject = message.Subject,
                From = message.From.Mailboxes.FirstOrDefault()?.Address,
                Received = message.Date,
                Source = "imap",
            };
        }

        return MailCodeResult.Fail("no code found in mailbox", "imap");
    }

    /// <summary>Block until a code arrives or the request times out.</summary>
    public async Task<MailCodeResult> WaitForCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        var deadline = DateTimeOffset.UtcNow + request.Timeout;
        MailCodeResult last = MailCodeResult.Fail("not polled yet", "imap");

        while (DateTimeOffset.UtcNow < deadline)
        {
            ct.ThrowIfCancellationRequested();
            last = await FindCodeAsync(request, ct).ConfigureAwait(false);
            if (last.Ok) return last;

            await Task.Delay(request.PollInterval, ct).ConfigureAwait(false);
            if (IsConnected) await RefreshCountAsync(ct).ConfigureAwait(false);
        }

        return last.Ok ? last : MailCodeResult.Fail("timeout waiting for code", "imap");
    }

    public void Dispose()
    {
        try { _client?.Dispose(); }
        catch (Exception) { /* nothing to salvage */ }
        _client = null;
        Status = ImapConnectionStatus.Disconnected;
    }
}

/// <summary>
/// Single entry point a checkout step calls: try IMAP first, then AYCD, and report which
/// mailbox actually answered.
/// </summary>
public sealed class MailCodeService
{
    private readonly Cybersole.Http.NetClient _http;

    public MailCodeService(Cybersole.Http.NetClient http) => _http = http;

    public async Task<MailCodeResult> GetCodeAsync(MailCodeRequest request,
        CancellationToken ct = default)
    {
        if (request.Imap is not null)
        {
            using var imap = new ImapMailProvider();
            var result = await imap.WaitForCodeAsync(request, ct).ConfigureAwait(false);
            if (result.Ok) return result;
        }

        if (request.Aycd is { Enabled: true, ApiKey: not null })
        {
            var client = new AycdInboxClient(_http);
            return await client.WaitForCodeAsync(request, ct).ConfigureAwait(false);
        }

        return MailCodeResult.Fail("no mailbox configured", "none");
    }
}
