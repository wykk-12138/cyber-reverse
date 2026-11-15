using Avalonia.Controls;
using Cybersole.Core.Expressions;
using Cybersole.Core.Models;
using Cybersole.Ui.Views.Profiles;
using Cybersole.Ui.Views.Tasks;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// Tasks + Profiles view parity. Type names below are the recovered XAML files under
/// <c>/Views/Tasks/</c> and <c>/Views/Profiles/</c>.
/// </summary>
public class TaskProfileViewTests
{
    private static readonly string[] TaskViews =
    {
        "TaskCreatorView", "TaskGroupView", "TaskDetailsView", "GroupSummary",
        "TaskGroupListView", "TaskView", "StaggerStartView",
    };

    private static readonly string[] ProfileViews =
    {
        "ProfileCreatorView", "ProfileCsvEditorView", "ExpressionView",
        "ProfileGroupView", "ProfileView",
    };

    [Theory]
    [InlineData("TaskCreatorView")]
    [InlineData("TaskGroupView")]
    [InlineData("TaskDetailsView")]
    [InlineData("GroupSummary")]
    [InlineData("TaskGroupListView")]
    [InlineData("TaskView")]
    [InlineData("StaggerStartView")]
    [InlineData("ProfileCreatorView")]
    [InlineData("ProfileCsvEditorView")]
    [InlineData("ExpressionView")]
    [InlineData("ProfileGroupView")]
    [InlineData("ProfileView")]
    public void ViewTypeExistsInTheExpectedNamespace(string name)
    {
        var assembly = typeof(TaskView).Assembly;
        var type = assembly.GetTypes().FirstOrDefault(t => t.Name == name);
        Assert.NotNull(type);
        Assert.True(typeof(Control).IsAssignableFrom(type), $"{name} is not a Control");
    }

    [Fact]
    public void AllRecoveredTaskViewsArePresent()
    {
        var names = typeof(TaskView).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in TaskViews) Assert.Contains(n, names);
    }

    [Fact]
    public void AllRecoveredProfileViewsArePresent()
    {
        var names = typeof(TaskView).Assembly.GetTypes().Select(t => t.Name).ToHashSet();
        foreach (var n in ProfileViews) Assert.Contains(n, names);
    }

    [Fact]
    public void TaskAndProfileUserControlsConstruct()
    {
        using var services = TestServices.Create();
        var group = services.Config.TaskGroups.First();
        var task = new BotTask { Name = "t1", Store = "Nike" };
        group.Tasks.Add(task);

        Assert.IsAssignableFrom<UserControl>(new TaskCreatorView(services));
        Assert.IsAssignableFrom<UserControl>(new TaskGroupView(services, group));
        Assert.IsAssignableFrom<UserControl>(new TaskDetailsView(services, task));
        Assert.IsAssignableFrom<UserControl>(new GroupSummary(services, group));
        Assert.IsAssignableFrom<UserControl>(new TaskGroupListView(services));
        Assert.IsAssignableFrom<UserControl>(new TaskView(services));

        Assert.IsAssignableFrom<UserControl>(new ProfileCreatorView(services));
        Assert.IsAssignableFrom<UserControl>(new ProfileCsvEditorView(services));
        Assert.IsAssignableFrom<UserControl>(new ExpressionView(services));
        Assert.IsAssignableFrom<UserControl>(new ProfileGroupView(services));
        Assert.IsAssignableFrom<UserControl>(new ProfileView(services));
    }

    [Fact]
    public void CsvColumnChoicesCoverTheProfileFields()
    {
        Assert.Contains("email", ProfileCsvEditorView.ColumnNames);
        Assert.Contains("cardNumber", ProfileCsvEditorView.ColumnNames);
        Assert.Equal(ProfileCsvEditorView.ColumnNames.Length,
            ProfileCsvEditorView.ColumnNames.Distinct().Count());
    }

    [Fact]
    public void TaskGroupCarriesTheRecoveredTabsFields()
    {
        var g = new TaskGroup
        {
            ErrorDelay = 1500,
            ResetLimitsAfter = TimeSpan.FromHours(1),
            WebhookFilter = "Checkouts only",
            ShippingRate = "Standard:0.00",
        };

        Assert.Equal(1500, g.ErrorDelay);
        Assert.Equal(TimeSpan.FromHours(1), g.ResetLimitsAfter);
        Assert.Equal("Checkouts only", g.WebhookFilter);
    }
}

/// <summary>Expression engine used by bulk profile generation and CSV columns.</summary>
public class ExpressionEngineTests
{
    [Fact]
    public void SubstitutesKnownVariables()
    {
        var vars = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["firstName"] = "Ada",
            ["email"] = "ada@example.com",
        };

        Assert.Equal("Ada <ada@example.com>", ExpressionEngine.Evaluate("{firstName} <{email}>", vars));
    }

    [Fact]
    public void LeavesUnknownVariablesEmpty()
    {
        Assert.Equal("[]", ExpressionEngine.Evaluate("[{missing}]"));
    }

    [Fact]
    public void EscapedBracesStayLiteral()
    {
        Assert.Equal("{firstName}", ExpressionEngine.Evaluate("{{firstName}}"));
    }

    [Fact]
    public void RandomIntHasTheRequestedLength()
    {
        for (var i = 0; i < 20; i++)
        {
            var v = ExpressionEngine.Evaluate("{randomInt(6)}");
            Assert.Equal(6, v.Length);
            Assert.True(v.All(char.IsDigit), v);
        }
    }

    [Fact]
    public void AlnumAndAlphaRespectLengthAndAlphabet()
    {
        var alnum = ExpressionEngine.Evaluate("{alnum(12)}");
        Assert.Equal(12, alnum.Length);
        Assert.True(alnum.All(char.IsLetterOrDigit));

        var alpha = ExpressionEngine.Evaluate("{alpha(8)}");
        Assert.Equal(8, alpha.Length);
        Assert.True(alpha.All(char.IsLetter));
    }

    [Fact]
    public void UuidIsA32CharHexString()
    {
        var v = ExpressionEngine.Evaluate("{uuid()}");
        Assert.Equal(32, v.Length);
        Assert.True(v.All(Uri.IsHexDigit));
    }

    [Fact]
    public void EmailUsesTheGivenDomain()
    {
        var v = ExpressionEngine.Evaluate("{email(shop.com)}");
        Assert.EndsWith("@shop.com", v);
        Assert.Contains("@", v);
    }

    [Fact]
    public void RandomStaysInsideTheRange()
    {
        for (var i = 0; i < 50; i++)
        {
            var v = int.Parse(ExpressionEngine.Evaluate("{random(10,20)}"));
            Assert.InRange(v, 10, 19);
        }
    }

    [Fact]
    public void PickReturnsOneOfTheOptions()
    {
        for (var i = 0; i < 30; i++)
        {
            var v = ExpressionEngine.Evaluate("{pick(red,green,blue)}");
            Assert.Contains(v, new[] { "red", "green", "blue" });
        }
    }

    [Fact]
    public void SequenceIncrementsAcrossCalls()
    {
        ExpressionEngine.ResetSequence();
        var a = ExpressionEngine.Evaluate("{sequence(1)}");
        var b = ExpressionEngine.Evaluate("{sequence(1)}");
        var c = ExpressionEngine.Evaluate("{sequence(1)}");

        Assert.Equal("1", a);
        Assert.Equal("2", b);
        Assert.Equal("3", c);
    }

    [Fact]
    public void PadLeftPadsWithZeroes()
    {
        Assert.Equal("0042", ExpressionEngine.Evaluate("{pad(42,4)}"));
    }

    [Fact]
    public void UpperAndLowerTransformTheirArgument()
    {
        Assert.Equal("ABC", ExpressionEngine.Evaluate("{upper(abc)}"));
        Assert.Equal("abc", ExpressionEngine.Evaluate("{lower(ABC)}"));
    }

    [Fact]
    public void VariablesAreListedInOrderWithoutFunctions()
    {
        var vars = ExpressionEngine.Variables("{b}-{a}-{randomInt(4)}-{b}");
        Assert.Equal(new[] { "b", "a" }, vars);
    }

    [Fact]
    public void IsSatisfiedRequiresEveryVariable()
    {
        var template = "{firstName} {lastName}";
        var half = new Dictionary<string, string> { ["firstName"] = "Ada" };
        var full = new Dictionary<string, string> { ["firstName"] = "Ada", ["lastName"] = "L" };

        Assert.False(ExpressionEngine.IsSatisfied(template, half));
        Assert.True(ExpressionEngine.IsSatisfied(template, full));
    }

    [Fact]
    public void EveryBuiltInExampleIsDocumented()
    {
        Assert.NotEmpty(ExpressionEngine.Examples);
        foreach (var e in ExpressionEngine.Examples)
        {
            Assert.False(string.IsNullOrWhiteSpace(e.Key));
            Assert.False(string.IsNullOrWhiteSpace(e.Description));
        }
    }

    [Fact]
    public void UnknownFunctionIsLeftVisible()
    {
        var v = ExpressionEngine.Evaluate("{notAFunction(x)}");
        Assert.Contains("notAFunction", v);
    }
}
