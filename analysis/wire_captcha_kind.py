"""R1286: record the challenge kind DetectAsync sees, using the loaders the image's own solver pages name."""

import io

P = 'D:/projects/cyber-reverse/replica/src/Cybersole.Stores/Flows/StoreFlow.cs'
text = io.open(P, encoding='utf-8').read()

old = ('            body.Contains("queue-it", StringComparison.OrdinalIgnoreCase) ? "queue-it" :\n'
       '            headers.Contains("cloudflare", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :\n'
       '            "none";\n'
       '\n'
       '        c.Session.Vars["antibot"] = vendor;\n')

new = ('            body.Contains("queue-it", StringComparison.OrdinalIgnoreCase) ? "queue-it" :\n'
       '            headers.Contains("cloudflare", StringComparison.OrdinalIgnoreCase) ? "cloudflare" :\n'
       '            "none";\n'
       '\n'
       '        // R1286: which captcha the page is asking for, from the loader it names. The image ships the solver\n'
       '        // pages themselves, so hCaptcha, Turnstile, Enterprise, v2 and v3 are each identifiable by their own\n'
       '        // script literal (CaptchaSurface carries the five, with addresses). This is separate from the wall\n'
       '        // vendor above: a Cloudflare edge can serve a Turnstile, and DataDome can sit in front of either.\n'
       '        c.Session.Vars["captcha.kind"] = CaptchaSurface.Classify(body);\n'
       '\n'
       '        c.Session.Vars["antibot"] = vendor;\n')

if old not in text:
    raise SystemExit('anchor missing')
text = text.replace(old, new)
io.open(P, 'w', encoding='utf-8', newline='\n').write(text)
print('DetectAsync now records captcha.kind')
