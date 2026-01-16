$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Cell Store.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\Sebastian\Desktop\CellStore\cellstore\run.bat"
$Shortcut.WorkingDirectory = "C:\Users\Sebastian\Desktop\CellStore\cellstore"
$Shortcut.Description = "Inicia la aplicación Flask Cell Store"
$Shortcut.IconLocation = "C:\Windows\System32\python.exe"
$Shortcut.Save()

Write-Host "Acceso directo creado en el escritorio: Cell Store.lnk"
