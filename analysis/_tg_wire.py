import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TasksViews.cs"
t = io.open(p, encoding='utf-8').read()
pairs = [
    ('UiKit.Row("Monitor delay (ms)", monitor),', 'UiKit.Row(MonitorDelayLabel, monitor),'),
    ('UiKit.Row("Retry delay (ms)", retry),', 'UiKit.Row(ErrorDelayLabel, retry),'),
    ('UiKit.Row("Error delay (ms)", error),', 'UiKit.Row("Retry Delay", error),'),
    ('UiKit.Row("Total checkout limit", checkoutLimit),', 'UiKit.Row(TotalCheckoutLimitLabel, checkoutLimit),'),
    ('UiKit.Row("Captcha source", source),', 'UiKit.Row(CaptchaSourceLabel, source),'),
    ('UiKit.Row("Cloudflare solver", solver)));', 'UiKit.Row(CloudflareSolverLabel, solver)));'),
    ('UiKit.Row("Webhook filter", filter),', 'UiKit.Row(WebhookFilterLabel, filter),'),
]
for old, new in pairs:
    assert old in t, old
    t = t.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('labels wired to the image copy')
