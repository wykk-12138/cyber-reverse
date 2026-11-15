import io

p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\tests\Cybersole.Tests\PaymentPageTests.cs"
t = io.open(p, encoding="utf-8").read()

anchor = "    private static IEnumerable<Control> Descendants(Control root)"
add = '''    /// <summary>
    /// The dropdown prints words, not enum names. R77 caught "RoundRobin" on screen where the live
    /// page prints "Round robin".
    /// </summary>
    [Fact]
    public void ProfileAssignmentPrintsWordsNotEnumNames()
    {
        _out.WriteLine(string.Join(" | ", PaymentView.AssignmentChoices));

        Assert.Equal(new[] { "Round robin", "Random", "Least used" }, PaymentView.AssignmentChoices);
        Assert.DoesNotContain("RoundRobin", PaymentView.AssignmentChoices);
    }

'''
if anchor not in t:
    raise SystemExit("anchor missing")
if "ProfileAssignmentPrintsWordsNotEnumNames" not in t:
    t = t.replace(anchor, add + anchor, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("test added")
else:
    print("test already present")
