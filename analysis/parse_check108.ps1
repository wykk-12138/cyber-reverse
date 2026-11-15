$ErrorActionPreference = 'Stop'
$path = 'D:\projects\cyber-reverse\replica\tools\verify.ps1'
$tokens = $null
$errors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors)
if ($errors -and $errors.Count -gt 0) {
    $errors | ForEach-Object { "PARSE ERROR: " + $_.Message + " @ line " + $_.Extent.StartLineNumber }
} else {
    "PARSE OK"
}
