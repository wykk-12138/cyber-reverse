import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Modals\CommonModals.cs"
t = io.open(p, encoding='utf-8').read()
old = '''    /// <summary>
    /// What kind of message this is (bound as <c>Type</c>, R357). The image carries it beside the three label flags; the
    /// kinds are the ones a message box actually distinguishes here: plain information and a confirmation.
    /// </summary>
    public string Type { get; set; } = "Information";'''
new = '''    /// <summary>
    /// What kind of message this is (bound as <c>Type</c>, R357). Same values the constructor already took: the dialog has
    /// carried a <see cref="MessageBoxType"/> since R253, it just was not exposed under the bound name.
    /// </summary>
    public MessageBoxType Type { get; set; } = MessageBoxType.Info;'''
assert old in t
t = t.replace(old, new, 1)

# the ctor should set the member too
t = t.replace('''        Title = title;
        Width = 460;
        Height = 240;''', '''        Type = type;
        Title = title;
        Width = 460;
        Height = 240;''', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('Type is now MessageBoxType, set from the ctor')
