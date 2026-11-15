$sample = @"
[xUnit.net 00:00:07.49]     Cybersole.Tests.NonParityClaimsTests.TheSecureTokenRotatesWithinSeventySeconds [FAIL]
  失败 Cybersole.Tests.OwnTlsFallbackTests.AHundredTimesCallerStillGreen [12 ms]
"@

$names = ($sample -split "`r?`n" |
          ForEach-Object {
              if ($_ -match '(Cybersole\.Tests\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+)') { $Matches[1] }
          } | Select-Object -Unique)

"count=" + $names.Count
$names | ForEach-Object { "  name: $_" }

$flaked = @()
foreach ($name in $names) {
    if (-not $name) { continue }
    $flaked += "flaked in the set, green alone: $name"
}
"flaked entries: " + $flaked.Count
$exitProbe = if ($flaked | Where-Object { $_ -like 'still failing alone:*' }) { 1 } else { 0 }
"exitProbe=" + $exitProbe
