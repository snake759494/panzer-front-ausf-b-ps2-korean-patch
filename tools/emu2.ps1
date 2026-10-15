# 백그라운드 PCSX2 조작: 포커스를 뺏지 않고 키 메시지 전송, PrintWindow로 캡처
param([string]$cmd, [string]$arg)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $root 'work\pcsx2pf\pcsx2-pf.exe'
$pidf = Join-Path $PSScriptRoot 'emu.pid'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Collections.Generic;
public class B {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint c, uint t);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static List<IntPtr> Kids(IntPtr p) { var l = new List<IntPtr>(); EnumChildWindows(p, (h, x) => { l.Add(h); return true; }, IntPtr.Zero); return l; }
}
"@
function Main { if (-not (Test-Path $pidf)) { throw 'not running' }; $p = Get-Process -Id ([int](Get-Content $pidf)) -ErrorAction Stop; $p.Refresh(); $p.MainWindowHandle }
switch ($cmd) {
  'start' {
    $al = @('-batch', '-nogui'); if ($env:EMU_STATE) { $al += @('-statefile', "`"$env:EMU_STATE`"") }; $al += "`"$arg`""
    $p = Start-Process -FilePath $exe -ArgumentList $al -PassThru -WindowStyle Minimized
    Set-Content $pidf $p.Id
    for ($i = 0; $i -lt 100; $i++) { Start-Sleep -Milliseconds 200; $p.Refresh(); if ($p.MainWindowHandle -ne 0) { break } }
    Start-Sleep -Milliseconds 500; $p.Refresh(); $h = $p.MainWindowHandle
    [B]::ShowWindow($h, 4) | Out-Null
    [B]::SetWindowPos($h, [IntPtr]1, 100, 100, 656, 519, 0x0010) | Out-Null   # HWND_BOTTOM, SWP_NOACTIVATE
    Write-Output "started $($p.Id)"
  }
  'stop' { if (Test-Path $pidf) { Get-Process -Id ([int](Get-Content $pidf)) -ErrorAction SilentlyContinue | Stop-Process -Force; Remove-Item $pidf }; 'stopped' }
  'key' {
    $parts = $arg.Split(','); $vk = [Convert]::ToUInt32($parts[0], 16); $ms = if ($parts.Length -gt 1) { [int]$parts[1] } else { 150 }
    $h = Main; $sc = [B]::MapVirtualKey($vk, 0); $ext = if ($vk -ge 0x21 -and $vk -le 0x2E) { 0x1000000 } else { 0 }
    $ld = [IntPtr](1 -bor ($sc -shl 16) -bor $ext); $lu = [IntPtr]([int64](1 -bor ($sc -shl 16) -bor $ext) -bor 0xC0000000)
    $ws = @($h) + [B]::Kids($h)
    foreach ($w in $ws) { [B]::PostMessage($w, 0x100, [IntPtr]$vk, $ld) | Out-Null }
    Start-Sleep -Milliseconds $ms
    foreach ($w in $ws) { [B]::PostMessage($w, 0x101, [IntPtr]$vk, $lu) | Out-Null }
    "key $($parts[0])"
  }
  'shot' {
    $dir = Join-Path $root 'work\pcsx2pf\snaps'; Get-ChildItem $dir -Filter *.png | Remove-Item
    & $PSCommandPath key '7B,80' | Out-Null
    for ($i = 0; $i -lt 50; $i++) { Start-Sleep -Milliseconds 200; $f = Get-ChildItem $dir -Filter *.png | Select-Object -First 1; if ($f -and $f.Length -gt 0) { break } }
    for ($j = 0; $j -lt 20; $j++) { Start-Sleep -Milliseconds 300; try { Move-Item $f.FullName $arg -Force -ErrorAction Stop; break } catch {} }; "saved $arg"
  }

}
