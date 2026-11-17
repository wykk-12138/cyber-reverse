using System.Collections.Specialized;
using System.ComponentModel;
using Cybersole.Helpers;
using Xunit;

namespace Cybersole.Tests;

/// <summary>
/// ObservableDictionary, the one core type in the absence list that needed writing rather than mapping.
///
/// <para>
/// R976. The image declares Cybersole.Helpers.ObservableDictionary`2 with a Count member; nothing in the source declared it
/// under any name, and the BCL has no equivalent -- ObservableCollection takes one parameter and reports changes by index,
/// which is the wrong shape for a dictionary. So substituting a plain Dictionary would not be a rename but a behaviour
/// change, and the kind that surfaces as a view quietly ceasing to update.
/// </para>
/// </summary>
public class ObservableDictionaryTests
{
    /// <summary>Adding a key raises the item-set event with the pair, and the count event separately.</summary>
    [Fact]
    public void AddingRaisesBothKinds()
    {
        var dict = new ObservableDictionary<string, int>();
        var sets = new List<NotifyCollectionChangedEventArgs>();
        var props = new List<string>();

        dict.CollectionChanged += (_, e) => sets.Add(e);
        dict.PropertyChanged += (_, e) => props.Add(e.PropertyName!);

        dict.Add("a", 1);

        Assert.Single(sets);
        Assert.Equal(NotifyCollectionChangedAction.Add, sets[0].Action);
        Assert.Equal(new KeyValuePair<string, int>("a", 1), (KeyValuePair<string, int>)sets[0].NewItems![0]!);

        Assert.Contains("Count", props);
        Assert.Contains("Item[]", props);
    }

    /// <summary>
    /// Replacing an existing key changes a value, not the item set -- so the collection event must not fire. A consumer
    /// rebuilding a view on every assignment would otherwise rebuild it on every edit.
    /// </summary>
    [Fact]
    public void ReplacingAKeyDoesNotRaiseTheSetEvent()
    {
        var dict = new ObservableDictionary<string, int> { ["a"] = 1 };

        var sets = 0;
        var props = new List<string>();
        dict.CollectionChanged += (_, _) => sets++;
        dict.PropertyChanged += (_, e) => props.Add(e.PropertyName!);

        dict["a"] = 2;

        Assert.Equal(0, sets);
        Assert.Contains("Item[]", props);
        Assert.DoesNotContain("Count", props);
        Assert.Equal(2, dict["a"]);
    }

    /// <summary>A removal carries the old pair, because a consumer cannot look it up afterwards.</summary>
    [Fact]
    public void RemovalCarriesTheRemovedPair()
    {
        var dict = new ObservableDictionary<string, int> { ["a"] = 1 };

        NotifyCollectionChangedEventArgs? captured = null;
        dict.CollectionChanged += (_, e) => captured = e;

        Assert.True(dict.Remove("a"));

        Assert.NotNull(captured);
        Assert.Equal(NotifyCollectionChangedAction.Remove, captured!.Action);
        Assert.Equal(new KeyValuePair<string, int>("a", 1), (KeyValuePair<string, int>)captured.OldItems![0]!);
        Assert.Equal(0, dict.Count);
    }

    /// <summary>Removing a key that is absent changes nothing and raises nothing.</summary>
    [Fact]
    public void RemovingAnAbsentKeyIsSilent()
    {
        var dict = new ObservableDictionary<string, int>();
        var raised = 0;
        dict.CollectionChanged += (_, _) => raised++;

        Assert.False(dict.Remove("nope"));
        Assert.Equal(0, raised);
    }

    /// <summary>Clearing raises a reset, and clearing an empty dictionary raises nothing.</summary>
    [Fact]
    public void ClearingRaisesResetOnlyWhenNonEmpty()
    {
        var dict = new ObservableDictionary<string, int>();

        var raised = 0;
        dict.CollectionChanged += (_, _) => raised++;
        dict.Clear();
        Assert.Equal(0, raised);   // clearing an empty dictionary is not a change

        dict["a"] = 1;             // the indexer raises on a new key, so these two are already counted
        dict["b"] = 2;
        var beforeClear = raised;

        dict.Clear();
        Assert.Equal(beforeClear + 1, raised);   // the reset, and nothing else
        Assert.Equal(0, dict.Count);
    }

    /// <summary>A duplicate add throws before any notification, so no consumer sees a change that did not happen.</summary>
    [Fact]
    public void ADuplicateAddThrowsBeforeNotifying()
    {
        var dict = new ObservableDictionary<string, int> { ["a"] = 1 };

        var raised = 0;
        dict.CollectionChanged += (_, _) => raised++;

        Assert.Throws<ArgumentException>(() => dict.Add("a", 2));
        Assert.Equal(0, raised);
        Assert.Equal(1, dict["a"]);
    }

    /// <summary>AddRange skips keys already present and notifies only for the ones that arrived.</summary>
    [Fact]
    public void AddRangeNotifiesOnlyForNewKeys()
    {
        var dict = new ObservableDictionary<string, int> { ["a"] = 1 };

        var sets = new List<NotifyCollectionChangedEventArgs>();
        dict.CollectionChanged += (_, e) => sets.Add(e);

        dict.AddRange(new[]
        {
            new KeyValuePair<string, int>("a", 9),
            new KeyValuePair<string, int>("b", 2),
            new KeyValuePair<string, int>("c", 3),
        });

        Assert.Equal(2, sets.Count);
        Assert.Equal(1, dict["a"]);   // the existing key was not overwritten
        Assert.Equal(2, dict["b"]);
    }

    /// <summary>It is a dictionary first: enumeration, lookup and the interfaces all behave.</summary>
    [Fact]
    public void ItIsADictionary()
    {
        var dict = new ObservableDictionary<string, int> { ["a"] = 1, ["b"] = 2 };

        Assert.Equal(2, dict.Count);
        Assert.True(dict.ContainsKey("a"));
        Assert.False(dict.ContainsKey("z"));
        Assert.Equal(2, dict.Count);
        Assert.Equal(new[] { "a", "b" }, dict.Keys.OrderBy(k => k));

        IReadOnlyDictionary<string, int> readOnly = dict;
        Assert.Equal(2, readOnly["b"]);

        var pairs = new List<KeyValuePair<string, int>>();
        foreach (var pair in dict) pairs.Add(pair);
        Assert.Equal(2, pairs.Count);
    }

    /// <summary>A comparer can be supplied, which matters for keys like hosts that differ only in case.</summary>
    [Fact]
    public void AComparerIsHonoured()
    {
        var dict = new ObservableDictionary<string, int>(StringComparer.OrdinalIgnoreCase) { ["Host"] = 1 };

        Assert.True(dict.ContainsKey("host"));
        Assert.Equal(1, dict["HOST"]);
    }

    /// <summary>Both notification interfaces are declared, because a binding to Count needs the second one.</summary>
    [Fact]
    public void BothInterfacesAreDeclared()
    {
        var type = typeof(ObservableDictionary<string, int>);

        Assert.True(typeof(INotifyCollectionChanged).IsAssignableFrom(type));
        Assert.True(typeof(INotifyPropertyChanged).IsAssignableFrom(type));
        Assert.True(typeof(IDictionary<string, int>).IsAssignableFrom(type));
        Assert.True(typeof(IReadOnlyDictionary<string, int>).IsAssignableFrom(type));
    }
}