$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$startupScript = Join-Path $repoRoot 'scripts\start-local-ci.ps1'
$taskName = 'KerjaYuk Local CI'
$userId = "$env:USERDOMAIN\$env:USERNAME"
$powershellExe = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$startupScript`""

$action = New-ScheduledTaskAction -Execute $powershellExe -Argument $arguments
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Starts KerjaYuk Jenkins and its Ngrok tunnel after Docker Desktop is ready.' -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Write-Output "Installed and started the '$taskName' logon task. It will start Jenkins and Ngrok when this Windows account signs in."
