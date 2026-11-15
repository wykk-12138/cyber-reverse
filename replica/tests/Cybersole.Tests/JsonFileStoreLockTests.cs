using System;
using System.Collections.Generic;
using System.IO;
using Cybersole.Core.Store;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R438: <c>JsonFileStore.Save</c> used to be <c>WriteAllText(tmp)</c> then <c>File.Delete(path)</c> then
/// <c>File.Move(tmp, path)</c>. The full suite caught the second step throwing for real:
///
/// <code>
/// System.IO.IOException: The process cannot access the file
///   '...\CybersoleReplica\tasks.json' because it is being used by another process.
/// </code>
///
/// <para>
/// Two defects in one method: a <b>window</b> between Delete and Move (a crash there loses the document),
/// and <b>no tolerance</b> for a briefly held handle. The fix is one <c>Move(overwrite: true)</c> plus a
/// bounded retry.
/// </para>
/// <para>
/// <b>What is NOT tested here, and why.</b> The obvious way to pin the retry is to hold the file open and
/// watch Save wait. That was tried with <c>FileShare.Read</c> and then <c>FileShare.None</c> and <b>both let
/// the replace through</b> — a rename does not need read access to the target, so a normal Windows handle
/// cannot simulate the transient lock that actually broke the suite. Rather than ship a test that asserts
/// nothing, the lock behaviour is guarded at the source level below: whoever reintroduces
/// Delete-then-Move turns it red.
/// </para>
/// </summary>
public sealed class JsonFileStoreLockTests
{
    private readonly ITestOutputHelper _out;

    public JsonFileStoreLockTests(ITestOutputHelper output) => _out = output;

    private static string RepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !File.Exists(Path.Combine(dir.FullName, "Cybersole.sln")))
            dir = dir.Parent;
        Assert.NotNull(dir);
        return dir!.FullName;
    }

    private static string TempStore(out string path)
    {
        var dir = Path.Combine(Path.GetTempPath(), "cyb-store-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        path = Path.Combine(dir, "tasks.json");
        File.WriteAllText(path, "{\"seed\":\"1\"}");
        return dir;
    }

    [Fact]
    public void Save_ReplacesAnExistingFile_AndLeavesNoTempBehind()
    {
        var dir = TempStore(out var path);
        try
        {
            var store = new JsonFileStore(path);

            store.Save(new Dictionary<string, string> { ["a"] = "b" });

            Assert.Contains("\"a\"", File.ReadAllText(path));
            Assert.DoesNotContain("seed", File.ReadAllText(path));
            Assert.False(File.Exists(path + ".tmp"), "the .tmp scratch file must not survive a successful save");
            _out.WriteLine(File.ReadAllText(path));
        }
        finally
        {
            Directory.Delete(dir, true);
        }
    }

    [Fact]
    public void Save_WritesIntoANewStoreDirectory()
    {
        // The first save in a fresh data root must create the directory, not throw.
        var root = Path.Combine(Path.GetTempPath(), "cyb-store-" + Guid.NewGuid().ToString("N"));
        var path = Path.Combine(root, "nested", "tasks.json");
        try
        {
            new JsonFileStore(path).Save(new Dictionary<string, string> { ["fresh"] = "1" });

            Assert.True(File.Exists(path));
            Assert.Contains("fresh", File.ReadAllText(path));
        }
        finally
        {
            if (Directory.Exists(root)) Directory.Delete(root, true);
        }
    }

    [Fact]
    public void Save_ReplacesInOneCall_InsteadOfDeleteThenMove()
    {
        // Source-level guard for the part a Windows test cannot simulate (see the class remarks).
        var source = File.ReadAllText(
            Path.Combine(RepoRoot(), "src", "Cybersole.Core", "Store", "AppPaths.cs"));

        var start = source.IndexOf("public void Save<T>", StringComparison.Ordinal);
        Assert.True(start >= 0, "JsonFileStore.Save is gone — update this guard");

        // Comments are stripped first: the doc comment above the method *quotes* the old
        // "File.Delete(_path)" line to explain why it went away, and a raw text scan counts that quote as
        // the defect. Same reasoning as CheckboxLabelTests (R249: prose was being counted as code).
        var body = System.Text.RegularExpressions.Regex.Replace(
            source[start..], @"(?<!:)//[^\n]*", " ");

        Assert.DoesNotContain("File.Delete(_path)", body);
        Assert.Contains("overwrite: true", body);
        Assert.Contains("catch (IOException)", body);
        Assert.Contains("attempt <", body);          // a bounded retry, not an unbounded loop
        _out.WriteLine("Save replaces in one call with a bounded IOException retry");
    }
}
