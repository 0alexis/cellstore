# Script para crear la tarea programada de Windows
# Ejecutar como Administrador

# Definir las variables
$taskName = "CellStore Flask App"
$taskDescription = "Ejecuta la aplicación Flask Cell Store automáticamente al iniciar"
$vbsPath = "C:\Users\Sebastian\Desktop\CellStore\cellstore\run_service.vbs"
$taskAction = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
$taskTrigger = New-ScheduledTaskTrigger -AtStartup
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Crear la tarea programada
Try {
    # Intentar eliminar la tarea si ya existe
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Crear nueva tarea
    Register-ScheduledTask -TaskName $taskName `
        -Description $taskDescription `
        -Action $taskAction `
        -Trigger $taskTrigger `
        -Settings $taskSettings `
        -RunLevel Highest `
        -User "SYSTEM" `
        -Force
    
    Write-Host "✓ Tarea programada '$taskName' creada exitosamente" -ForegroundColor Green
    Write-Host "✓ La aplicación Flask se ejecutará automáticamente al iniciar Windows" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para verificar el estado de la tarea, ejecute:" -ForegroundColor Yellow
    Write-Host "Get-ScheduledTask -TaskName 'CellStore Flask App'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para ver los logs, abra:" -ForegroundColor Yellow
    Write-Host "C:\Users\Sebastian\Desktop\Cell Store\cellstore\service.log" -ForegroundColor Cyan
}
Catch {
    Write-Host "✗ Error al crear la tarea: $_" -ForegroundColor Red
}
