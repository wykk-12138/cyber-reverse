import io

# ---------------------------------------------------------------- CustomStoresView
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Settings\ProviderViews.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("        var addPreset = UiKit.Button(\"Add Preset\", () =>")
end = t.find("        var clear = UiKit.Button(\"Clear Presets\", () =>")
if start < 0 or end < 0 or end <= start:
    raise SystemExit("stores inline modal: %d .. %d" % (start, end))

replacement = '''        var addPreset = UiKit.Button("Add Preset", () =>
        {
            // R83: this used to be a hand-built Window here, while
            // Views/Settings/Modals/StoreCreatorView.cs already existed — two copies of one dialog.
            // The modal is the single implementation now, and it carries the live wording.
            var modal = new Modals.StoreCreatorView(services, Refresh);
            if (TopLevel.GetTopLevel(this) is Window owner) modal.ShowDialog(owner);
            else modal.Show();
        });

'''
t = t[:start] + replacement + t[end:]

# ---------------------------------------------------------------- CustomSizesView
start2 = t.find("        var addSizes = UiKit.Button(\"Add Size(s)\", () =>")
end2 = t.find("        var clearSizes = UiKit.Button(\"Clear Sizes\", () =>")
if start2 < 0 or end2 < 0 or end2 <= start2:
    raise SystemExit("sizes inline modal: %d .. %d" % (start2, end2))

replacement2 = '''        var addSizes = UiKit.Button("Add Size(s)", () =>
        {
            // R83: same story as Add Preset — SizeCreatorView already existed.
            var modal = new Modals.SizeCreatorView(services, Refresh);
            if (TopLevel.GetTopLevel(this) is Window owner) modal.ShowDialog(owner);
            else modal.Show();
        });

'''
t = t[:start2] + replacement2 + t[end2:]

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("both pages now open the shared modals")
