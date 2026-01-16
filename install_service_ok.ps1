# Script para crear la tarea programada - Ejecutar como Administrador
# Este script crea una tarea que ejecuta la aplicación Flask automáticamente al iniciar Windows

$ErrorActionPreference = "Stop"

# Verificar si se está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Este script requiere permisos de administrador. Reintentando..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurando servicio Cell Store Flask" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$taskName = "CellStore_Flask_Service"
$vbsPath = "C:\Users\Public\CellStore\cellstore\run_service.vbs"
$description = "Servicio autoejecutable de Cell Store Flask"

# Verificar que el archivo .vbs existe
if (-not (Test-Path $vbsPath)) {
    Write-Host "ERROR: No se encuentra el archivo VBS en:" -ForegroundColor Red
    Write-Host "  $vbsPath" -ForegroundColor Red
    Write-Host "Verifique la ruta y vuelva a intentarlo." -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit
}

# Eliminar tarea anterior si existe
Write-Host "[1/3] Eliminando tarea anterior..." -ForegroundColor Yellow
try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} catch {
    Write-Host "  (No había tarea anterior)" -ForegroundColor Gray
}

# Crear acción y trigger
Write-Host "[2/3] Creando nueva tarea programada..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)

# Registrar la tarea
Write-Host "[3/3] Registrando tarea en Windows..." -ForegroundColor Yellow
try {
    Register-ScheduledTask -TaskName $taskName -Description $description -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -User "SYSTEM" -Force | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SERVICIO INSTALADO CORRECTAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "La aplicación Flask se ejecutará automáticamente al iniciar Windows." -ForegroundColor Green
    Write-Host ""
    Write-Host "Para verificar la tarea:" -ForegroundColor Cyan
    Write-Host "  schtasks /query /tn `"$taskName`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para ejecutar manualmente ahora:" -ForegroundColor Cyan
    Write-Host "  schtasks /run /tn `"$taskName`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Logs del servicio en:" -ForegroundColor Cyan
    Write-Host "  C:\Users\Sebastian\Desktop\CellStore\cellstore\service.log" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "ERROR: No se pudo crear la tarea" -ForegroundColor Red
    Write-Host "Detalle: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Presione Enter para salir..." -ForegroundColor Yellow
Read-Host