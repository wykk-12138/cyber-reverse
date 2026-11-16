using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using Cybersole.Core.Models;
using Cybersole.Services;

namespace Cybersole.Ui.Views;

/// <summary>
/// Billing profile editor (Cybersole.Ui.Views.Billing + ProfileAddressView).
/// </summary>
public sealed class ProfileEditorWindow : Window
{
    private readonly AppServices _services;
    private readonly TextBox _name = new() { Watermark = "Profile 1" };
    private readonly TextBox _email = new();
    private readonly TextBox _first = new();
    private readonly TextBox _last = new();
    private readonly TextBox _phone = new();
    private readonly TextBox _address1 = new();
    private readonly TextBox _address2 = new();
    private readonly TextBox _city = new();
    private readonly TextBox _state = new();
    private readonly TextBox _zip = new();
    private readonly TextBox _country = new() { Text = "US" };
    private readonly TextBox _card = new();
    private readonly TextBox _expiry = new() { Watermark = "MM/YY" };
    private readonly TextBox _cvv = new();
    private readonly TextBox _cardName = new();
    private readonly TextBlock _status = new() { Opacity = 0.8 };

    /// <summary>
    /// R69: Profile.ProxyGroupId was declared and serialised but no control ever set it, and
    /// nothing read it. The original has get_ProxyGroupId / set_ProxyGroupId next to
    /// FromPayPalAccount, so the concept exists there.
    ///
    /// A profile-level proxy group is offered here as a stored preference. The engine does not
    /// consult it yet — TaskEngine routes by task.ProxyGroupId — so choosing one records the
    /// intent without changing behaviour. Making it authoritative is a routing decision that
    /// needs evidence for precedence, which this round does not have.
    /// </summary>
    private readonly ComboBox _proxyGroup = new();

    /// <summary>The billing group this profile belongs to; null means "the first one".</summary>
    private readonly BillingGroup? _group;

    public ProfileEditorWindow(AppServices services, Profile? existing = null,
                               BillingGroup? group = null)
    {
        _services = services;
        _group = group;
        Title = existing is null ? "New profile" : $"Edit profile — {existing.Name}";
        Width = 560;
        Height = 640;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;

        if (existing is not null)
        {
            _name.Text = existing.Name;
            _email.Text = existing.Email;
            _first.Text = existing.FirstName;
            _last.Text = existing.LastName;
            _phone.Text = existing.Phone;
            _address1.Text = existing.Address1;
            _address2.Text = existing.Address2;
            _city.Text = existing.City;
            _state.Text = existing.State;
            _zip.Text = existing.Zip;
            _country.Text = existing.Country;
            _card.Text = existing.CardNumber;
            _expiry.Text = existing.CardExpiry;
            _cvv.Text = existing.CardCvv;
            _cardName.Text = existing.CardName;
        }

        var save = new Button { Content = "Save", Padding = new Thickness(16, 5) };
        save.Click += (_, _) => Submit(existing);

        var cancel = new Button { Content = "Cancel" };
        cancel.Click += (_, _) => Close();

        var grid = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("120,*"),
            RowDefinitions = new RowDefinitions(string.Join(",", Enumerable.Repeat("Auto", 16))),
        };

        void Row(int i, string label, Control input)
        {
            var l = new TextBlock { Text = label, VerticalAlignment = VerticalAlignment.Center };
            Grid.SetRow(l, i); Grid.SetColumn(l, 0);
            Grid.SetRow(input, i); Grid.SetColumn(input, 1);
            grid.Children.Add(l);
            grid.Children.Add(input);
        }

        Row(0, "Name", _name);
        Row(1, "Email", _email);
        Row(2, "First name", _first);
        Row(3, "Last name", _last);
        Row(4, "Phone", _phone);
        Row(5, "Address 1", _address1);
        Row(6, "Address 2", _address2);
        Row(7, "City", _city);
        Row(8, "State", _state);
        Row(9, "ZIP", _zip);
        Row(10, "Country", _country);
        Row(11, "Card number", _card);
        Row(12, "Expiry", _expiry);
        Row(13, "CVV", _cvv);
        Row(14, "Cardholder", _cardName);

        // index 0 is "(task proxy)" so a profile can decline to name one
        var proxyNames = new List<string> { "(task proxy)" };
        proxyNames.AddRange(_services.Config.ProxyGroups.Select(g => g.Name));
        _proxyGroup.ItemsSource = proxyNames;
        _proxyGroup.SelectedIndex = 0;
        _proxyGroup.HorizontalAlignment = HorizontalAlignment.Stretch;
        Row(15, "Proxy group", _proxyGroup);

        if (existing is not null)
        {
            var idx = _services.Config.ProxyGroups.FindIndex(g => g.Id == existing.ProxyGroupId);
            _proxyGroup.SelectedIndex = idx < 0 ? 0 : idx + 1;
        }

        var buttons = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 8,
            HorizontalAlignment = HorizontalAlignment.Right,
            Margin = new Thickness(0, 12, 0, 0),
            Children = { cancel, save },
        };

        Content = new ScrollViewer
        {
            Content = new StackPanel
            {
                Margin = new Thickness(16),
                Spacing = 6,
                Children = { grid, _status, buttons },
            },
        };
    }

    private void Submit(Profile? existing)
    {
        // Round 107: this used to be FirstOrDefault(), so a profile added while "VIP" was
        // selected landed in "Group 1" instead. The caller now passes the group the user was
        // looking at, and the fallback only applies when nobody said which.
        var group = _group ?? _services.Config.BillingGroups.FirstOrDefault();
        if (group is null)
        {
            group = new BillingGroup { Name = "Group 1" };
            _services.Config.BillingGroups.Add(group);
        }

        var profile = existing ?? new Profile();
        profile.Name = string.IsNullOrWhiteSpace(_name.Text) ? $"Profile {group.Profiles.Count + 1}" : _name.Text!.Trim();
        profile.Email = _email.Text ?? string.Empty;
        profile.FirstName = _first.Text ?? string.Empty;
        profile.LastName = _last.Text ?? string.Empty;
        profile.Phone = _phone.Text ?? string.Empty;
        profile.Address1 = _address1.Text ?? string.Empty;
        profile.Address2 = _address2.Text ?? string.Empty;
        profile.City = _city.Text ?? string.Empty;
        profile.State = _state.Text ?? string.Empty;
        profile.Zip = _zip.Text ?? string.Empty;
        profile.Country = string.IsNullOrWhiteSpace(_country.Text) ? "US" : _country.Text!.Trim();
        profile.CardNumber = _card.Text ?? string.Empty;
        profile.CardExpiry = _expiry.Text ?? string.Empty;
        profile.CardCvv = _cvv.Text ?? string.Empty;
        profile.CardName = _cardName.Text ?? string.Empty;
        profile.GroupId = group.Id;

        // R69: index 0 clears the binding; anything else stores the group's Id.
        var proxyIndex = _proxyGroup.SelectedIndex;
        profile.ProxyGroupId = proxyIndex <= 0
            ? null
            : _services.Config.ProxyGroups[Math.Min(proxyIndex - 1,
                _services.Config.ProxyGroups.Count - 1)].Id;

        if (existing is null) group.Profiles.Add(profile);

        _services.Config.Save();
        _services.Bus.Info("Billing", $"{(existing is null ? "created" : "updated")} profile {profile.Name} ({profile.Last4})");
        Close();
    }
}
