import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()

old = '''        var logOut = new Button
        {
            Content = "Log Out",'''
new = '''        // R213 kept an entry point for the signed-out case; the live panel only shows it when there is no session
        // (the signed-in panel in R337 has Dashboard / Terms / Privacy / Log Out and nothing else).
        var signIn = new Button
        {
            Content = "Sign in",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            IsVisible = user is null,
        };
        signIn.Click += (_, _) =>
        {
            var login = new Cybersole.Ui.Views.Auth.LoginControl(services);
            login.SignedIn += (_, _) => Close();
            status.Text = "Sign-in form opened.";
            if (Owner is Window host)
                _ = new Common.ViewHostModal("Login", login, 1536, 814).ShowDialog(host);
        };

        var logOut = new Button
        {
            Content = "Log Out",'''
assert old in t
t = t.replace(old, new, 1)

t = t.replace('''                dashboard,
                new Border''', '''                dashboard,
                signIn,
                new Border''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('conditional Sign-in restored')
