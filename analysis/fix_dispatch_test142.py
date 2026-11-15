import io

p = r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\WallDispatchTests.cs"
t = io.open(p, encoding="utf-8").read()

old = '''    private sealed class MinimalFlow : StoreFlow
    {
        public override string Name => "minimal";
        public override IReadOnlyList<string> Domains => new[] { "example.test" };
        public override string Platform => "test";

        public Task<StepOutcome> Detect(FlowContext c, CancellationToken ct) => DetectAsync(c, ct);
    }'''

new = '''    private sealed class MinimalFlow : StoreFlow
    {
        public override string Id => "minimal";
        public override string Name => "minimal";
        public override IReadOnlyList<string> Domains => new[] { "example.test" };

        public Task<StepOutcome> Detect(FlowContext c, CancellationToken ct) => DetectAsync(c, ct);
    }'''

if old not in t:
    raise SystemExit("minimal flow anchor missing")
io.open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new, 1))
print("minimal flow matches the abstract surface")
