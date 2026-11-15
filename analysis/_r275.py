import io, re
p = r'D:\projects\cyber-reverse\replica\src\Cybersole.Stores\Flows\StoreFlowSteps.cs'
t = io.open(p, encoding='utf-8').read()

# 1) the record gains a Source with a safe default
old = '    public sealed record Flow(string Store, IReadOnlyList<Step> Steps)'
new = '''    /// <summary>
    /// Where a flow's step list came from — the distinction R274 found missing.
    ///
    /// <para><see cref="FlowSource.Literal"/>: read straight out of one literal in the image, so it can be checked
    /// against a recovered segment step by step. <see cref="FlowSource.Endpoint"/>: reconstructed from an endpoint
    /// family, with names that are not the image's method names (<c>StartEcomSession</c> vs <c>Start</c>) — it must not
    /// be compared to a literal segment, and calling the two together "1:1" is exactly the mistake this avoids.</para>
    /// </summary>
    public enum FlowSource
    {
        /// <summary>Read from one literal; step-by-step verifiable.</summary>
        Literal = 0,
        /// <summary>Reconstructed from endpoints; narrative, not literal names.</summary>
        Endpoint = 1,
    }

    public sealed record Flow(string Store, IReadOnlyList<Step> Steps, FlowSource Source = FlowSource.Endpoint)'''
assert old in t
t = t.replace(old, new, 1)

# 2) the two literal-derived flows say so
for store in ('structure-token-multi', 'structure-token-single'):
    pat = re.compile(r'(new\("%s", new\[\]\s*\{.*?\n    \})\);' % re.escape(store), re.S)
    m = pat.search(t)
    assert m, store
    t = t[:m.end(1)] + ', FlowSource.Literal' + t[m.end(1):]
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('FlowSource added; the two literal flows marked')
