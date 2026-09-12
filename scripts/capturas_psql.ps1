<#
capturas_psql.ps1 - Toma capturas de pantalla reales de sesiones psql (Windows).
Abre una ventana de Windows Terminal, ejecuta las consultas con psql y captura solo esa ventana.
La contrasena se lee de la variable de entorno PGPASSWORD (por defecto la de laboratorio, huerto_dev).

Uso (PowerShell, desde la raiz del repositorio, con sesion de escritorio activa):
  .\scripts\capturas_psql.ps1
Requiere: cliente psql (por defecto C:\Program Files\PostgreSQL\17\bin\psql.exe) y Windows Terminal (wt.exe).
#>
param(
    [string]$Psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe",
    [string]$Salida = (Join-Path $PSScriptRoot "..\docs\evidencia\img")
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class W32 {
  public delegate bool EW(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EW cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool repaint);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr wp, IntPtr lp);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
  public struct RECT { public int Left, Top, Right, Bottom; }
  public static List<IntPtr> PorPrefijo(string prefijo) {
    var lista = new List<IntPtr>();
    EnumWindows((h, l) => {
      if (!IsWindowVisible(h)) return true;
      var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
      if (sb.ToString().StartsWith(prefijo)) lista.Add(h);
      return true; }, IntPtr.Zero);
    return lista;
  }
}
"@
if (-not $env:PGPASSWORD) { $env:PGPASSWORD = "huerto_dev" }
$Salida = (Resolve-Path $Salida).Path
$PREFIJO = "psql - "

function Cerrar-Ventanas([string]$prefijo) {
    foreach ($h in [W32]::PorPrefijo($prefijo)) { [W32]::PostMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
    Start-Sleep -Seconds 1
}

function Captura([string]$Nombre, [int]$Puerto, [string]$Titulo, [string[]]$Comandos, [int]$Cols = 150, [int]$Lineas = 44, [int]$Alto = 950) {
    $tmp = Join-Path $env:TEMP "captura_psql.sql"
    Set-Content -Path $tmp -Value ($Comandos -join "`r`n") -Encoding ASCII
    $cmdLine = "/k chcp 65001 >nul && `"$Psql`" -h 127.0.0.1 -p $Puerto -U huerto_app -d huerto_db -P pager=off -f `"$tmp`""
    Start-Process wt.exe -ArgumentList "-w new --size $Cols,$Lineas --title `"$Titulo`" --suppressApplicationTitle cmd $cmdLine" | Out-Null
    $h = [IntPtr]::Zero
    for ($i = 0; $i -lt 40 -and $h -eq [IntPtr]::Zero; $i++) {
        Start-Sleep -Milliseconds 500
        $lista = [W32]::PorPrefijo($Titulo)
        if ($lista.Count -gt 0) { $h = $lista[0] }
    }
    if ($h -eq [IntPtr]::Zero) { Write-Warning "sin ventana para $Nombre"; return }
    Start-Sleep -Seconds 4                      # tiempo para que psql termine de imprimir
    [W32]::MoveWindow($h, 0, 0, 1500, $Alto, $true) | Out-Null
    [W32]::SetForegroundWindow($h) | Out-Null
    Start-Sleep -Milliseconds 800
    $r = New-Object W32+RECT
    # limites visibles reales (sin el marco invisible que agrega el escritorio de Windows)
    if ([W32]::DwmGetWindowAttribute($h, 9, [ref]$r, 16) -ne 0) { [W32]::GetWindowRect($h, [ref]$r) | Out-Null }
    $bmp = New-Object System.Drawing.Bitmap ($r.Right - $r.Left), ($r.Bottom - $r.Top)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size)
    $ruta = Join-Path $Salida $Nombre
    $bmp.Save($ruta, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    [W32]::PostMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null   # WM_CLOSE
    Start-Sleep -Seconds 1
    Write-Host "[captura] $Nombre"
}

Cerrar-Ventanas $PREFIJO   # ventanas sobrantes de corridas anteriores

# 1) PostgreSQL 16 (Docker, puerto 5436): conexion, tablas y conteos
Captura "14_psql_docker_tablas.png" 5436 "psql - PostgreSQL 16 (Docker 5436) - tablas y conteos" @(
  "\conninfo",
  "SELECT version();",
  "\dt",
  "SELECT 'zona' AS entidad, count(*) AS registros FROM zona UNION ALL SELECT 'variable', count(*) FROM variable UNION ALL SELECT 'sensor', count(*) FROM sensor UNION ALL SELECT 'umbral', count(*) FROM umbral UNION ALL SELECT 'lectura', count(*) FROM lectura UNION ALL SELECT 'alerta', count(*) FROM alerta UNION ALL SELECT 'anotacion', count(*) FROM anotacion;"
)

# 1b) PostgreSQL 16 (Docker): estructura de lectura y anotacion (llaves, CHECK, indices)
Captura "17_psql_docker_estructura.png" 5436 "psql - PostgreSQL 16 (Docker 5436) - estructura de lectura y anotacion" @(
  "\d lectura",
  "\d anotacion"
) 150 60 1150

# 2) PostgreSQL 16 (Docker): lecturas con alerta, alertas y anotaciones
Captura "15_psql_docker_lecturas.png" 5436 "psql - PostgreSQL 16 (Docker 5436) - lecturas, alertas y anotaciones" @(
  "SELECT l.id, s.codigo, v.nombre AS variable, z.nombre AS zona, l.valor, v.unidad, l.origen, l.observacion, l.registrado_en, a.nivel AS alerta FROM lectura l JOIN sensor s ON s.id = l.sensor_id JOIN variable v ON v.id = s.variable_id JOIN zona z ON z.id = s.zona_id LEFT JOIN alerta a ON a.lectura_id = l.id ORDER BY l.registrado_en DESC LIMIT 10;",
  "SELECT a.id, s.codigo, a.nivel, a.mensaje, a.atendida, a.creada_en FROM alerta a JOIN lectura l ON l.id = a.lectura_id JOIN sensor s ON s.id = l.sensor_id ORDER BY a.creada_en DESC;",
  "SELECT n.id, z.nombre AS zona, n.autor_rol, n.texto, n.lectura_id, n.creada_en FROM anotacion n JOIN zona z ON z.id = n.zona_id ORDER BY n.creada_en DESC;"
) 170 40

# 3) PostgreSQL 17 instalado en Windows (puerto 5433): Opcion B del README
Captura "16_psql_nativo_pg17.png" 5433 "psql - PostgreSQL 17 instalado en Windows (5433) - Opcion B" @(
  "\conninfo",
  "SELECT version();",
  "\dt",
  "SELECT id, valor, origen, observacion, registrado_en FROM lectura ORDER BY id DESC LIMIT 5;"
)
Write-Host "Capturas guardadas en $Salida"
