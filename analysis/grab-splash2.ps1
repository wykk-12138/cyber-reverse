param(
    [string]$Exe = 'D:\projects\cyber-reverse\target\Cybersole.exe',
    [string]$WorkDir = 'D:\projects\cyber-reverse\target',
    [string]$Out = 'D:\projects\cyber-reverse\analysis\splash_real.png'
)

# R220c: PrintWindow returns a blank surface for this window (Avalonia/Skia does not render into an arbitrary DC), so
# the splash is brought to the front for the length of one screen grab and then put back.

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public static class Win3 {
    public delegate bool EnumProc(IntPtr h, IntPtr l);

    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();

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

    public static int[] Rect(IntPtr h) {
        RECT r; GetWindowRect(h, out r);
        return new int[] { r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top };
    }
}
'@

$previous = [Win3]::GetForegroundWindow()
$p = Start-Process -FilePath $Exe -WorkingDirectory $WorkDir -PassThru
$hwnd = [IntPtr]::Zero
$t0 = Get-Date

while (((Get-Date) - $t0).TotalMilliseconds -lt 3000) {
    $hwnd = [Win3]::Find([uint32]$p.Id, 400, 700, 400)
    if ($hwnd -ne [IntPtr]::Zero) { break }
    Start-Sleep -Milliseconds 40
}

if ($hwnd -eq [IntPtr]::Zero) { Write-Host 'splash window never appeared'; return }

$r = [Win3]::Rect($hwnd)
Write-Host ("splash {0}x{1} at {2},{3} after {4} ms" -f $r[2], $r[3], $r[0], $r[1], [int]((Get-Date) - $t0).TotalMilliseconds)

# raise it (TOPMOST, no move/resize), grab, then drop the topmost flag back
[Win3]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0001 -bor 0x0002 -bor 0x0010) | Out-Null
[Win3]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 140

$bounds = New-Object System.Drawing.Rectangle($r[0], $r[1], $r[2], $r[3])
$bmp = New-Object System.Drawing.Bitmap($r[2], $r[3])
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

[Win3]::SetWindowPos($hwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0001 -bor 0x0002 -bor 0x0010) | Out-Null
if ($previous -ne [IntPtr]::Zero) { [Win3]::SetForegroundWindow($previous) | Out-Null }

Write-Host "saved=$Out"
