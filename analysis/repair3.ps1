$ErrorActionPreference='Continue'
function W([string]$m){ $l = "[{0:HH:mm:ss}] {1}" -f (Get-Date), $m; Write-Host $l; Add-Content -Path 'D:\projects\cyber-reverse\analysis\repair3.log' -Value $l -Encoding UTF8 }
Set-Content -Path 'D:\projects\cyber-reverse\analysis\repair3.log' -Value '' -Encoding UTF8
W 'elevated check'
W ((& whoami.exe) -join '')
W ('--- acl before ---')
W ((& icacls.exe 'C:\Users\wykk\scoop\apps\tokensave\current' 2>&1) -join "`n")
W ('--- takeown ---')
W ((& takeown.exe /F 'C:\Users\wykk\scoop\apps\tokensave\current' 2>&1) -join "`n")
W ('--- grant ---')
W ((& icacls.exe 'C:\Users\wykk\scoop\apps\tokensave\current' /grant '*S-1-5-32-544:F' 2>&1) -join "`n")
W ('--- rmdir ---')
W ((& cmd.exe /c rmdir /s /q 'C:\Users\wykk\scoop\apps\tokensave\current' 2>&1) -join "`n")
W ('exists after: ' + (Test-Path 'C:\Users\wykk\scoop\apps\tokensave\current'))
W ('--- parent ---')
W ((& cmd.exe /c rmdir /s /q 'C:\Users\wykk\scoop\apps\tokensave' 2>&1) -join "`n")
W ('parent exists: ' + (Test-Path 'C:\Users\wykk\scoop\apps\tokensave'))
