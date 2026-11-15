import io, json, os
A = os.path.expandvars(r"%APPDATA%\Cybersole")

settings = json.loads(io.open(os.path.join(A,'settings.json'), encoding='utf-8-sig', errors='replace').read())
tasks = json.loads(io.open(os.path.join(A,'tasks.json'), encoding='utf-8-sig', errors='replace').read())
solvers = json.loads(io.open(os.path.join(A,'solvers.json'), encoding='utf-8-sig', errors='replace').read())

group_keys = list(tasks[0].keys())
solver_obj = solvers[0]['solvers'][0]
solver_keys = list(solver_obj.keys())
solver_settings_keys = list((solver_obj.get('settings') or {}).keys())
settings_keys = list(settings.keys())

def cs(names, indent=12):
    body = ''
    line = ' ' * indent
    for n in names:
        piece = '"' + n + '", '
        if len(line) + len(piece) > 100:
            body += line.rstrip() + '\n'
            line = ' ' * indent
        line += piece
    body += line.rstrip().rstrip(',')
    return body

code = '''using System.Linq;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R383: the field names the running build actually writes to %APPDATA%\\\\Cybersole, pinned so a rename cannot slip by.
///
/// <para>
/// These lists were read out of the live application's own JSON on 2026-11-14 — settings.json (43 top-level keys),
/// tasks.json (one TaskGroup) and solvers.json (one Solver plus its SolverSettings). They are the hardest evidence in this
/// project: the program wrote them itself. The test asserts each name still resolves to a member, so a property renamed in
/// the replica fails here instead of silently diverging from what the original persists.
/// </para>
/// </summary>
public sealed class LiveSchemaPinsTests
{
    private readonly ITestOutputHelper _out;
    public LiveSchemaPinsTests(ITestOutputHelper output) => _out = output;

    [Fact]
    public void TheSettingsFileFieldsAllExist()
    {
        var names = new[]
        {
''' + cs(settings_keys) + '''
        };

        var props = typeof(GlobalSettings).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var missing = names.Where(n => !props.Contains(n)).ToList();

        _out.WriteLine($"{names.Length} live keys, missing: {missing.Count}");
        Assert.Empty(missing);
    }

    [Fact]
    public void TheTaskGroupFileFieldsAllExist()
    {
        var names = new[]
        {
''' + cs(group_keys) + '''
        };

        var props = typeof(TaskGroup).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var missing = names.Where(n => !props.Contains(n)).ToList();

        _out.WriteLine($"{names.Length} live keys, missing: {missing.Count}");
        Assert.Empty(missing);
    }

    [Fact]
    public void TheSolverFileFieldsAllExist()
    {
        var solver = new[]
        {
''' + cs(solver_keys) + '''
        };

        var settings = new[]
        {
''' + cs(solver_settings_keys) + '''
        };

        var solverProps = typeof(Solver).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();
        var settingsProps = typeof(SolverSettings).GetProperties().Select(p => p.Name.ToLowerInvariant()).ToHashSet();

        Assert.Empty(solver.Where(n => !solverProps.Contains(n)).ToList());
        Assert.Empty(settings.Where(n => !settingsProps.Contains(n)).ToList());
        _out.WriteLine($"{solver.Length} + {settings.Length} live keys, all present");
    }
}
'''
io.open(r"D:\projects\cyber-reverse\replica\tests\Cybersole.Tests\LiveSchemaPinsTests.cs", 'w', encoding='utf-8', newline='').write(code)
print('test written;', len(settings_keys), 'settings keys,', len(group_keys), 'group keys,', len(solver_keys), '+', len(solver_settings_keys), 'solver keys')
