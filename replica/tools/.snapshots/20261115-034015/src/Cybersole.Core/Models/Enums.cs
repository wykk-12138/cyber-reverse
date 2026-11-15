namespace Cybersole.Core.Models;

/// <summary>Currency used for analytics / price display.</summary>
public enum Currency
{
    USD = 0,
    EUR = 1,
    GBP = 2,
    CAD = 3,
    AUD = 4,
    JPY = 5,
    CNY = 6,
}

/// <summary>How the task queue is presented in the UI.</summary>
public enum QueuePresentation
{
    Standard = 0,
    Compact = 1,
    Expanded = 2,
}

/// <summary>Browser window hosting mode (matches settings.json browserWindowMode).</summary>
public enum BrowserWindowMode
{
    Tab = 0,
    Window = 1,
}

public enum TaskGroupOrder
{
    Newest = 0,
    Oldest = 1,
    Name = 2,
}

public enum ProxyGroupOrder
{
    Custom = 0,
    Name = 1,
    Newest = 2,
}

public enum ProfileGroupOrder
{
    Custom = 0,
    Name = 1,
    Newest = 2,
}

public enum ProxyGroupBehaviour
{
    RoundRobin = 0,
    Random = 1,
    LeastUsed = 2,
}

/// <summary>Browser profile assignment strategy.</summary>
public enum BrowserProfileAssignment
{
    RoundRobin = 0,
    Random = 1,
    LeastUsed = 2,
}

/// <summary>Lifecycle state of a single bot task.</summary>
public enum TaskState
{
    Idle = 0,
    Starting = 1,
    Monitoring = 2,
    Waiting = 3,
    CheckingOut = 4,
    Success = 5,
    Failed = 6,
    Stopped = 7,
    Declined = 8,
}

/// <summary>Captcha provider selection for a task group (settings captchaSource).</summary>
public enum CaptchaSource
{
    None = 0,
    ReCaptcha = 1,
    HCaptcha = 2,
    Turnstile = 3,
    Geetest = 4,
    GeetestV4 = 5,
    Question = 6,
    Empty = 7,
}

/// <summary>Notification channel kinds (settings notificationOptions).</summary>
public enum NotificationKind
{
    Checkout = 0,
    Decline = 1,
    Captcha = 2,
    SmartAction = 3,
    Other = 4,
}

/// <summary>Where the app should open on start (settings startup).</summary>
public enum StartupPage
{
    Home = 0,
    Tasks = 1,
    Accounts = 2,
    Proxies = 3,
    Analytics = 4,
    Settings = 5,
}

/// <summary>Concurrency limiting strategy (settings concurrency.mode).</summary>
public enum ConcurrencyMode
{
    Unlimited = 0,
    Maximum = 1,
    Ratio = 2,
}

/// <summary>Checkout / web task result classification.</summary>
public enum CheckoutResult
{
    Unknown = 0,
    Declined = 1,
    PaymentRequired = 2,
    Success = 3,
    Cancelled = 4,
    Error = 5,

    /// <summary>The issuer asked for a 3-D Secure challenge before the payment can settle.</summary>
    ThreeDSRequired = 6,
}
