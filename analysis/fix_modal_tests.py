import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\SettingsDialogSingleSourceTests.cs"
t = io.open(p, encoding="utf-8").read()

start = t.find("    /// <summary>The store dialog is one field and one button, as the live build shows it.</summary>")
end = t.find("    /// <summary>\n    /// The two pages no longer build a dialog of their own")
if start < 0 or end < 0:
    raise SystemExit("anchors: %d .. %d" % (start, end))

new_tests = '''    /// <summary>
    /// The store dialog is one field and one button.
    ///
    /// <para>
    /// Asserted against the source rather than a constructed control tree: these are
    /// <see cref="Window"/> subclasses, and constructing a Window needs an
    /// <c>IWindowingPlatform</c>, which a headless test run does not have. The strings are
    /// constants, so the class's shape is readable without instantiating it.
    /// </para>
    /// </summary>
    [Fact]
    public void TheStoreDialogIsOneFieldAndOneButton()
    {
        _out.WriteLine($"{StoreCreatorView.DialogTitle} / {StoreCreatorView.Prompt}");

        Assert.Equal("Add Custom Store", StoreCreatorView.DialogTitle);
        Assert.Equal("Enter store URL", StoreCreatorView.Prompt);

        var source = ModalSource("StoreCreatorView");

        Assert.Contains("UiKit.Row(Prompt, url, 130)", source);
        Assert.Contains('Content = "Add"', source);

        // the invented Name/URL pair and the generic Save/Close footer are gone
        Assert.DoesNotContain("UiKit.Row(\\"Name\\"", source);
        Assert.DoesNotContain("SaveButton(", source);
        Assert.DoesNotContain("BuildFooter(", source);
    }

    /// <summary>The size dialog keeps its four captured strings and its two inline controls.</summary>
    [Fact]
    public void TheSizeDialogCarriesTheCapturedWording()
    {
        _out.WriteLine($"{SizeCreatorView.DialogTitle} / {SizeCreatorView.Prompt} / " +
                       $"{SizeCreatorView.EmptyTitle} / {SizeCreatorView.EmptySubtitle}");

        Assert.Equal("Add Custom Sizes", SizeCreatorView.DialogTitle);
        Assert.Equal("Enter product URL", SizeCreatorView.Prompt);
        Assert.Equal("Nothing to see here", SizeCreatorView.EmptyTitle);
        Assert.Equal("Search a valid product URL", SizeCreatorView.EmptySubtitle);

        var source = ModalSource("SizeCreatorView");

        Assert.Contains('Content = "Search"', source);
        Assert.Contains("UiKit.Button(\\"Clear\\"", source);
        Assert.Contains("EmptyTitle", source);
        Assert.Contains("EmptySubtitle", source);

        // the invented size catalogue is gone
        Assert.DoesNotContain("Toggle size selected", source);
        Assert.DoesNotContain("SaveButton(", source);
        Assert.DoesNotContain("BuildFooter(", source);
    }

    /// <summary>
    /// The store dialog is the only writer of a new preset: it parses the URL, derives the name
    /// from the host, and calls back so the page refreshes.
    /// </summary>
    [Fact]
    public void TheStoreDialogWritesThroughToSettings()
    {
        var source = ModalSource("StoreCreatorView");

        Assert.Contains("settings.CustomStores ??= new List<CustomStore>()", source);
        Assert.Contains("Name = uri.Host.Replace(\\"www.\\", string.Empty", source);
        Assert.Contains("onAdded?.Invoke();", source);
        Assert.Contains("services.Config.Save();", source);
    }

'''
t = t[:start] + new_tests + t[end:]

# A helper that returns one modal class's source.
helper_anchor = "    private static string RepoRoot()"
helper = '''    /// <summary>One dialog class's source text, so its shape can be asserted without a window.</summary>
    private static string ModalSource(string className)
    {
        var path = Path.Combine(RepoRoot(), "src", "Cybersole.Ui", "Views", "Settings", "Modals",
            "SettingsModals.cs");
        var text = File.ReadAllText(path);

        var start = text.IndexOf("class " + className, StringComparison.Ordinal);
        Assert.True(start > 0, className + " not found");

        // the class ends at the next top-level class doc comment
        var next = text.IndexOf("\\npublic sealed class ", start, StringComparison.Ordinal);
        return next > start ? text[start..next] : text[start..];
    }

'''
if helper_anchor not in t:
    raise SystemExit("helper anchor missing")
t = t.replace(helper_anchor, helper + helper_anchor, 1)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("tests rewritten to source-level assertions")
