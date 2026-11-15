import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\OriginalViewClassParityTests.cs"
t = io.open(p, encoding="utf-8").read()

# The replica's profile editor is ProfileCreatorView, not a class called ProfileEditorView.
t = t.replace('["ProfileAddressView"] = "ProfileEditorView",',
              '["ProfileAddressView"] = "ProfileCreatorView",', 1)
t = t.replace('["ProfileAdvancedView"] = "ProfileEditorView",',
              '["ProfileAdvancedView"] = "ProfileCreatorView",', 1)
t = t.replace('["ProfilePaymentView"] = "ProfileEditorView",',
              '["ProfilePaymentView"] = "ProfileCreatorView",', 1)

# SmartActionSettings is renamed, not unbudgeted — having it in both lists double-counted it.
t = t.replace('        "SmartActionSettings",      // see Renamed: present as SmartActionSettingsView\n', "")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("renames corrected")
