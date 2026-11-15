param(
    [string]$Exe = 'D:\projects\cyber-reverse\target\Cybersole.exe',
    [string]$WorkDir = 'D:\projects\cyber-reverse\target',
    [string]$OutDir = 'D:\projects\cyber-reverse\analysis\shots'
)

# R220: capture the original's start-up splash. It lives about half a second and it is 529x630, so the only way to see
# it is to screenshot the screen continuously from the moment the process starts and crop the small window out.

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class Win {
    public delegate bool EnumProc(IntPtr h, IntPtr l);

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);

    public struct RECT { public int Left, Top, Right, Bottom; }

    public static List<string> Rects(uint pid) {
        var list = new List<string>();
        EnumWindows((h, l) => {
            uint p; GetWindowThreadProcessId(h, out p);
            if (p != pid) return true;
            var sb = new StringBuilder(256); GetWindowTextW(h, sb, 256);
            var title = sb.ToString();
            if (title.Length == 0) return true;
            RECT r; GetWindowRect(h, out r);
            list.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}",
                h.ToInt64(), IsWindowVisible(h) ? 1 : 0, r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top, title));
            return true;
        }, IntPtr.Zero);
        return list;
    }
}
'@

if (Test-Path $OutDir) { Remove-Item $OutDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutDir | Out-Null

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$log = Join-Path $OutDir 'rects.txt'
Set-Content -Path $log -Value '# ms | hwnd | visible | left | top | width | height' -Encoding UTF8

$p = Start-Process -FilePath $Exe -WorkingDirectory $WorkDir -PassThru
$t0 = Get-Date
$shot = 0

for ($i = 0; $i -lt 26; $i++) {
    $ms = [int]((Get-Date) - $t0).TotalMilliseconds

    foreach ($r in [Win]::Rects([uint32]$p.Id)) {
        Add-Content -Path $log -Value ("{0,5} | {1}" -f $ms, $r) -Encoding UTF8
    }

    $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $file = Join-Path $OutDir ("shot{0:d2}_{1:d4}ms.png" -f $shot, $ms)
    $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    $shot++

    Start-Sleep -Milliseconds 90
}

Write-Host "pid=$($p.Id) shots=$shot"
Get-Content $log | Select-Object -First 60
