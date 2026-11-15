import io

# --- proxies -----------------------------------------------------------------
p = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Proxies\ProxyGrid.cs"
t = io.open(p, encoding="utf-8").read()
old = 'private const string RowColumns = "34,1.6*,0.9*,1.5*,1.2*,Auto";'
new = '''/// <summary>
    /// One column template for the header and every row.
    ///
    /// <para>
    /// R72: the last column used to be <c>Auto</c>, which sized itself to the toolbar in the header
    /// and to nothing in the rows — so the header said IP/Port/Username/Status at one set of x
    /// positions and the cells landed at another. A screenshot showed it. The two grids have to
    /// reserve the same fixed width.
    /// </para>
    /// </summary>
    private const string RowColumns = "34,1.6*,0.9*,1.5*,1.2*," + ActionsWidth;

    /// <summary>Width reserved for the header's buttons, in every row as well.</summary>
    internal const string ActionsWidth = "300";'''
if old not in t:
    raise SystemExit("proxy anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("proxies columns fixed")

# --- accounts ----------------------------------------------------------------
p2 = r"C:\Users\wykk\AppData\Local\Cybersole\replica\src\Cybersole.Ui\Views\Accounts\AccountGrid.cs"
t2 = io.open(p2, encoding="utf-8").read()
old2 = 'private const string RowColumns = "34,2*,1.4*,1.3*,88,Auto";'
new2 = '''/// <summary>
    /// One column template for the header and every row.
    ///
    /// <para>
    /// R71/R72: the last column was <c>Auto</c>, which sized itself to the toolbar in the header and
    /// to nothing in the rows — so the header's Email/Password/Added sat at different x positions
    /// than the cells under them. A screenshot showed it. The reserved width has to be fixed.
    /// </para>
    /// </summary>
    private const string RowColumns = "34,2*,1.4*,1.3*,88," + ActionsWidth;

    /// <summary>Width reserved for the header's buttons, in every row as well.</summary>
    internal const string ActionsWidth = "200";'''
if old2 not in t2:
    raise SystemExit("accounts anchor missing")
io.open(p2, "w", encoding="utf-8", newline="").write(t2.replace(old2, new2, 1))
print("accounts columns fixed")
