// The smallest thing that still pulls in a normal share of the BCL via a console entry point.
//
// R1065: the replica reports 174,293 functions against the original's 277,120, and R1064 established that the ratio
// cannot be read as completeness because the two artifacts inline two different class libraries -- the original is
// .NET 10.0.12 and the replica is .NET 8. This program exists to give the .NET 8 side a number: publish it, count its
// functions, and the framework's contribution to the replica's total stops being a guess.
//
// It deliberately does something rather than nothing. An empty Main would be trimmed down to almost no framework, and
// the baseline would then understate what a real application carries.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;

Console.WriteLine("baseline");

var builder = new StringBuilder();
for (var i = 0; i < 3; i++)
{
    builder.Append(i).Append(',');
}

Console.WriteLine(builder.ToString());

var numbers = Enumerable.Range(0, 10).Select(x => x * 2).Where(x => x % 3 == 0).ToList();
Console.WriteLine(numbers.Count);

var map = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase) { ["a"] = 1 };
Console.WriteLine(map.TryGetValue("A", out var got) ? got : -1);

var payload = JsonSerializer.Serialize(new { ok = true, n = numbers.Count });
Console.WriteLine(payload);

try
{
    using var client = new HttpClient { Timeout = TimeSpan.FromMilliseconds(1) };
    Console.WriteLine(client.BaseAddress?.ToString() ?? "(no base address)");
}
catch (Exception ex)
{
    Console.WriteLine(ex.GetType().Name);
}

Console.WriteLine(DateTimeOffset.UtcNow.Year > 2000 ? "ok" : "clock");
