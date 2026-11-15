import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\GoatFlow.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        c.Session.Vars["home"] = res.Body;
        AbsorbCsrf(c, res.Body);'''
new = '''        c.Session.Vars["home"] = res.Body;
        AbsorbCsrf(c, res.Body);

        // R321: the image carries a dedicated token endpoint (https://www.goat.com/web-api/get-csrf-token, found in the
        // string pool). The cookie/meta paths above are what a browser session gives; this is the fallback for when the
        // page was served without either — the flow still has to send the header on every call.
        if (string.IsNullOrEmpty(c.Session.CsrfToken))
        {
            var token = await GetAsync(c, WebApi(c, "/get-csrf-token"), "goat-csrf", ct).ConfigureAwait(false);
            if (token is { IsSuccess: true } && !string.IsNullOrWhiteSpace(token.Body))
                c.Session.CsrfToken = token.Body.Trim().Trim('"');
        }'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('goat CSRF fallback added (evidence: /web-api/get-csrf-token in the pool)')
