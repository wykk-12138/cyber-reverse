import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
lines = io.open(p, encoding='utf-8').read().split('\n')
start = next(i for i, l in enumerate(lines) if 'public UserView(AppServices services)' in l)
print('ctor at line', start + 1, '| total', len(lines))
print('last lines:', [l.rstrip() for l in lines[-4:]])
# keep everything before the ctor
head = lines[:start]
new = r'''    public UserView(AppServices services)
    {
        _services = services;
        Title = "Account";
        Width = 460;
        Height = 340;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        var user = services.Auth.Claims;
        var status = UiKit.Status();

        // R337: laid out from the running build's profile panel:
        //   •  My License / [avatar] / name / email / [Dashboard ↗]
        //   ---------------------------------------------
        //   Terms of Service  •  Privacy Policy           [Log Out]
        var header = new TextBlock { Text = "\u2022  My License", FontSize = 12, Opacity = 0.8 };

        var avatar = new Border
        {
            Width = 64,
            Height = 64,
            CornerRadius = new CornerRadius(32),
            Background = Brushes.DimGray,
            HorizontalAlignment = HorizontalAlignment.Center,
            Child = new TextBlock
            {
                Text = "\u263A",
                FontSize = 28,
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
            },
        };

        var name = new TextBlock
        {
            Text = user?.DisplayName ?? user?.Email ?? "(signed out)",
            FontSize = 18,
            FontWeight = FontWeight.SemiBold,
            HorizontalAlignment = HorizontalAlignment.Center,
        };

        var email = new TextBlock
        {
            Text = user?.Email ?? string.Empty,
            FontSize = 11,
            Opacity = 0.6,
            HorizontalAlignment = HorizontalAlignment.Center,
        };

        var dashboard = new Button
        {
            Content = "Dashboard \u2197",
            HorizontalAlignment = HorizontalAlignment.Stretch,
            HorizontalContentAlignment = HorizontalAlignment.Center,
            Command = new RelayCommand(() => status.Text = "Opening " + DashboardUrl),
        };

        var terms = new Button { Content = "Terms of Service", Background = Brushes.Transparent, Padding = new Thickness(2, 0) };
        terms.Click += (_, _) => status.Text = "Opening " + TermsUrl;

        var privacy = new Button { Content = "Privacy Policy", Background = Brushes.Transparent, Padding = new Thickness(2, 0) };
        privacy.Click += (_, _) => status.Text = "Opening " + PrivacyUrl;

        var logOut = new Button
        {
            Content = "Log Out",
            Background = Brushes.Crimson,
            Foreground = Brushes.White,
            Padding = new Thickness(10, 4),
            HorizontalAlignment = HorizontalAlignment.Right,
        };
        logOut.Click += (_, _) => LogOut();

        var footerLeft = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 6,
            VerticalAlignment = VerticalAlignment.Center,
            Children = { terms, new TextBlock { Text = "\u2022", Opacity = 0.6 }, privacy },
        };

        var footer = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        footer.Children.Add(footerLeft);
        Grid.SetColumn(logOut, 1);
        footer.Children.Add(logOut);

        Content = new StackPanel
        {
            Margin = new Thickness(16),
            Spacing = 10,
            Children =
            {
                header,
                avatar,
                name,
                email,
                dashboard,
                new Border { Height = 1, Background = Brushes.DimGray, Margin = new Thickness(0, 4) },
                footer,
                status,
            },
        };
    }
}
'''
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(head) + new)
print('UserView rewritten')
