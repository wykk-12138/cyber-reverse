using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Input;
using Cybersole.Core.Models;
using Cybersole.Core.Settings;
using Cybersole.Ui.Views.Monitor;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// R434: the five commands the original binds on MonitorView are binding targets (Getter/Setter/Property
/// descriptors all present, addresses in <c>docs/R434_DECISIONS.md</c> §0), so "the command acts on the
/// current selection" is a structural reading. Two of them have model evidence and are implemented for
/// real; three have no behavioural evidence and are explicit, inert-by-default hooks.
///
/// <para>
/// What these tests pin: the two observable ones do what the binding table implies, and the three hooks
/// never pretend to succeed — with no hook supplied they perform no side effect, and whether or not one is
/// supplied they always hand over the event that was selected <b>at that moment</b>.
/// </para>
/// </summary>
public sealed class MonitorViewCommandTests
{
    private readonly ITestOutputHelper _out;

    public MonitorViewCommandTests(ITestOutputHelper output) => _out = output;

    private static MonitorEvent Event(string name, string? store = "nike", string? type = "restock") =>
        new() { Name = name, Store = store, Type = type, Timestamp = new DateTime(2026, 11, 14, 9, 30, 0, DateTimeKind.Utc) };

    // ---- constraint 1: the two that have model evidence are implemented for real ----

    [Fact]
    public void View_ShowsDetailOfSelectedEvent()
    {
        var view = new MonitorView();
        var selected = Event("Air Max 90");
        view.SelectedEvent = selected;

        Assert.False(view.DetailVisible);

        view.View.Execute(null);

        Assert.True(view.DetailVisible);
        Assert.Equal(MonitorView.DetailLine(selected), view.DetailText);
        _out.WriteLine(view.DetailText);
    }

    [Fact]
    public void View_WithoutSelection_ShowsNoDetail()
    {
        var view = new MonitorView();

        view.View.Execute(null);

        Assert.False(view.DetailVisible);
        Assert.Equal(string.Empty, view.DetailText);
    }

    [Fact]
    public void OpenFilter_SurfacesSettingsInstance()
    {
        var settings = new GlobalSettings();
        settings.MonitorFilters.Supreme = false;          // a value the page must be able to see
        var view = new MonitorView(settings);

        Assert.False(view.FilterExposed);
        Assert.Same(settings.MonitorFilters, view.Filters);

        view.OpenFilter.Execute(null);

        Assert.True(view.FilterExposed);
        Assert.Same(settings.MonitorFilters, view.Filters);
        Assert.False(view.Filters.Supreme);
    }

    [Fact]
    public void OpenFilter_FallsBackToLocalFiltersWhenNoSettings()
    {
        var view = new MonitorView();

        view.OpenFilter.Execute(null);

        Assert.True(view.FilterExposed);
        Assert.NotNull(view.Filters);
    }

    // ---- constraint 2: the three hooks must not pretend to succeed ----

    [Fact]
    public void Hooks_WithNoDelegate_ProduceNoSideEffectAndRecordWhy()
    {
        foreach (var claim in new[] { "C-monitor-openurl", "C-monitor-linkchange", "C-monitor-quicktask" })
        {
            var view = new MonitorView();
            view.SelectedEvent = Event("Dunk Low");
            var command = HooksOf(view).First(pair => pair.Claim == claim).Command;

            command.Execute(null);

            Assert.Equal(claim, view.LastHookClaim);
            Assert.Contains("structure only", view.LastHookNote);
            Assert.Single(view.HookTargets);
            Assert.Null(view.OpenUrlHook);
            Assert.Null(view.LinkChangeHook);
            Assert.Null(view.QuicktaskHook);
        }
    }

    [Fact]
    public void Hooks_HandOverTheEventSelectedAtThatMoment()
    {
        var view = new MonitorView();
        var first = Event("first");
        var second = Event("second");
        var received = new List<string>();

        view.OpenUrlHook = e => received.Add(e.Name);
        view.LinkChangeHook = e => received.Add(e.Name);
        view.QuicktaskHook = e => received.Add(e.Name);

        view.SelectedEvent = first;
        view.OpenUrl.Execute(null);
        view.SelectedEvent = second;
        view.Quicktask.Execute(null);
        view.LinkChange.Execute(null);

        Assert.Equal(new[] { "first", "second", "second" }, received);
        Assert.Equal(new[] { "first", "second", "second" }, view.HookTargets.Select(e => e.Name).ToArray());
        Assert.All(new[] { first, second }, e => Assert.Contains(e, view.HookTargets));
        Assert.Null(view.LastHookClaim);
    }

    [Fact]
    public void Hooks_WithNoSelection_DoNothingAndSaySo()
    {
        var view = new MonitorView();
        var called = 0;
        view.OpenUrlHook = _ => called++;

        view.OpenUrl.Execute(null);

        Assert.Equal(0, called);
        Assert.Equal("no selection", view.LastHookNote);
        Assert.Equal("C-monitor-openurl", view.LastHookClaim);
        Assert.Empty(view.HookTargets);
    }

    [Fact]
    public void AllFiveCommandsAreBound_ICommandProperties()
    {
        var view = new MonitorView();
        foreach (var name in new[] { nameof(MonitorView.View), nameof(MonitorView.OpenFilter),
                                     nameof(MonitorView.OpenUrl), nameof(MonitorView.LinkChange),
                                     nameof(MonitorView.Quicktask) })
        {
            var property = typeof(MonitorView).GetProperty(name);
            Assert.NotNull(property);
            Assert.True(typeof(ICommand).IsAssignableFrom(property!.PropertyType), name + " must be ICommand");
            Assert.NotNull(property.GetValue(view));
        }
    }

    [Fact]
    public void SetEvents_MakesFirstRowTheSelection_AndDetailFollowsIt()
    {
        var view = new MonitorView();
        var a = Event("a");
        var b = Event("b");

        view.SetEvents(new[] { a, b });
        Assert.Same(a, view.SelectedEvent);

        view.SelectedEvent = b;
        view.View.Execute(null);

        Assert.Equal(MonitorView.DetailLine(b), view.DetailText);
        Assert.Contains("b", view.DetailText);
    }

    private static IEnumerable<(ICommand Command, string Claim)> HooksOf(MonitorView view)
    {
        yield return (view.OpenUrl, "C-monitor-openurl");
        yield return (view.LinkChange, "C-monitor-linkchange");
        yield return (view.Quicktask, "C-monitor-quicktask");
    }
}
