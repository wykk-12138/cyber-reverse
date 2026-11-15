import io
p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LoginControlTests.cs"
t = io.open(p, encoding='utf-8').read()
idx = t.rindex('}')
add = '''
    /// <summary>
    /// R343: the five operations the binding table binds on this control exist as methods, not as inline lambdas.
    ///
    /// <para>
    /// <c>Cybersole.Ui.Views.Auth.LoginControl</c> binds Cancel, OpenBrowser, SignIn, SignUp and UseCode. The replica did
    /// all of it inside click handlers, which is the same behaviour with nothing to bind to — the same correction R239
    /// made on NotificationsView. SignIn is async because it exchanges the code with the auth service, so it is checked
    /// by name here and exercised through the code form.
    /// </para>
    /// </summary>
    [Fact]
    public void TheFiveBoundOperationsExistAsMembers()
    {
        var type = typeof(Cybersole.Ui.Views.Auth.LoginControl);
        var names = type.GetMethods().Select(m => m.Name).ToList();

        foreach (var bound in new[] { "Cancel", "OpenBrowser", "SignUp", "UseCode" })
            Assert.Contains(bound, names);

        Assert.Contains("SignInAsync", names);
        Assert.Equal(typeof(System.Threading.Tasks.Task<bool>), type.GetMethod("SignInAsync")!.ReturnType);
    }
'''
t = t[:idx] + add + '}\n'
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('LoginControl member test appended')
