param(
    [string]$Exe = 'D:\projects\cyber-reverse\target\Cybersole.exe',
    [string]$WorkDir = 'D:\projects\cyber-reverse\target',
    [string]$Out = 'D:\projects\cyber-reverse\analysis\splash_real.png'
)

# R220b: PrintWindow with PW_RENDERFULLCONTENT grabs a window's own pixels even when it is covered — the earlier
# screen-capture attempts only ever produced the windows on top of the splash.

Add-Type -AssemblyName System.Drawing

Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class Win2 {
    public delegate bool EnumProc(IntPtr h, IntPtr l);

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);

    public struct RECT { public int Left, Top, Right, Bottom; }

    public static IntPtr Find(uint pid, int minW, int maxW, int minH) {
        IntPtr found = IntPtr.Zero;
        EnumWindows((h, l) => {
            uint p; GetWindowThreadProcessId(h, out p);
            if (p != pid || !IsWindowVisible(h)) return true;
            RECT r; GetWindowRect(h, out r);
            int w = r.Right - r.Left, ht = r.Bottom - r.Top;
            if (w >= minW && w <= maxW && ht >= minH) { found = h; return false; }
            return true;
        }, IntPtr.Zero);
        return found;
    }

    public static string Size(IntPtr h) {
        RECT r; GetWindowRect(h, out r);
        return (r.Right - r.Left) + "x" + (r.Bottom - r.Top);
    }
}
'@

$p = Start-Process -FilePath $Exe -WorkingDirectory $WorkDir -PassThru
$hwnd = [IntPtr]::Zero
$t0 = Get-Date

while (((Get-Date) - $t0).TotalMilliseconds -lt 3000) {
    $hwnd = [Win2]::Find([uint32]$p.Id, 400, 700, 400)
    if ($hwnd -ne [IntPtr]::Zero) { break }
    Start-Sleep -Milliseconds 50
}

if ($hwnd -eq [IntPtr]::Zero) { Write-Host 'splash window never appeared'; return }

$size = [Win2]::Size($hwnd)
Write-Host "splash hwnd=$($hwnd) size=$size at $([int]((Get-Date)-$t0).TotalMilliseconds) ms"

$parts = $size.Split('x')
$bmp = New-Object System.Drawing.Bitmap([int]$parts[0], [int]$parts[1])
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [Win2]::PrintWindow($hwnd, $hdc, 2)   # PW_RENDERFULLCONTENT
$g.ReleaseHdc($hdc)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Host "PrintWindow=$ok saved=$Out"
