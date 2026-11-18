"""Mutation check: break each fix on purpose and confirm its guard fails.

A test that has never failed is not evidence. This walks three fixes from rounds 136-138, undoes
each one the way it was before, runs the guard that is supposed to catch it, and restores. If a
guard stays green while the defect is back, the guard is decorative.

Every mutation runs inside try/finally so the file is restored even when the test run throws.
"""
import io
import os
import re
import subprocess
import sys

# R127: the repo moved to D:. Resolve it from this file's own location so a future move is a no-op.
REPO = str(__import__("pathlib").Path(__file__).resolve().parent.parent)
DOTNET = r"D:\tools\dotnet8\dotnet.exe"
BRIDGE = os.path.join(REPO, "src", "Cybersole.Stores", "Scripts", "ChromiumBridge.cs")
ANALYTICS = os.path.join(REPO, "src", "Cybersole.Http", "HttpAnalytics.cs")
CORE_CSPROJ = os.path.join(REPO, "src", "Cybersole.Core", "Cybersole.Core.csproj")
SETTINGS_VIEWS = os.path.join(REPO, "src", "Cybersole.Ui", "Views", "Settings", "SettingsViews.cs")
PROVIDER_VIEWS = os.path.join(REPO, "src", "Cybersole.Ui", "Views", "Settings", "ProviderViews.cs")
SOLVER_WINDOW = os.path.join(REPO, "src", "Cybersole.Ui", "Views", "SolverWindow.cs")
SPOOF_JS = os.path.join(REPO, "src", "Cybersole.Core", "Engine", "Cybersole.Engine.hcaptcha-spoof.js")
GEETEST_HTML = os.path.join(REPO, "src", "Cybersole.Core", "Engine", "Cybersole.Engine.Geetest.html")
CAPTCHA_HTML = os.path.join(REPO, "src", "Cybersole.Core", "Engine", "Cybersole.Engine.Captcha.html")
PARITY_DOC = os.path.join(REPO, "docs", "PARITY.md")
EN_LOCALE = os.path.join(REPO, "src", "Cybersole.Core", "Locales", "Cybersole.Locales.en.json")
SETTINGS_SHELL = os.path.join(REPO, "src", "Cybersole.Ui", "Views", "Settings", "SettingsShell.cs")
TASKS_VIEWS = os.path.join(REPO, "src", "Cybersole.Ui", "Views", "Tasks", "TasksViews.cs")
SHOPIFY_FLOW = os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "ShopifyFlow.cs")
SHAPE_AUDIT = os.path.join(REPO, "tools", "shape_audit.py")
BIND_DIFF = os.path.join(REPO, "tools", "bind_diff.py")
BIND_SCOPE = os.path.join(REPO, "tools", "bind_scope.py")
# R605: the metric-claims document sits in the REPOSITORY docs dir, not replica/docs
METRIC_CLAIMS = os.path.join(os.path.dirname(REPO), "docs", "METRIC_CLAIMS.md")
BLOCKERS_DOC = os.path.join(os.path.dirname(REPO), "docs", "BLOCKERS.md")
TRIAGE_SCRIPT = os.path.join(os.path.dirname(REPO), "analysis", "type_presence_triage.py")
COPY_AUDIT = os.path.join(REPO, "tools", "copy_audit_report.py")
# R1076-R1078: the three rounds that landed decompiled checkout/3DS behaviour. Their guards are new, so each
# gets a mutation of its own -- a guard that has never been killed is not evidence (the harness's own rule).
NIKE_FLOW = os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "NikeFlow.cs")
PAYPAL_3DS = os.path.join(REPO, "src", "Cybersole.Stores", "Payments", "PayPalThreeDs.cs")
FARFETCH_FLOW = os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "FarfetchFlow.cs")

MUTATIONS = [
    {
        "name": "round 136 — the contentWindow replay route",
        "file": BRIDGE,
        "find": "            const descriptor = Object.getOwnPropertyDescriptor(proto, 'contentWindow');",
        # the getter route reads a frame that already exists; dropping it leaves that path open
        "replace": "            const descriptor = null;",
        "test": "FullyQualifiedName~RealmReplayTests",
        "guard": "BothIframeRoutesAreHooked",
    },
    {
        "name": "round 136 — the createElement replay route",
        "file": BRIDGE,
        "find": "            const createElement = Document.prototype.createElement;",
        "replace": "            const createElement = null;",
        "test": "FullyQualifiedName~RealmReplayTests",
        "guard": "BothIframeRoutesAreHooked",
    },
    {
        "name": "round 136 — replay a fresh realm through a bare global",
        "file": BRIDGE,
        "find": "              Object.defineProperty(N, 'webdriver', { get: () => undefined, configurable: true });",
        # the pre-round-136 shape: patch the current realm, not the one passed in
        "replace": "              Object.defineProperty(navigator, 'webdriver', { get: () => undefined, configurable: true });",
        "test": "FullyQualifiedName~RealmReplayTests",
        "guard": "NoPatchReadsABareNavigatorOrWindow",
    },
    {
        "name": "round 137 — speechSynthesis voices",
        "file": BRIDGE,
        "find": "                value: function getVoices() { return voices.slice(); },",
        "replace": "                value: function getVoices() { return []; },",
        "test": "FullyQualifiedName~RealmReplayTests",
        "guard": "SpeechSynthesisReturnsAVoiceList",
    },
    {
        "name": "round 138 — one version reading",
        "file": BRIDGE,
        "find": "        var fullVersion = ChromiumBridgeVersion();          // 157.0.8103.38",
        "replace": '        var fullVersion = "131.0.0.0";                      // MUTATED',
        "test": "FullyQualifiedName~UserAgentConsistencyTests",
        "guard": "UserAgentDataComesFromTheSameReading",
    },
    {
        "name": "round 127 -- Flush dequeues before it checks for a sink",
        "file": ANALYTICS,
        "find": "        if (SinkUrl is null) return;     // nothing to do on the request side, and nothing to lose\n",
        # the pre-round-127 body: an empty loop that discards events it cannot deliver
        "replace": ("        if (SinkUrl is null) { while (_requests.TryDequeue(out _)) { } return; }\n"
                    "        if (SinkUrl is null) return;     // nothing to do, and nothing to lose\n"),
        "test": "FullyQualifiedName~HttpAnalyticsFlushTests",
        "guard": "Flush_WithNoSink_KeepsEveryEvent",
    },
    {
        "name": "round 133 -- a locale dictionary loses its WithCulture=false",
        "file": CORE_CSPROJ,
        "find": 'LogicalName="Cybersole.Locales.ja.json" WithCulture="false"',
        # without this the payload becomes a satellite assembly under ja/ and the main
        # assembly cannot find it
        "replace": 'LogicalName="Cybersole.Locales.ja.json"',
        "test": "FullyQualifiedName~LocaleDictionaryTests",
        "guard": "AllFourResourcesAreEmbedded",
    },
    {
        "name": "round 124 -- a catch message overwritten by the next line",
        "file": SETTINGS_VIEWS,
        "find": "            status.Text = \"Saved.\";",
        # write the status unconditionally before the success line, which is the shape the
        # StatusOverwriteTests guard was written for
        "replace": ("            status.Text = \"Saved.\";\n"
                    "            try { throw new InvalidOperationException(\"x\"); }\n"
                    "            catch (Exception ex) { status.Text = \"failed: \" + ex.Message; }\n"
                    "            status.Text = \"Saved.\";"),
        "test": "FullyQualifiedName~StatusOverwriteTests",
        "guard": "NoStatusWriteImmediatelyFollowsItsOwnCatch",
    },
    {
        "name": "round 124 -- a brand new dead button",
        "file": TASKS_VIEWS,
        "find": "    private void Status(string text) => _status.Text = text;",
        # the shape DeadButtonTests exists for: a button whose handler only writes status text.
        # TasksViews has both _status and Status(string), so this compiles and the guard is the
        # only thing that can reject it.
        "replace": ("    private void Status(string text) => _status.Text = text;\n"
                    '    private void Probe() { var dead = UiKit.Button("Export settings", () => Status("later")); }'),
        "test": "FullyQualifiedName~DeadButtonTests",
        "guard": "NoNewStatusOnlyButtons",
    },
    {
        "name": "round 122 -- a cross-layer await loses its ConfigureAwait",
        "file": SOLVER_WINDOW,
        "find": "}).ConfigureAwait(true);",
        # The real shape: SolverWindow awaits _services.Captcha.SolveAsync and pins the
        # continuation. Drop the pin and UiContinuationTests has something to reject — and unlike
        # an injected await of a void method, this compiles.
        "replace": "});",
        "test": "FullyQualifiedName~UiContinuationTests",
        "guard": "UiAwaitsPinTheirContinuation",
    },
    {
        "name": "round 112 -- a mojibake sequence written into a comment",
        "file": PROVIDER_VIEWS,
        "find": "namespace Cybersole.Ui.Views.Settings;",
        # U+9225 followed by '?' -- the exact pair a UTF-8 file read as GBK leaves behind
        "replace": ("namespace Cybersole.Ui.Views.Settings;\n"
                    "// \u9225? probe"),
        "test": "FullyQualifiedName~SourceEncodingTests",
        "guard": "NoSourceFileContainsMojibake",
    },
    {
        "name": "round 124 -- a throwaway settings object beside Config.Save",
        "file": SOLVER_WINDOW,
        "find": "public sealed class SolverWindow : Window\n{",
        "replace": ("public sealed class SolverWindow : Window\n{\n"
                    "    private readonly SolverSettings _throwaway = new();"),
        "test": "FullyQualifiedName~StatusOverwriteTests",
        "guard": "NoUiFieldHoldsAThrowawaySettingsObjectWhileSaving",
    },
    {
        "name": "round 134 -- an engine asset stops being embedded",
        "file": CORE_CSPROJ,
        "find": '<EmbeddedResource Include="Engine\Cybersole.Engine.Popmart.html" LogicalName="Cybersole.Engine.Popmart.html" />',
        "replace": '<!-- asset removed -->',
        "test": "FullyQualifiedName~EngineAssetsTests",
        "guard": "AllFourteenAreEmbedded",
    },
    {
        "name": "round 135 -- the screen table stops agreeing with the geometry table",
        "file": SPOOF_JS,
        "find": 'const SCREEN = {"width": 402, "height": 874, "availWidth": 402,',
        # ScreenAndGeometryAgree exists for exactly this: two tables that are each plausible but
        # contradict each other, which is the easiest inconsistency for a detector to spot
        "replace": 'const SCREEN = {"width": 390, "height": 874, "availWidth": 390,',
        "test": "FullyQualifiedName~DeviceTableTests",
        "guard": "ScreenAndGeometryAgree",
    },
    {
        "name": "round 135 -- a device table loses its declaration",
        "file": SPOOF_JS,
        "find": 'const INTL = {"locale": "nl-NL"',
        # AllDeviceTablesArePresent counts const NAME = declarations, so renaming one is the
        # mutation that targets it. The first attempt edited getVoices instead, which that guard
        # does not look at — the guard was right, the mutation was aimed at the wrong thing.
        "replace": 'const INTL_X = {"locale": "nl-NL"',
        "test": "FullyQualifiedName~DeviceTableTests",
        "guard": "AllDeviceTablesArePresent",
    },
    {
        "name": "round 134 -- geetest page loads the v4 script",
        "file": GEETEST_HTML,
        "find": "https://static.geetest.com/static/tools/gt.js",
        # GeetestV4UsesTheV4ScriptAndGeetestDoesNot asserts gt4.js is only in the v4 page
        "replace": "https://static.geetest.com/v4/gt4.js",
        "test": "FullyQualifiedName~EngineAssetsTests",
        "guard": "GeetestV4UsesTheV4ScriptAndGeetestDoesNot",
    },
    {
        "name": "round 134 -- the recaptcha page stops loading recaptcha",
        "file": CAPTCHA_HTML,
        "find": "g-recaptcha",
        # the page must no longer name the vendor at all; g-recaptcha-disabled still contains
        # g-recaptcha, and Contains() duly matched it — the guard was right, the mutation was
        # too gentle to be a mutation.
        "replace": "captcha-slot",
        # the page names the vendor ten times; replacing only the first left nine behind, so
        # Contains() still matched and the guard looked decorative. It was not — the mutation was
        # one-tenth applied.
        "all": True,
        "test": "FullyQualifiedName~EngineAssetsTests",
        "guard": "EachPageLoadsTheVendorItsNameClaims",
    },
    {
        "name": "round 164 -- PARITY.md's module count drifts",
        "file": PARITY_DOC,
        # the table said 50 for eleven rounds after the catalogue reached 61. ParityDocTests reads
        # the number out of the document and compares it to CreateAll().Count, so a hand-edit that
        # forgets to recount now fails here.
        #
        # R980: this row had been SKIPPED because its literal anchor carried the number itself ("**62 个注册模块") and
        # the catalogue has since reached 65. Re-anchoring the literal to 65 would repeat round 164's own history a third
        # time, so the anchor is a pattern: it matches whatever count the line currently shows and prefixes a 9, which
        # makes the document's figure disagree with CreateAll().Count no matter what that count becomes.
        "find_re": r"(\*\*)(\d+)( 个注册模块)",
        "replace_re": r"\g<1>9\g<2>\g<3>",
        "test": "FullyQualifiedName~ParityDocTests",
        "guard": "TheModuleCountInParityMatchesTheCatalogue",
    },
    {
        "name": "round 164 -- PARITY.md's UI count drifts",
        "file": PARITY_DOC,
        # R71: the counts in this line move whenever a view is added or removed, so the anchor is
        # the stable prefix only. Anchoring on "**71 个 UI 类：24 个" made the guard silently skip
        # the round the page was split into four views — the exact failure it exists to catch.
        # R435: re-anchored a second time. R423 added MonitorView, so the live figure became 85 and this
        # row was *skipping* — the R435 full pass printed "SKIPPED — anchor not found", which is how it
        # was found. The mutation now walks the number backwards to the previous value.
        "find": "**85 个 UI 类：26 个",
        "replace": "**84 个 UI 类：26 个",
        "test": "FullyQualifiedName~ParityDocTests",
        "guard": "TheUiClassCountsInParityMatchTheSource",
    },
    {
        "name": "round 168 -- a locale dictionary repeats a key",
        "file": EN_LOCALE,
        "find": "  \"Solver.AllCaptchas\": \"All Captchas\",",
        # R168 found en and ja each held 1143 properties: this exact line appeared twice. The
        # value was identical so nothing broke, and a Dictionary-based check would have collapsed
        # the duplicate. EveryLocaleDictionaryHasTheSameKeyCount enumerates properties and groups.
        "replace": ("  \"Solver.AllCaptchas\": \"All Captchas\",\n"
                    "  \"Solver.AllCaptchas\": \"All Captchas\","),
        "test": "FullyQualifiedName~EveryLocaleDictionaryHasTheSameKeyCount",
        "guard": "EveryLocaleDictionaryHasTheSameKeyCount",
    },
    {
        "name": "round 169 -- a locale dictionary loses a key",
        "file": EN_LOCALE,
        "find": "  \"Solver.AllCaptchas\": \"All Captchas\",",
        # The complement of the duplicate case. A duplicate leaves every Dictionary.Count
        # unchanged, so LocaleDictionaryTests stays green and only the property-count test sees
        # it. A deletion is the reverse: Dictionary.Count drops, ExpectedKeys fails, and
        # EveryDictionaryCoversTheSameKeys reports the key missing from the other three.
        # Two mutations, because the two tests catch different things.
        "replace": "",
        "test": "FullyQualifiedName~LocaleDictionaryTests",
        "guard": "EveryDictionaryHasTheSameKeyCount",
    },
    {
        "name": "round 179 -- an event is declared, raised, and never subscribed",
        "file": SETTINGS_SHELL,
        "find": "    public string CurrentSection => _current;",
        # R118 left UpdateRequested behind after fixing the button. UnsubscribedEventsTests
        # reports any event that is raised with no `+=` anywhere in src/; this restores exactly
        # that shape, one event, raised once.
        "replace": ("    public string CurrentSection => _current;\n"
                    "    public event EventHandler? ProbeEvent;\n"
                    "    private void ProbeRaise() => ProbeEvent?.Invoke(this, EventArgs.Empty);"),
        "test": "FullyQualifiedName~UnsubscribedEventsTests",
        "guard": "NoEventIsDeclaredRaisedAndNeverListenedTo",
    },
    {
        "name": "round 187 -- a Cloudflare provider is added to only one of the two lists",
        "file": PROVIDER_VIEWS,
        "find": 'Type = "cfsolver",',
        # R113's defect in a new place: the page writes settings.CloudflareSolvers, the task-group
        # dropdown reads Captcha.Registry.Configs, and a provider added here was invisible where it
        # gets chosen.
        #
        # The first attempt commented out the whole AddConfig call, which left an unpaired brace
        # and reported DID NOT COMPILE. Deleting this line instead keeps the code compiling and
        # still removes the connection: the config lands in the registry typed humanpresence, so
        # no driver claims it. It also proved the string-only assertion too weak — the call was
        # still present, so the test stayed green until it started checking the Type.
        "replace": "",
        "test": "FullyQualifiedName~SettingsStorageLinkTests",
        "guard": "AddingACloudflareProviderAlsoRegistersItAsACaptchaProvider",
    },
    # R305: the three guards added between rounds 287 and 303 were never mutation-checked. Each one below breaks the
    # thing that guard exists to catch.
    # R307: the cookie and query-param ratchets got the same per-line treatment as the endpoint one in R306; both are
    # now mutation-checked too, so all three evidence ledgers have a proven guard rather than a plausible one.
    {
        "name": "round 297 -- an unbacked cookie loses its inferred marker",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "FarfetchFlow.cs"),
        "find": 'inferred: no image evidence (R297)',
        "replace": 'no marker here', "all": True,
        "test": "FullyQualifiedName~CookieEvidenceRatchetTests",
        "guard": "EachOneIsStillUsedAndStillMarked",
    },
    {
        "name": "round 298 -- an unbacked query param loses its inferred marker",
        "file": os.path.join(REPO, "src", "Cybersole.Stores", "Flows", "GoatFlow.cs"),
        "find": 'inferred: no image evidence (R298)',
        "replace": 'no marker here', "all": True,
        "test": "FullyQualifiedName~QueryParamEvidenceRatchetTests",
        "guard": "EachOneIsStillUsedAndMarked",
    },
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
    {
        "name": "round 10 -- a blank shipping preference stops being handled",
        "file": SHOPIFY_FLOW,
        # TaskGroup.ShippingRate had no reader for its whole life; PickRate is that reader.
        # The blank guard is what keeps a group that never set the field behaving exactly as
        # before. Removing it lets a null preference reach preference.Trim().
        "find": "if (string.IsNullOrWhiteSpace(preference)) return null;",
        "replace": "",
        "test": "FullyQualifiedName~ShippingRateSelectionTests",
        "guard": "ABlankPreferenceSelectsNothing",
    },
    {
        "name": "round 575 -- the shape audit's return-type class loses its nullable marker",
        "file": SHAPE_AUDIT,
        # R575: without `\?` in the class, `public SmartActionFilterInput? AddInput(…)` fails to match and is
        # reported as `?` -- "the replica does not have this member" -- instead of `method`. Two rows were wrong,
        # and the direction of the error matters: `?` and `method` lead to opposite work.
        "find": r"r'[\w<>,\[\]\.\?\s]+?\s+'",
        "replace": r"r'[\w<>,\[\]\.\s]+?\s+'",
        "test": "FullyQualifiedName~ShapeAuditGuardTests",
        "guard": "NullableReturningPublicMethodsAreNotReportedAsMissing",
    },
    {
        "name": "round 579 -- bind_diff stops stripping the generic-arity suffix",
        "file": BIND_DIFF,
        # R576 checked this split and found it correct; R579 pinned it. Without `split('`')[0]`,
        # `Cybersole.Models.EditValue`1` no longer matches `class EditValue<T>`, so the type becomes ABSENT.
        # It also degrades the member names to `HasMultiple`, which the NOISE pattern then misses -- the real gap
        # would read 16 instead of 4. Two metrics wrong from one regex, with no visible symptom.
        "find": "simple = typ.split('.')[-1].split('`')[0]",
        "replace": "simple = typ.split('.')[-1]",
        "test": "FullyQualifiedName~BindDiffGuardTests",
        "guard": "GenericTypeNameSuffixDoesNotMakeTheTypeAbsent",
    },
    {
        "name": "round 580 -- bind_scope DECL forgets `class`",
        "file": BIND_SCOPE,
        # R580: the failure this tool could previously hide. Drop `class` and most of the examined set
        # vanishes while `types with scope misses` stays 0 -- the metric looks better, not worse.
        # (The first version of this mutation dropped `record` instead and was DECORATIVE: the only
        # binding-table records are positional ones DECL cannot parse, so `record` contributes nothing.)
        "find": "DECL = re.compile(r\"\\b(?:class|interface|record|struct)\\s+(\\w+)\\s*(?::\\s*([^;{]+?))?\\s*(?:where[^;{]*)?\\{\")",
        "replace": "DECL = re.compile(r\"\\b(?:interface|record|struct)\\s+(\\w+)\\s*(?::\\s*([^;{]+?))?\\s*(?:where[^;{]*)?\\{\")",
        "test": "FullyQualifiedName~BindScopeGuardTests",
        "guard": "ScopeMissesStayAtZeroAndTheExaminedSetReconciles",
    },
    {
        "name": "round 605 -- the metric-claims document names a tool that does not exist",
        "file": METRIC_CLAIMS,
        # R604 wrote docs/METRIC_CLAIMS.md by hand; it is the only place that says what each number can and cannot
        # prove. Nothing else keeps it in step with tools/, so a rename there would leave a document that still reads
        # authoritative and is silently wrong about which script produces which number.
        "find": "tools/bind_scope.py",
        "replace": "tools/bind_scopex.py",
        "test": "FullyQualifiedName~MetricClaimsTests",
        "guard": "EveryToolTheDocumentNamesExists",
    },
    {
        "name": "round 606 -- the metric index points at a section that does not exist",
        "file": BLOCKERS_DOC,
        # R606 added a metric index to BLOCKERS.md ("I don't believe this number, what do I read?"). It is
        # hand-written, so renumbering a heading leaves a pointer into nothing -- which reads as if the explanation
        # exists. The guard parses the index block and requires every section number it names to be a real heading.
        #
        # R980: the target section was \u00a799, chosen when the document had barely a hundred sections. It has four
        # hundred now, so \u00a799 came to name a real heading and the mutation stopped mutating anything -- the run
        # reported "GUARD IS DECORATIVE", which blamed the guard for the mutation's own expired premise. \u00a79999
        # cannot become a real heading.
        "find": "| **\u540d\u5b57\u7ea7\u7f3a\u53e3\u62a5\u5c11\u4e86** | \u00a724\u3001\u00a725 |",
        "replace": "| **\u540d\u5b57\u7ea7\u7f3a\u53e3\u62a5\u5c11\u4e86** | \u00a724\u3001\u00a79999 |",
        "test": "FullyQualifiedName~MetricClaimsTests",
        "guard": "EverySectionTheMetricIndexReferencesExists",
    },
    {
        "name": "round 621 -- the type-presence triage list drifts from the presence metric",
        "file": TRIAGE_SCRIPT,
        # R619/R620 built the per-item classification of the ABSENT types; R621 gave it a guard. Deleting one entry
        # leaves the script's own self-check satisfied (rows == len(ABSENT)) and only the cross-check against
        # `bind_diff --type-presence` notices -- which is exactly the drift worth failing on.
        "find": "    \"TaskCreatorMainView\": \"ProfileGroupItems, ProfileItems, ShowCartView, SizeItems\",\n",
        "replace": "",
        "test": "FullyQualifiedName~TypePresenceTriageTests",
        "guard": "EveryAbsentTypeCarriesExactlyOneVerdict",
    },
    {
        "name": "round 623 -- the copy audit's detail loop goes back to the old predicate",
        "file": COPY_AUDIT,
        # R590 was exactly this defect: the summary was fixed and the detail loop was not, so the file stated one
        # number and listed another number of rows. R622 changed the predicate again (a key whose name appears in the
        # source counts as in use), which is the kind of edit that can land on one consumer only.
        # The mutation restores the narrow predicate in the DETAIL loop while the summary keeps the new one.
        # R980: the anchor had been SKIPPED since the predicate gained its fourth argument. `_satisfied(k, v, text)` became
        # `_satisfied(k, v, text, code)` when comments started being stripped before the key lookup, so the literal no
        # longer existed and the mutation quietly stopped running. A predicate's signature is exactly the kind of thing a
        # later round changes, so the anchor is now a pattern over the call and not a copy of it.
        "find_re": r"if not _satisfied\(k, v, text, code\):\n(\s+)lines\.append",
        "replace_re": r"if not _present(v, text):\n\g<1>lines.append",
        "test": "FullyQualifiedName~CopyAuditConsistencyTests",
        "guard": "DetailRowsMatchTheSummaryTotal",
    },
    {
        "name": "round 1076 -- the checkout totals lose a NOT_CALCULATED marker",
        "file": NIKE_FLOW,
        # BuildTotals is pinned by an exact-JSON assertion, so flipping one marker back to a
        # pre-decompile shape ("CALCULATED") has to redden the pin.
        "find": '                    ["items"] = new JObject { ["tax"] = 0, ["type"] = "NOT_CALCULATED" },',
        "replace": '                    ["items"] = new JObject { ["tax"] = 0, ["type"] = "CALCULATED" },',
        "test": "FullyQualifiedName~NikeBuyRequestTests",
        "guard": "TheCheckoutRequestCarriesPaymentTokenEmailFirstAndTotals",
    },
    {
        "name": "round 1076 -- the ASTLA/CA state sentinel loses its CA half",
        "file": NIKE_FLOW,
        # The sentinel branch is decompiled behaviour (0x146B34B08/0x146B655C8), not a formatting
        # choice; dropping one literal puts the raw state where the join belonged.
        "find": '        return state == "ASTLA" || state == "CA"',
        "replace": '        return state == "ASTLA"',
        "test": "FullyQualifiedName~NikeBuyRequestTests",
        "guard": "TheStateSentinelsJoinCountryAndState",
    },
    {
        "name": "round 1078 -- PayPal's hermione app name drifts",
        "file": PAYPAL_3DS,
        # The frozen literal 0x146fc7338 is pinned by value, not by self-reference.
        "find": '    public const string AppName = "checkoutuinodeweb_hermione";',
        "replace": '    public const string AppName = "hermione";',
        "test": "FullyQualifiedName~PayPalThreeDsTests",
        "guard": "TheStageConstantsMatchTheFrozenLiterals",
    },
    {
        "name": "round 1078 -- the 429 half of the shared retry closure disappears",
        "file": PAYPAL_3DS,
        # Both builders register ONE closure for 403 and 429 (sub_141102970/sub_141105A80's
        # status dispatch); splitting them is precisely the behaviour the pin forbids.
        "find": "        if (res.StatusCode is 403 or 429) return StageOutcome.Retry(res.StatusCode);",
        "replace": "        if (res.StatusCode == 403) return StageOutcome.Retry(res.StatusCode);",
        "test": "FullyQualifiedName~PayPalThreeDsTests",
        "guard": "TheStatusDispatchMirrorsTheRegisteredHandlers",
    },
    {
        "name": "round 1077 -- a Farfetch step forgets why its route is unknown",
        "file": FARFETCH_FLOW,
        # The reclassified message names the server-delivered config and the credential it needs;
        # shortening it back to a bare "unknown" is the retraction the guard exists to catch.
        "find": '            "farfetch: product endpoint unknown -- server-delivered route (connect/app config), schema needs the original login");',
        "replace": '            "farfetch: product endpoint unknown");',
        "test": "FullyQualifiedName~FarfetchIsCoveredByTheOriginalTests",
        "guard": "TheStepsNameTheServerDeliveredTransport",
    },
]


#: A mutated build can make a browser-backed test loop forever, and an unbounded run then says nothing at all —
#: it neither fails nor finishes. Rounds 180-181 hit exactly that: every mutation looked identical to a hang. So each
#: run is bounded, and a bound is reported as its own verdict ("hung") rather than folded into "caught".
RUN_TIMEOUT_SECONDS = 600


def restore_bytes(path, data, attempts=5):
    """Byte-exact restore that tolerates a lingering handle.

    R1079: the first wb-restore crashed with EINVAL on one file while the test host was still
    tearing down after its run -- transient, and a plain retry succeeded moments later. A restore
    that dies mid-loop leaves the tree mutated, which is worse than any delay, so it retries with
    a growing pause; if the file still refuses, the crash-proof copy in .mutation-backup holds
    the same bytes and the next run's repair path restores from it.
    """
    import time
    for attempt in range(attempts):
        try:
            with io.open(path, "wb") as handle:
                handle.write(data)
            return
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.4 * (attempt + 1))


def content_manifest():
    """sha256 of every file a mutation run exercises, keyed by repo-relative path.

    R1079: the reporter's staleness used mtimes, and a git restore of the run's own line-ending
    churn (identical bytes, new timestamp) read as staleness. Hashes do not have that failure
    mode. The set walked here must stay the same as the one mutation_report.py walks: src,
    tests and tools, .cs/.py only, no obj/bin/.mutation-backup, and the reporter itself excluded
    there (reading cannot change a verdict) — while this checker is INCLUDED, because editing
    the mutation list is exactly the kind of change that makes the last run stop describing it.
    """
    import hashlib
    manifest = {}
    for base in ("src", "tests", "tools"):
        for dp, _d, fns in os.walk(os.path.join(REPO, base)):
            if f"{os.sep}obj{os.sep}" in dp or f"{os.sep}bin{os.sep}" in dp or ".mutation-backup" in dp:
                continue
            for fn in fns:
                if not (fn.endswith(".cs") or fn.endswith(".py")):
                    continue
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, REPO).replace(os.sep, "/")
                if rel == "tools/mutation_report.py":
                    # Symmetric with mutation_report.py's own walk, which excludes itself (R982):
                    # editing the reader cannot change a verdict, and a manifest that hashed it
                    # would make every reporter improvement mark the run stale.
                    continue
                try:
                    data = io.open(p, "rb").read()
                except OSError:
                    continue
                manifest[rel] = hashlib.sha256(data).hexdigest()
    return manifest


def run_tests(test_filter, trx=None):
    """Return (exit_code, tail) for a filtered test run. `exit_code` is None when the run was cut off.

    R206: `trx` writes a result file, because `-v q` prints a count and not the names. Without it a red
    restore-verification says "1 failed" and nothing else, which is not enough to act on.
    """
    args = [DOTNET, "test", os.path.join(REPO, "tests", "Cybersole.Tests",
                                        "Cybersole.Tests.csproj"),
            "--filter", test_filter, "-v", "q", "--nologo"]
    if trx:
        args += ["--logger", "trx;LogFileName=" + trx]
    try:
        result = subprocess.run(
            args, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return None, ["timeout after %ds" % RUN_TIMEOUT_SECONDS]
    return result.returncode, (result.stdout or "").strip().splitlines()[-3:]


def failed_names(trx):
    """The tests a trx marks Failed, so a red verdict can name them instead of counting them."""
    if not trx or not os.path.exists(trx):
        return []
    try:
        import xml.etree.ElementTree as ET
        ns = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"
        root = ET.parse(trx).getroot()
        out = []
        for r in root.iter(ns + "UnitTestResult"):
            if r.get("outcome") == "Failed":
                out.append(r.get("testName"))
        return out
    except Exception as exc:                      # a broken trx must not hide the verdict
        return ["<trx unreadable: %s>" % exc]


def classify_hung():
    """Say what a cut-off run means: the mutation did not just fail a guard, it stopped the guard finishing."""
    return {"verdict": "hung", "why": "the run did not finish inside %ds" % RUN_TIMEOUT_SECONDS}


def classify(code, tail):
    """
    Say whether a red run is a real catch.

    A mutation that fails to compile also makes `dotnet test` exit non-zero, and that is not
    evidence of anything: the guard never ran. Three mutations in the first pass did exactly
    this and looked identical to a catch in the summary. A compile error is reported separately
    so it can be fixed rather than counted.
    """
    joined = "\n".join(tail)
    if "error CS" in joined:
        return "DID NOT COMPILE — the guard never ran"
    if code == 0:
        return "GUARD IS DECORATIVE — tests stayed green"
    return "guard fired"


def repair_leftovers():
    """Restore any file a killed run left mutated.

    <para>
    The mutation is applied with a marker comment (<c>MUTATED</c>) so a leftover is visible from the
    file alone; this pass rewrites the affected files from the backup directory before anything runs.
    </para>
    """
    backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mutation-backup")
    if not os.path.isdir(backup_dir):
        return 0

    repaired = 0
    for name in os.listdir(backup_dir):
        target = os.path.join(REPO, "src", name.replace("_", os.sep))
        if not os.path.exists(target):
            continue
        current = io.open(target, encoding="utf-8").read()
        if "MUTATED" not in current:
            continue
        saved = io.open(os.path.join(backup_dir, name), encoding="utf-8").read()
        with io.open(target, "w", encoding="utf-8", newline="") as handle:
            handle.write(saved)
        repaired += 1
        print("repaired a leftover mutation: " + name)

    return repaired


def main():
    repair_leftovers()
    results = []

    # R281: --limit N (and --only TEXT) so the tool can be smoke-tested cheaply. A full pass takes about an hour
    # because each mutation rebuilds and reruns its guard, which is fine once a session but far too much to check that
    # the harness itself still works.
    limit = None
    only = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--limit" and i + 1 < len(sys.argv) - 1:
            limit = int(sys.argv[i + 2])
        if arg == "--only" and i + 1 < len(sys.argv) - 1:
            only = sys.argv[i + 2]

    selected = MUTATIONS
    if only:
        selected = [m for m in MUTATIONS if only.lower() in m["name"].lower()]
    if limit:
        selected = selected[:limit]

    print(f"running {len(selected)} of {len(MUTATIONS)} mutations")

    for m in selected:
        path = m["file"]
        # R1079 byte-faithful round-trip, second cut. The first cut read with newline="" as well,
        # which keeps \r\n in the working string -- and the find_re anchors (R980) match on \n, so
        # four patterns stopped matching and their mutations reported SKIPPED. Matching stays on
        # the universal-newline text exactly as it always was; only the BACKUP and the RESTORE go
        # byte-exact, so what leaves the run is the same bytes that entered it.
        original = io.open(path, encoding="utf-8").read()   # matching text: newline-normalised
        saved_raw = io.open(path, "rb").read()              # restore bytes: verbatim

        # keep a crash-proof copy so an interrupted run can be repaired by the next one
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mutation-backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup = os.path.join(backup_dir, os.path.basename(path).replace(os.sep, "_"))
        with io.open(backup, "wb") as handle:
            handle.write(saved_raw)

        # R980: a mutation may name its anchor as a regular expression instead of a literal. A literal that contains a
        # number which moves -- a module count, a section count -- silently stops matching the moment the number changes,
        # and the run then reports "SKIPPED" rather than testing anything. That happened to round 164 twice and to round
        # 623 once. A pattern cannot go stale the same way: it matches whatever the current number is and substitutes a
        # deliberately wrong one.
        if "find_re" in m:
            mutated, matched = re.subn(m["find_re"], m["replace_re"], original,
                                       count=0 if m.get("all") else 1)
            if matched == 0:
                results.append((m["name"], "SKIPPED — pattern matched nothing"))
                print(f"  [skip] {m['name']}: pattern matched nothing")
                continue
        else:
            if m["find"] not in original:
                results.append((m["name"], "SKIPPED — anchor not found"))
                print(f"  [skip] {m['name']}: anchor not found")
                continue

            mutated = original.replace(m["find"], m["replace"], -1 if m.get("all") else 1)

        try:
            io.open(path, "w", encoding="utf-8", newline="").write(mutated)
            code, tail = run_tests(m["test"])
            verdict = classify_hung()["verdict"] if code is None else classify(code, tail)
            results.append((m["name"], verdict))
            print(f"  [{verdict}] {m['name']}")
            for line in tail:
                print(f"        {line[:110]}")
        finally:
            restore_bytes(path, saved_raw)
            print(f"        restored {os.path.basename(path)}")

    print("\n== summary ==")
    for name, verdict in results:
        print(f"  {verdict:44} {name}")

    # confirm the tree really is back to green. A red verdict must NAME the test: `-v q` only counts.
    trx = os.path.join(os.path.dirname(REPO), "analysis", "_mutation-restore.trx")
    if os.path.exists(trx):
        os.remove(trx)
    code, tail = run_tests("Speed!=Slow", trx=trx)
    state = "UNKNOWN (cut off)" if code is None else ("GREEN" if code == 0 else "RED")
    print("\nrestored tree: " + state)
    for line in tail:
        print("  " + line[:110])
    for name in failed_names(trx):
        print("  FAILED: " + name)

    # R982: criterion (e) says the mutation tests all fire, and until now that figure lived only in prose -- the one thing
    # this project's conventions forbid. A full run takes about twelve minutes, so it cannot run inside metrics_report;
    # what it can do is leave a dated result the metrics read and a freshness check beside it, so the number is a number
    # with a timestamp rather than an impression. `tools/mutation_report.py` reads this file.
    import json
    fired = sum(1 for _n, v in results if v == "guard fired")
    decorative = sum(1 for _n, v in results if "DECORATIVE" in v)
    skipped = sum(1 for _n, v in results if v.startswith("SKIPPED"))
    record = {
        "ran_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))).isoformat(timespec="seconds"),
        "total": len(results),
        "fired": fired,
        "decorative": decorative,
        "skipped": skipped,
        "tree": state,
    }
    # R1079: staleness by CONTENT, not mtime. The mtime check mis-fired the same round it was healthy:
    # restoring a mutation's own EOL churn with git rewrites the file with identical bytes and a new mtime,
    # and the reporter then called the run stale over a change that did not happen. The manifest hashes
    # every file a run exercises; tools/mutation_report.py compares hashes, so a byte-identical restore
    # is fresh and a real edit is stale regardless of timestamps.
    record["content_manifest"] = content_manifest()

    out = os.path.join(os.path.dirname(REPO), "analysis", "MUTATION_RESULT.json")
    with io.open(out, "w", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print("\nwrote " + out)


if __name__ == "__main__":
    main()
