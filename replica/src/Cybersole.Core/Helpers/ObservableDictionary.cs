namespace Cybersole.Helpers;

using System.Collections;
using System.Collections.Specialized;
using System.ComponentModel;

/// <summary>
/// A dictionary that raises change notifications, which is what the original has and the replica did not.
///
/// <para>
/// R976. <c>Cybersole.Helpers.ObservableDictionary`2</c> was the one core type in the absence list that was neither a
/// rename nor UI: no declaration under any name anywhere in the source, and no BCL equivalent -- the framework offers
/// <c>ObservableCollection&lt;T&gt;</c> with one parameter and nothing of this shape. So it is written rather than
/// classified away.
/// </para>
///
/// <para>
/// <b>Why a dictionary needs notifications at all.</b> A collection can report "something changed" by index. A dictionary
/// cannot: adding or removing a key changes the item set while leaving every other key where it was, so a consumer that
/// caches by position has nothing to diff. That is why the original carries one and why a plain
/// <c>Dictionary&lt;TKey,TValue&gt;</c> substituted for it is not a rename but a behaviour change -- and it is the kind that
/// shows up as a view that stops updating rather than as an exception.
/// </para>
///
/// <para>
/// The notifications are the two the framework defines for this purpose: <see cref="INotifyCollectionChanged"/> for the item
/// set and <see cref="INotifyPropertyChanged"/> for <c>Count</c> and the indexer, because a binding to either wants to be
/// told separately from a binding to the set.
/// </para>
/// </summary>
public sealed class ObservableDictionary<TKey, TValue> :
    IDictionary<TKey, TValue>,
    INotifyCollectionChanged,
    INotifyPropertyChanged,
    IReadOnlyDictionary<TKey, TValue>
    where TKey : notnull
{
    private readonly Dictionary<TKey, TValue> _inner;

    public ObservableDictionary() => _inner = new Dictionary<TKey, TValue>();

    public ObservableDictionary(IEqualityComparer<TKey> comparer) => _inner = new Dictionary<TKey, TValue>(comparer);

    /// <summary>Raised when the item set changes: an add, an insert over an existing key, a remove or a clear.</summary>
    public event NotifyCollectionChangedEventHandler? CollectionChanged;

    /// <summary>Raised for <c>Count</c> and for the indexer, separately from the set.</summary>
    public event PropertyChangedEventHandler? PropertyChanged;

    // ── reads ────────────────────────────────────────────────────────────────

    public int Count => _inner.Count;

    public bool IsReadOnly => false;

    public TValue this[TKey key]
    {
        get => _inner[key];
        set
        {
            var existed = _inner.ContainsKey(key);
            _inner[key] = value;

            // replacing an existing key changes a value, not the item set -- so only the indexer is notified
            if (existed)
            {
                RaisePropertyChanged("Item[]");
                return;
            }

            RaiseCollectionChanged(NotifyCollectionChangedAction.Add,
                new KeyValuePair<TKey, TValue>(key, value));
            RaisePropertyChanged("Count");
            RaisePropertyChanged("Item[]");
        }
    }

    public ICollection<TKey> Keys => _inner.Keys;

    public ICollection<TValue> Values => _inner.Values;

    IEnumerable<TKey> IReadOnlyDictionary<TKey, TValue>.Keys => _inner.Keys;

    IEnumerable<TValue> IReadOnlyDictionary<TKey, TValue>.Values => _inner.Values;

    public bool ContainsKey(TKey key) => _inner.ContainsKey(key);

    public bool TryGetValue(TKey key, out TValue value) => _inner.TryGetValue(key, out value!);

    // ── writes ───────────────────────────────────────────────────────────────

    public void Add(TKey key, TValue value)
    {
        _inner.Add(key, value);   // throws on a duplicate key, as a dictionary should, before any notification
        RaiseCollectionChanged(NotifyCollectionChangedAction.Add, new KeyValuePair<TKey, TValue>(key, value));
        RaisePropertyChanged("Count");
        RaisePropertyChanged("Item[]");
    }

    public void Add(KeyValuePair<TKey, TValue> item) => Add(item.Key, item.Value);

    public bool Remove(TKey key)
    {
        if (!_inner.TryGetValue(key, out var value)) return false;

        _inner.Remove(key);
        // the removed pair is carried in the event: a consumer cannot look it up afterwards
        RaiseCollectionChanged(NotifyCollectionChangedAction.Remove, new KeyValuePair<TKey, TValue>(key, value));
        RaisePropertyChanged("Count");
        RaisePropertyChanged("Item[]");
        return true;
    }

    public bool Remove(KeyValuePair<TKey, TValue> item) =>
        _inner.TryGetValue(item.Key, out var existing) && EqualityComparer<TValue>.Default.Equals(existing, item.Value) &&
        Remove(item.Key);

    public void Clear()
    {
        if (_inner.Count == 0) return;

        _inner.Clear();
        RaiseCollectionChanged(NotifyCollectionChangedAction.Reset, default);
        RaisePropertyChanged("Count");
        RaisePropertyChanged("Item[]");
    }

    public void AddRange(IEnumerable<KeyValuePair<TKey, TValue>> items)
    {
        // batched so a consumer rebuilding its view once does not rebuild it per item
        var added = new List<KeyValuePair<TKey, TValue>>();
        foreach (var item in items)
            if (!_inner.ContainsKey(item.Key))
            {
                _inner[item.Key] = item.Value;
                added.Add(item);
            }

        if (added.Count == 0) return;

        foreach (var item in added)
            RaiseCollectionChanged(NotifyCollectionChangedAction.Add, item);
        RaisePropertyChanged("Count");
        RaisePropertyChanged("Item[]");
    }

    // ── copy and enumerate ───────────────────────────────────────────────────

    public void CopyTo(KeyValuePair<TKey, TValue>[] array, int arrayIndex) =>
        ((ICollection<KeyValuePair<TKey, TValue>>)_inner).CopyTo(array, arrayIndex);

    public bool Contains(KeyValuePair<TKey, TValue> item) =>
        ((ICollection<KeyValuePair<TKey, TValue>>)_inner).Contains(item);

    public IEnumerator<KeyValuePair<TKey, TValue>> GetEnumerator() => _inner.GetEnumerator();

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    private void RaiseCollectionChanged(NotifyCollectionChangedAction action, KeyValuePair<TKey, TValue>? item) =>
        CollectionChanged?.Invoke(this, item is { } pair
            ? new NotifyCollectionChangedEventArgs(action, pair)
            : new NotifyCollectionChangedEventArgs(action));

    private void RaisePropertyChanged(string name) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}