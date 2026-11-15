import io
p = r"D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Analytics\AnalyticsViews.cs"
t = io.open(p, encoding='utf-8').read()

# 1) one place decides the caption, with the live wording
old1 = '''        if (index == 0) _caption.Text = "Checkouts"; else _caption.Text = "Money spent";'''
new1 = '''        _caption.Text = SegmentCaption(index);'''
assert old1 in t
t = t.replace(old1, new1, 1)

old2 = '''        _caption.Text = Segments[Math.Clamp(_segment, 0, Segments.Length - 1)] == "Spend" ? "Spend" : "Checkouts";'''
new2 = '''        _caption.Text = SegmentCaption(_segment);'''
assert old2 in t
t = t.replace(old2, new2, 1)

# 2) the figure: the live window prints a currency amount on the Spend segment
old3 = '''        _number.Text = (_segment == 0 ? total : (int)Math.Round(spent)).ToString();'''
new3 = '''        _number.Text = _segment == 0 ? total.ToString() : SpendFigure(spent);'''
assert old3 in t
t = t.replace(old3, new3, 1)

anchor = '''    /// <summary>
    /// How the carousel pager reads.'''
add = '''    /// <summary>
    /// The word under the big figure. The live window says "Money Spent" — capital S — on the Spend segment (R335);
    /// the replica used to say "Spend" and, before that, "Money spent".
    /// </summary>
    public static string SegmentCaption(int index) => index == 1 ? "Money Spent" : "Checkouts";

    /// <summary>
    /// The Spend figure as the window prints it: a dollar amount, <c>$0</c> when there is nothing (R335). The
    /// multi-digit format is inferred — the empty state is the only one the running build showed.
    /// </summary>
    public static string SpendFigure(double amount) => "$" + Math.Round(amount).ToString("0");

''' + anchor
assert anchor in t
t = t.replace(anchor, add, 1)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('caption + spend figure unified')
