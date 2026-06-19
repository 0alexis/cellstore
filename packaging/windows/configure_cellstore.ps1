param(
    [Parameter(Mandatory = $true)]
    [string]$InstallDir,

    [Parameter(Mandatory = $true)]
    [string]$ProgramDataDir
)

$ErrorActionPreference = 'Stop'

$dataDir = Join-Path $ProgramDataDir 'data'
$uploadDir = Join-Path $ProgramDataDir 'uploads'
$envPath = Join-Path $InstallDir '.env'
$exePath = Join-Path $InstallDir 'CellStore.exe'
$taskName = 'CellStore Auto Start'
$firewallRuleName = 'CellStore Port 8000'

New-Item -ItemType Directory -Force -Path $ProgramDataDir, $dataDir, $uploadDir | Out-Null

$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
$dbPath = Join-Path $dataDir 'cellstore.db'

$envContent = @"
HOST=0.0.0.0
PORT=8000
DEBUG=False
FLASK_ENV=production
SERVER_BACKEND=waitress
WAITRESS_THREADS=8
WAITRESS_CONNECTION_LIMIT=100
DATABASE_URL=sqlite:///$($dbPath -replace '\\','/')
UPLOAD_FOLDER=$uploadDir
SECRET_KEY=$secretKey
RUN_STARTUP_MIGRATIONS=True
RUN_STARTUP_INDEXES=True
"@

Set-Content -Path $envPath -Value $envContent -Encoding ASCII

$action = New-ScheduledTaskAction -Execute $exePath -WorkingDirectory $InstallDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -RunLevel Highest -LogonType ServiceAccount

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {
}

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null

try {
    Remove-NetFirewallRule -DisplayName $firewallRuleName -ErrorAction SilentlyContinue
} catch {
}

New-NetFirewallRule -DisplayName $firewallRuleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8000 | Out-Null
Start-ScheduledTask -TaskName $taskName