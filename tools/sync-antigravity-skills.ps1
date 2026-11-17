# 为什么不用 junction：Antigravity 的语言服务器扫描 `.agents/skills/<name>/SKILL.md` 时会跳过
# NTFS junction（实测：新建的 junction 不出现在 GetAllSkills 里，同名的真实目录一秒就出现），
# 而 `.agents/skills.json` 清单在这版 44.9.1 里根本不生效（各种绝对路径形式都试过，零效果）。
# 所以 Antigravity 只能用「真实目录副本」这条路 —— 这个脚本负责把副本刷回源。
#
# 用法：
#   powershell -File tools\sync-antigravity-skills.ps1            # 同步
#   powershell -File tools\sync-antigravity-skills.ps1 -DryRun    # 只看差异，不动文件
#
# 证据见 .agents/README-antigravity.md「实测记录」一节。

[CmdletBinding()]
param([switch]$DryRun)

$ErrorActionPreference = 'Stop'

# 源 → 目标名。目标目录名必须等于 skill 名（Antigravity 用目录名做标识）。
$map = [ordered]@{
  'ida-reverse'                      = 'D:\projects\Seep-Reverse-Lab\Tool\skill\ida-reverse'
  'softseep'                         = 'D:\projects\Seep-Reverse-Lab\Tool\skill\softseep'
  'client-license-validation-bypass' = 'D:\projects\Seep-Reverse-Lab\Tool\skill\client-license-validation-bypass'
  'reverse-engineering'              = 'D:\projects\Seep-Reverse-Lab\Tool\skill\safe-skills\reverse-engineering'
  'radare2'                          = 'D:\projects\Seep-Reverse-Lab\Tool\skill\safe-skills\radare2'
  'cua-driver'                       = 'C:\Users\wykk\.cua-driver\skills\cua-driver'
}

$root = Join-Path $PSScriptRoot '..\.agents\skills'
$root = [System.IO.Path]::GetFullPath($root)

$changed = 0
$missing = 0

foreach ($name in $map.Keys) {
  $src = $map[$name]
  if (-not (Test-Path $src)) {
    Write-Warning "源不存在，跳过：$name  ($src)"
    $missing++
    continue
  }
  $dst = Join-Path $root $name

  $srcFiles = Get-ChildItem $src -Recurse -File -Force
  $dstFiles = if (Test-Path $dst) { Get-ChildItem $dst -Recurse -File -Force } else { @() }

  $srcIndex = @{}
  foreach ($f in $srcFiles) {
    $rel = $f.FullName.Substring($src.Length).TrimStart('\')
    $srcIndex[$rel] = $f
  }
  $dstIndex = @{}
  foreach ($f in $dstFiles) {
    $rel = $f.FullName.Substring($dst.Length).TrimStart('\')
    $dstIndex[$rel] = $f
  }

  $diff = @()
  foreach ($rel in $srcIndex.Keys) {
    if (-not $dstIndex.ContainsKey($rel)) { $diff += "  + $rel"; continue }
    $a = $srcIndex[$rel]; $b = $dstIndex[$rel]
    if ($a.Length -ne $b.Length -or $a.LastWriteTimeUtc -ne $b.LastWriteTimeUtc) { $diff += "  ~ $rel" }
  }
  foreach ($rel in $dstIndex.Keys) {
    if (-not $srcIndex.ContainsKey($rel)) { $diff += "  - $rel" }
  }

  if ($diff.Count -eq 0) {
    Write-Host "same     $name"
    continue
  }

  $changed++
  Write-Host "differ   $name  ($($diff.Count) 处)"
  $diff | Select-Object -First 10 | ForEach-Object { Write-Host $_ }
  if ($diff.Count -gt 10) { Write-Host "  … 另有 $($diff.Count - 10) 处" }

  if (-not $DryRun) {
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    New-Item -ItemType Directory -Path $dst -Force | Out-Null
    Copy-Item (Join-Path $src '*') $dst -Recurse -Force
    if (-not (Test-Path (Join-Path $dst 'SKILL.md'))) {
      throw "复制后仍缺 SKILL.md：$dst"
    }
  }
}

Write-Host ''
Write-Host ("源缺失 {0} 个；本次{1} {2} 个。" -f $missing, $(if ($DryRun) { '发现差异' } else { '重写' }), $changed)

# 判据：让语言服务器重算一次，确认工作区 skill 都还在。
# 端口/令牌从 ~/.gemini/antigravity/daemon/hub_*.json 里取（最新写入的那个）。
if (-not $DryRun) {
  $hubDir = Join-Path $env:USERPROFILE '.gemini\antigravity\daemon'
  $hub = Get-ChildItem $hubDir -Filter 'hub_*.json' -ErrorAction SilentlyContinue |
         Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($hub) {
    $meta = Get-Content $hub.FullName -Raw | ConvertFrom-Json
    $uri = 'file:///' + ($root -replace '\\', '/' -replace '/\.agents/skills$', '')
    $body = @{ workspaceUris = @($uri) } | ConvertTo-Json -Compress
    try {
      $r = Invoke-RestMethod -Uri ("http://localhost:{0}/exa.language_server_pb.LanguageServerService/GetAllSkills" -f $meta.httpPort) `
        -Method Post -ContentType 'application/json' `
        -Headers @{ 'x-codeium-csrf-token' = $meta.csrfToken } -Body $body -TimeoutSec 20
      $ws = @($r.skills | Where-Object { $_.path -notmatch '\.gemini\\antigravity\\builtin' } | ForEach-Object { $_.name })
      $expect = @($map.Keys) + @('antigravity-tool-map')
      $absent = @($expect | Where-Object { $ws -notcontains $_ })
      Write-Host ("语言服务器看到的工作区 skill：{0}" -f ($ws -join ', '))
      if ($absent.Count -gt 0) {
        Write-Warning ("没被加载：{0}（Antigravity 可能没开，或该工作区没在活动）" -f ($absent -join ', '))
        exit 1
      }
      Write-Host 'VERDICT: all workspace skills loaded'
    } catch {
      Write-Warning "RPC 校验失败（不影响文件已同步）：$($_.Exception.Message)"
      exit 2
    }
  } else {
    Write-Warning "找不到 daemon/hub_*.json，跳过 RPC 校验"
  }
}
