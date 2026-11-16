using System.Collections.Generic;

namespace Cybersole.Core.Webhooks;

/// <summary>
/// What a webhook has to be able to do (IWebhook, R342).
///
/// <para>
/// The binding table carries six members on <c>Cybersole.Webhook.IWebhook</c>: Enabled, Events, ExtraFields, Name, Type
/// and Url. The replica had only ExtraFields, so the interface now states the whole contract and the concrete model
/// satisfies it. Where the extra fields are edited is still unknown (R341); where they are stored is not.
/// </para>
/// </summary>
public interface IWebhook
{
    /// <summary>The name shown in the list (bound as <c>Name</c>).</summary>
    string? Name { get; }

    /// <summary>Where the payload is posted (bound as <c>Url</c>).</summary>
    string Url { get; }

    /// <summary>Whether the hook fires at all (bound as <c>Enabled</c>).</summary>
    bool Enabled { get; }

    /// <summary>The platform the payload is shaped for (bound as <c>Type</c>).</summary>
    string Type { get; }

    /// <summary>Which notifications fire it (bound as <c>Events</c>).</summary>
    IReadOnlyList<string> Events { get; }

    /// <summary>Extra key/value pairs sent with every post (bound as <c>ExtraFields</c>).</summary>
    Dictionary<string, string> ExtraFields { get; }
}
