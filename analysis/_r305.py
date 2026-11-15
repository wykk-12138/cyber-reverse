import io
p = r'D:\projects\cyber-reverse\replica\tools\mutation-check.py'
t = io.open(p, encoding='utf-8').read()

anchor = '''    {
        "name": "round 10 -- a blank shipping preference stops being handled",'''
new = '''    # R305: the three guards added between rounds 287 and 303 were never mutation-checked. Each one below breaks the
    # thing that guard exists to catch.
    {
        "name": "round 290 -- a flow step loses its ordinal",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "StoreFlowSteps.cs"),
        "find": 'new Step("CalculateTaxes", 45)',
        "replace": 'new Step("CalculateTaxes", 44)',
        "test": "FullyQualifiedName~StoreFlowDigestTests",
        "guard": "EveryFlowMatchesItsLiteralDigest",
    },
    {
        "name": "round 294 -- an unbacked endpoint loses its inferred marker",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "GoatFlow.cs"),
        "find": 'inferred: no image evidence (R294)',
        "replace": 'not marked',
        "test": "FullyQualifiedName~EndpointEvidenceRatchetTests",
        "guard": "EveryUnbackedEndpointSaysSoInItsFile",
    },
    {
        "name": "round 292 -- an error catalogue title is rewritten",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "ErrorCatalog.cs"),
        "find": '"[General] Rate Limit"',
        "replace": '"[General] Rate limiting"',
        "test": "FullyQualifiedName~ErrorCatalogDigestTests",
        "guard": "TheCatalogueHoldsTheThirteenEntriesTheImageCarries",
    },
''' + anchor
assert anchor in t
io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(anchor, new, 1))
print('3 mutations added (now 27)')
