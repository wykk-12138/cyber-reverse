# clean-temp.ps1 — remove the browser profiles and probe shells this workspace leaves in %TEMP%.
#
# R130: YG found 115 cyb-chromium-* profile folders and 14 cyb-missing-* shells in %TEMP%. Both are
# this project's own artifacts (ChromiumBridge names its user-data-dir cyb-chromium-<8 hex>;
# CheckoutStats used to create cyb-missing-<32 hex> and write "[]"). They are not the original's —
# Cybersole keeps its profiles under its own data folder — so they are safe to delete, and deleting
# them is the only reason C: was running out of room.
param(
    [int]$OlderThanHours = 0,
    [switch]$WhatIfOnly
)

$temp = [System.IO.Path]::GetTempPath()
$patterns = @('cyb-chromium-*', 'cyb-missing-*', 'cyb-bad-*')
$cutoff = (Get-Date).AddHours(-$OlderThanHours)

$removed = 0
$bytes = 0

foreach ($pattern in $patterns) {
    foreach ($dir in Get-ChildItem $temp -Directory -Filter $pattern -ErrorAction SilentlyContinue) {
        if ($dir.LastWriteTime -gt $cutoff) { continue }
        $size = (Get-ChildItem $dir.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object Length -Sum).Sum
        if ($WhatIfOnly) {
            "{0}  {1} MB" -f $dir.Name, [math]::Round($size / 1MB, 1)
        } else {
            Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
        $removed++
        $bytes += [int64]$size
    }
}

if ($WhatIfOnly) {
    "{0} folder(s), {1} MB" -f $removed, [math]::Round($bytes / 1MB, 1)
} else {
    "removed {0} folder(s), {1} MB" -f $removed, [math]::Round($bytes / 1MB, 1)
}
