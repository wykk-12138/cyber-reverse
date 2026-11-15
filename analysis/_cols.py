import io
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Ui\Views\Tasks\TaskGrid.cs'
t = io.open(p, encoding='utf-8').read()
old = '	private const string RowColumns = "34,1.3*,2.2*,1.2*,1.2*,1.1*,90";'
new = '''	// R218: the four leading proportions are measured, not estimated. Header label left edges were read off the running
	// build at two window widths and agree exactly once normalised by the Proxies column:
	//
	//   width 1568:  Site 204  Product 384  Profile 191  Proxies 168
	//   width 1375:  Site 165  Product 311  Profile 155  Proxies 136
	//   ratio       :  1.21       2.29         1.14        1.00
	//
	// The replica had 1.3 / 2.2 / 1.2 / 1.2, i.e. Site and Proxies were both wrong by about 10%. Status stays at 1.1
	// on purpose: in an empty table the last star column absorbs the remainder, so its width measures the leftover
	// space rather than a designed proportion and cannot be inferred from these screenshots.
	private const string RowColumns = "34,1.21*,2.29*,1.14*,1.0*,1.1*,90";'''
assert old in t, 'template line'
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
print('RowColumns updated')
