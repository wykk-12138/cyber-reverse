import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Utilities\UtilitiesViews.cs"
t = io.open(p, encoding='utf-8').read()
# the class keeps services only as a ctor parameter, so remember it
t = t.replace('''    public StoreGroupModal(AppServices services, StoreGroup? existing = null)
    {
        _editing = existing;''',
'''    private readonly AppServices _storeServices;

    public StoreGroupModal(AppServices services, StoreGroup? existing = null)
    {
        _storeServices = services;
        _editing = existing;''', 1)
t = t.replace('''        if (_editing is null) return false;
        if (!_services.Config.StoreGroups.Remove(_editing)) return false;

        _services.Config.Save();''',
'''        if (_editing is null) return false;
        if (!_storeServices.Config.StoreGroups.Remove(_editing)) return false;

        _storeServices.Config.Save();''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('services kept as a field')
