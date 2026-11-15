import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()
anchor = '''    {
        "name": "round 290 -- a flow step loses its ordinal",'''
new = '''    # R307: the cookie and query-param ratchets got the same per-line treatment as the endpoint one in R306; both are
    # now mutation-checked too, so all three evidence ledgers have a proven guard rather than a plausible one.
    {
        "name": "round 297 -- an unbacked cookie loses its inferred marker",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "FarfetchFlow.cs"),
        "find": 'inferred: no image evidence (R297)',
        "replace": 'no marker here',
        "test": "FullyQualifiedName~CookieEvidenceRatchetTests",
        "guard": "EachOneIsStillUsedAndStillMarked",
    },
    {
        "name": "round 298 -- an unbacked query param loses its inferred marker",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "GoatFlow.cs"),
        "find": 'inferred: no image evidence (R298)',
        "replace": 'no marker here',
        "test": "FullyQualifiedName~QueryParamEvidenceRatchetTests",
        "guard": "EachOneIsStillUsedAndMarked",
    },
''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, new, 1))
print('2 mutations added (29 total)')
