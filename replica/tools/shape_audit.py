import io, os, re, sys, json, collections

ROOT = r"D:\projects\cyber-reverse\replica"
POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")

# 1) shapes: two evidence sources, and the choice matters (R885).
#
#   pool     -- analysis/pe_strings.txt, the sampled string dump. 180,228 lines that read like a
#               full inventory and are not; IDA's own inventory is far larger. Section 2.7b records
#               four rounds of trouble from treating this as complete.
#   baseline -- docs/baseline/recovered_accessors_by_type.txt, written in R883 from
#               idautils.Strings() over the whole image: 508 declaring types. This is the source to
#               prefer, and the reason this switch exists is that the pool does not even contain
#               Cybersole.Models.CreateModel, so any audit built on it reports that type as absent.
BASELINE = os.path.join(ROOT, "docs", "baseline", "recovered_accessors_by_type.txt")
shape = collections.defaultdict(lambda: collections.defaultdict(set))

if "--baseline" in sys.argv and os.path.exists(BASELINE):
    # R886 format: one row per (type, property) with the accessor kinds kept, because the setter check
    # below reads them. R883's format collapsed this to one row per type and dropped the kind, which made
    # the check silently match nothing.
    for line in io.open(BASELINE, encoding="utf-8", errors="replace"):
        if line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        decl, prop, ks = parts
        short = decl.split(".")[-1]
        prop = prop.strip().split(".")[-1]
        if not prop:
            continue
        for k in ks.split(","):
            if k.strip():
                shape[short][prop].add(k.strip())
    print("evidence: baseline (%d types, kinds kept)" % len(shape))
else:
    lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
    rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
    for r in rows:
        for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
            member, kind = m.group(1), m.group(2)
            idx = r.find(',Cybersole.' + member + '!' + kind)
            if idx <= 0:
                continue
            t = re.split(r'[,\s]', r[:idx])[-1].split('.')[-1]
            shape[t][member].add(kind)
    print("evidence: string pool (%d types, sampled)" % len(shape))

# 2) replica declarations, per type body (brace matched)
# R1186: blank out comments and string literals before looking for declarations. The declaration regex is
# `(?:class|record|interface)\s+(\w+)`, and prose uses those words too: Checkout.cs carries a comment with
# "a record of the checkout ..." in it, so the scanner invented a type called `of`, claimed a thousand
# characters of the file as its body - which contained Checkout's own members - and left Checkout with a
# fragment. Every member beyond that point then read as `replica=?`, i.e. "the replica does not have this
# member" for a member that is right there in the file. This is the R764 failure (brace counting disturbed by
# text that is not code) surviving in a second place, and the same lesson applies: strip first, parse second.


def strip_non_code(text):
    """Blank comments and string/char literals, preserving offsets and line structure."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            while i < n and text[i] != '\n':
                out.append(' ')
                i += 1
        elif c == '/' and i + 1 < n and text[i + 1] == '*':
            out.append(' ')
            out.append(' ')
            i += 2
            while i < n and not (text[i] == '*' and i + 1 < n and text[i + 1] == '/'):
                out.append('\n' if text[i] == '\n' else ' ')
                i += 1
            if i < n:
                out.append(' ')
                out.append(' ')
                i += 2
        elif c == '"' or c == "'":
            quote = c
            verbatim = i > 0 and text[i - 1] == '@'
            out.append(' ')
            i += 1
            while i < n:
                if text[i] == '\\' and not verbatim and i + 1 < n:
                    out.append(' ')
                    out.append(' ')
                    i += 2
                    continue
                if text[i] == quote:
                    out.append(' ')
                    i += 1
                    break
                out.append('\n' if text[i] == '\n' else ' ')
                i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


bodies = {}
body_projects = {}
is_interface = set()
implementors = {}
for dirpath, _d, files in os.walk(os.path.join(ROOT, "src")):
    if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
        continue
    _parts = dirpath.replace("/", os.sep).split(os.sep)
    # R1194: remember which project each body came from. The owner map further down is keyed by bare type name
    # and takes the first project it sees, so a name declared in two projects was attributed to whichever came
    # first in the walk. Recording the provenance here settles that without guessing.
    _proj = _parts[_parts.index("src") + 1] if "src" in _parts and _parts.index("src") + 1 < len(_parts) else "(unknown)"
    for fn in files:
        if not fn.endswith(".cs"):
            continue
        text = strip_non_code(io.open(os.path.join(dirpath, fn), encoding='utf-8', errors='replace').read())
        # R1195: which classes name which interfaces. A binding to IWebhook.ExtraFields is resolved by the binder
        # against the object it was handed, and that object is a Webhook instance, not the interface - so judging
        # the interface body reported five members as read-only that the implementing class already exposes with
        # setters. The contract was being measured instead of the thing the contract describes.
        for _c in re.finditer(r"\bclass\s+(\w+)\s*(?:<[^>]*>)?\s*:\s*([^{\n]+)", text):
            for _name in re.findall(r"\b(I[A-Z]\w*)\b", _c.group(2)):
                implementors.setdefault(_name, []).append(_c.group(1))
        for m in re.finditer(r"\b(?:class|record|interface)\s+(\w+)[^;{]*\{", text):
            depth, start = 0, m.end() - 1
            for i in range(start, len(text)):
                if text[i] == '{': depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        bodies.setdefault(m.group(1), []).append(text[m.start():i+1])
                        body_projects.setdefault(m.group(1), set()).add(_proj)
                        if m.group(0).lstrip().startswith("interface"):
                            is_interface.add(m.group(1))
                        break

def kind_of(body, member):
    # R1187: a positional record parameter is a property, but it lives in the declaration line rather than in
    # the braces, so `public sealed record Notification(Kind, string Title, ...) { }` reported Title as `?` -
    # "the replica does not have this member" - when what is true is "it has it and it cannot be written".
    # Those two lead to different repairs, so the reason is reported as its own kind instead of absence.
    if re.search(r'\brecord\s+\w+\s*\([^)]*\b' + member + r'\b[^)]*\)', body):
        return 'record-positional'
    # R470: an `ICommand` property is read-only by design — the original's `Setter` evidence on an action
    # member means "it is a bindable property", not "someone assigns to it". Treating `ICommand Foo { get; }`
    # as a mismatch produced 9 false positives (MonitorView.OpenFilter/OpenUrl/Quicktask/LinkChange,
    # AccountGrid.Edit, …). Check this before the plain getter rule.
    if re.search(r'\bICommand\s+' + member + r'\b', body):
        return 'command'
    # R470b: the old rules required `{ get;` on one line. Properties written as
    #
    #     public IReadOnlyList<string> SelectedProfiles
    #     {
    #         get => _checkoutProfile;
    #     }
    #
    # matched none of them and fell through to '?' — i.e. "the replica does not have this member", which is
    # wrong and inflates the not-found bucket. Take the whole property block first, then look inside it.
    block = re.search(r'\b' + member + r'\s*\{', body)
    if block:
        # A fixed window rather than a matched block: property bodies can contain lambdas (`get => { … }`),
        # and requiring a brace-free block dropped those back into '?' (3 regressions when first tried).
        window = body[block.end():block.end() + 400]
        if re.search(r'\bset\b', window):
            return 'prop+set'
        if re.search(r'\bget\b', window):
            return 'prop-get'
    if re.search(r'\b' + member + r'\s*=>', body):
        return 'prop-get'
    # R517: X ( matched a CALL, not a definition — MessageBoxDialog's Close() call-site made the audit
    # report Close as "the replica has a method", when the member is actually inherited from Window and
    # the audit was reading an invocation. 58 of the 140 mismatches were that. A declaration needs a return
    # type and an access modifier in front of the name.
    # R530: only a PUBLIC declaration can be a binding target. Counting `private` ones made
    # `ExpressionView.Refresh` (a `private void Refresh()`) look like "the replica has it as a method" when the
    # binding cannot reach it at all — that is a missing member, not a wrong shape.
    # R575: the return-type char class was missing `?`, so a public method returning a NULLABLE type
    # (`SmartActionFilterInput? AddInput(…)`, `string? ToggleFilterBehaviour(…)`) failed to match and fell
    # through to '?', i.e. "the replica does not have this member". That is the same family as the three
    # defects already recorded above (R470b property blocks, R517 call-sites, R530 private declarations):
    # a regex that is too narrow reports absence where the member exists. Two of the 80 rows were this.
    if re.search(r'\bpublic\s+(?:static\s+|async\s+|override\s+|virtual\s+)*'
                 r'[\w<>,\[\]\.\?\s]+?\s+' + member + r'\s*\(', body):
        return 'method'
    return '?'

rows_out = []
over_out = []
for full, members in sorted(json.load(io.open(BINDS, encoding='utf-8')).items()):
    short = full.split('.')[-1]
    ev = shape.get(short)
    body = "\n".join(bodies.get(short, []))
    # R1195: an interface is a contract, not the object the binder was handed. When the matched type is an
    # interface that some class implements, judge the implementing class instead; if nothing implements it, the
    # honest answer is that the replica exposes the contract and no concrete type, which is its own reason.
    if short in is_interface:
        _impls = [n for n in implementors.get(short, []) if n in bodies]
        if _impls:
            body = "\n".join("\n".join(bodies.get(n, [])) for n in _impls)
    if not ev or not body:
        continue
    for m in sorted(members):
        kinds = ev.get(m)
        if not kinds:
            continue
        have = kind_of(body, m)
        want_set = 'Setter' in kinds
        # `command` is a deliberate match: an ICommand property is bindable and read-only by design, which is
        # exactly what the original's action members are. Only a genuinely missing setter counts.
        if want_set and have not in ('prop+set', 'command'):
            rows_out.append((short, m, ','.join(sorted(kinds)), have))
        # R1198: the other direction. Every rule above asks for a setter the replica is missing; nothing ever
        # looked for a setter the replica has and the original does not, so a member that is read-only in the
        # shipped product and writable here could never be reported. IWebhook.Type is exactly that - the
        # descriptors carry Type!Getter with no !Setter, while the replica's Webhook.Type is settable - and it
        # went unnoticed until a binding table was read by hand. These rows are counted apart from the totals
        # rather than mixed in: an extra setter does not break a binding, it widens what the UI can do.
        elif (not want_set) and have == 'prop+set' and 'command' not in (have,):
            over_out.append((short, m, ','.join(sorted(kinds)), have))

print('mismatches: member has Setter evidence but the replica is not a settable property')
for t, m, kinds, have in rows_out:
    print('  %-26s %-22s evidence=%-26s replica=%s' % (t, m, kinds, have))
print('total mismatches:', len(rows_out))

print('')
print('over-permissive: member is read-only in the original but settable here')
for t, m, kinds, have in over_out:
    print('  %-26s %-22s evidence=%-26s replica=%s' % (t, m, kinds, have))
print('over-permissive total:', len(over_out))

# ---------------------------------------------------------------------------------------------
# R888: the same rows, split by the project that owns each type.
#
# The total is a misleading steering signal on its own. Of the ninety-four rows, seventy-seven belong
# to Cybersole.Ui, which is priority four in the user's ordering -- deferred behind checkout flows,
# anti-bot and the request layer. Core and Services carry seventeen between them and Cybersole.Stores
# carries none.
#
# So the published total has been dominated by work the ordering defers, and several rounds went into
# improving the accuracy of a figure whose largest term is out of scope. Splitting it puts the number
# that matters next to the number that does not.
# ---------------------------------------------------------------------------------------------
_owner = {}
for _dp, _dirs, _fs in os.walk(os.path.join(ROOT, "src")):
    if (os.sep + "obj" + os.sep) in _dp or (os.sep + "bin" + os.sep) in _dp:
        continue
    _parts = _dp.replace("/", os.sep).split(os.sep)
    # the project is the directory immediately after "src", and ROOT is absolute so an index from the
    # front would name the drive's parent rather than the project.
    _proj = _parts[_parts.index("src") + 1] if "src" in _parts and _parts.index("src") + 1 < len(_parts) else "(root)"
    for _fn in _fs:
        if not _fn.endswith(".cs"):
            continue
        try:
            _text = io.open(os.path.join(_dp, _fn), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for _m in re.finditer(r"\b(?:class|record|interface)\s+(\w+)", _text):
            _owner.setdefault(_m.group(1), _proj)

# R1194: the owner is the project that actually supplied the body the row was judged against, and a name that
# two projects both declare is reported as (shared) rather than silently credited to whichever came first in the
# walk.
def _owner_of(_short):
    _ps = body_projects.get(_short, set())
    if len(_ps) == 1:
        return next(iter(_ps))
    if len(_ps) > 1:
        return "(shared)"
    return _owner.get(_short, "(unknown)")


_by_proj = collections.Counter(_owner_of(t) for t, _m, _k, _h in rows_out)
print("")
print("by owning project (priority order: Stores > Services > Http > Core > Ui):")
for _p, _n in _by_proj.most_common():
    print("  %-22s %3d" % (_p, _n))

# the one line a metrics runner can read without parsing a table
CORE = ("Cybersole.Stores", "Cybersole.Services", "Cybersole.Http", "Cybersole.Core")
print("core mismatches: %d" % sum(n for p, n in _by_proj.items() if p in CORE))

# ---------------------------------------------------------------------------------------------
# R885: the reverse direction, which this tool never reported. The check above finds members the
# image evidences and the replica lacks; it cannot find members the replica declares and the image
# does not, which is the question R884 left open about CreateModel's twelve extra properties.
#
# What this report IS: a review list. Every row is a replica member under a type the image also has,
# with no accessor evidence for that member.
#
# What it is NOT: proof the member is invented. R883 established that the accessor baseline covers
# only members the runtime materialised for binding, so a plain property that no XAML path touches
# produces no literal either. A row here means "no evidence found", and the two ways that happens --
# the member is mine, or the member is the image's but unbound -- call for opposite remedies.
# ---------------------------------------------------------------------------------------------
want_extra = '--extra' in sys.argv
if want_extra:
    only = None
    if '--type' in sys.argv:
        i = sys.argv.index('--type')
        if i + 1 < len(sys.argv):
            only = sys.argv[i + 1].strip()

    extra = []
    for short, ev in shape.items():
        body = "\n".join(bodies.get(short, []))
        if not ev or not body:
            continue
        if only and short != only:
            continue
        # every public member the replica declares on this type, against the image's evidence
        for m in sorted(set(re.findall(r'public\s+[\w<>\[\]?.,\s]+?\s+(\w+)\s*(?:\{|=>)', body))):
            if m in ev:
                continue
            if m in ('get', 'set', 'value', 'ToString', 'Equals', 'GetHashCode'):
                continue
            extra.append((short, m, kind_of(body, m)))

    print('')
    print('review list: replica member with no accessor evidence for that member')
    print('  not a defect list -- see the header comment above the code that prints it')
    for t, m, have in extra:
        print('  %-26s %-24s replica=%s' % (t, m, have))
    print('total review rows:', len(extra))
