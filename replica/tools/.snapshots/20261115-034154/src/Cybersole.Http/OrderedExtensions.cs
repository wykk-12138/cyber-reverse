using System.Collections;

namespace Cybersole.Http;

/// <summary>
/// Insertion-ordered dictionary used for TLS extensions. BouncyCastle writes the
/// ClientHello extensions in enumeration order, so this is what lets us match a
/// browser's extension ordering (the third component of a JA3 hash).
/// </summary>
public sealed class OrderedExtensions : IDictionary<int, byte[]>
{
    private readonly List<int> _order = new();
    private readonly Dictionary<int, byte[]> _map = new();

    public byte[] this[int key]
    {
        get => _map[key];
        set
        {
            if (!_map.ContainsKey(key)) _order.Add(key);
            _map[key] = value;
        }
    }

    public ICollection<int> Keys => _order.AsReadOnly();
    public ICollection<byte[]> Values => _order.Select(k => _map[k]).ToList();
    public int Count => _map.Count;
    public bool IsReadOnly => false;

    public void Add(int key, byte[] value)
    {
        if (_map.ContainsKey(key)) throw new ArgumentException($"duplicate extension 0x{key:X4}");
        _map[key] = value;
        _order.Add(key);
    }

    public void Add(KeyValuePair<int, byte[]> item) => Add(item.Key, item.Value);
    public bool ContainsKey(int key) => _map.ContainsKey(key);
    public bool Remove(int key)
    {
        if (!_map.Remove(key)) return false;
        _order.Remove(key);
        return true;
    }

    public bool TryGetValue(int key, out byte[] value) => _map.TryGetValue(key, out value!);

    public bool Contains(KeyValuePair<int, byte[]> item)
        => _map.TryGetValue(item.Key, out var v) && ReferenceEquals(v, item.Value);

    public bool Remove(KeyValuePair<int, byte[]> item)
        => Contains(item) && Remove(item.Key);

    public void AddRange(IEnumerable<KeyValuePair<int, byte[]>> items)
    {
        foreach (var kv in items) this[kv.Key] = kv.Value;
    }

    public void Clear()
    {
        _map.Clear();
        _order.Clear();
    }

    public void CopyTo(KeyValuePair<int, byte[]>[] array, int arrayIndex)
    {
        foreach (var k in _order) array[arrayIndex++] = new KeyValuePair<int, byte[]>(k, _map[k]);
    }

    public IEnumerator<KeyValuePair<int, byte[]>> GetEnumerator()
    {
        foreach (var k in _order) yield return new KeyValuePair<int, byte[]>(k, _map[k]);
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
