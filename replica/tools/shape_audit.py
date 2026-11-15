import io, os, re, json, collections

ROOT = r"D:\projects\cyber-reverse\replica"
POOL = r"D:\projects\cyber-reverse\analysis\pe_strings.txt"
BINDS = os.path.join(ROOT, "docs", "xaml_bindings.json")

# 1) shapes from the pool
lines = io.open(POOL, encoding='utf-8', errors='replace').read().splitlines()
rows = [m.group(2).strip() for m in (re.match(r'^\s*(0x[0-9a-f]+)\s+(.*)$', l) for l in lines) if m]
shape = collections.defaultdict(lambda: collections.defaultdict(set))
for r in rows:
    for m in re.finditer(r'Cybersole\.(\w+)!(Property|Getter|Setter)', r):
        member, kind = m.group(1), m.group(2)
        idx = r.find(',Cybersole.' + member + '!' + kind)
        if idx <= 0:
            continue
        t = re.split(r'[,\s]', r[:idx])[-1].split('.')[-1]
        shape[t][member].add(kind)

# 2) replica declarations, per type body (brace matched)
bodies = {}
for dirpath, _d, files in os.walk(os.path.join(ROOT, "src")):
    if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
        continue
    for fn in files:
        if not fn.endswith(".cs"):
            continue
        text = io.open(os.path.join(dirpath, fn), encoding='utf-8', errors='replace').read()
        for m in re.finditer(r"\b(?:class|record|interface)\s+(\w+)[^;{]*\{", text):
            depth, start = 0, m.end() - 1
            for i in range(start, len(text)):
                if text[i] == '{': depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        bodies.setdefault(m.group(1), []).append(text[start:i+1])
                        break

def kind_of(body, member):
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
for full, members in sorted(json.load(io.open(BINDS, encoding='utf-8')).items()):
    short = full.split('.')[-1]
    ev = shape.get(short)
    body = "\n".join(bodies.get(short, []))
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

print('mismatches: member has Setter evidence but the replica is not a settable property')
for t, m, kinds, have in rows_out:
    print('  %-26s %-22s evidence=%-26s replica=%s' % (t, m, kinds, have))
print('total mismatches:', len(rows_out))
