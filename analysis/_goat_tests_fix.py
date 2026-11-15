import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\GoatAccountSurfaceTests.cs"
t = io.open(p, encoding='utf-8').read()
old = '''        var login = src.IndexOf("/v1/login", System.StringComparison.Ordinal);
        var otp = src.IndexOf("/v1/users/send_otp_token", System.StringComparison.Ordinal);

        Assert.Contains("email", src.Substring(login, 200), System.StringComparison.Ordinal);
        Assert.Contains("password", src.Substring(login, 200), System.StringComparison.Ordinal);
        Assert.Contains("email", src.Substring(otp, 200), System.StringComparison.Ordinal);'''
new = '''        // anchor on the request tags, not on the path: the path also appears in the class comment above
        var loginTag = src.IndexOf("\\"goat-login\\"", System.StringComparison.Ordinal);
        var otpTag = src.IndexOf("\\"goat-otp\\"", System.StringComparison.Ordinal);
        Assert.True(loginTag > 300 && otpTag > 300);

        var loginBody = src.Substring(loginTag - 300, 300);
        var otpBody = src.Substring(otpTag - 300, 300);

        _out.WriteLine(loginBody.Trim());
        Assert.Contains("email", loginBody, System.StringComparison.Ordinal);
        Assert.Contains("password", loginBody, System.StringComparison.Ordinal);
        Assert.Contains("email", otpBody, System.StringComparison.Ordinal);'''
assert old in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('test anchored on the request tags')
