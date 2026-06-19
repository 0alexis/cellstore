param(
    [Parameter(Mandatory = $true)]
    [string]$InstallDir
)

$ErrorActionPreference = 'Continue'
$taskName = 'CellStore Auto Start'
$firewallRuleName = 'CellStore Port 8000'

try {
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
} catch {
}

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
} catch {
}

try {
    Remove-NetFirewallRule -DisplayName $firewallRuleName -ErrorAction SilentlyContinue
} catch {
}

$envPath = Join-Path $InstallDir '.env'
if (Test-Path $envPath) {
    Remove-Item $envPath -Force -ErrorAction SilentlyContinue
}