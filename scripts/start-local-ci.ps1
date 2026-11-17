$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$logDirectory = Join-Path $env:LOCALAPPDATA 'KerjaYuk'
$logPath = Join-Path $logDirectory 'local-ci-startup.log'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

function Write-StartupLog([string]$message) {
    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format o) $message"
}

try {
    Set-Location -LiteralPath $repoRoot
    $dockerCommand = Get-Command docker.exe -ErrorAction Stop
    $dockerReady = $false

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $null = & $dockerCommand.Source info 2>&1
        $dockerExitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorActionPreference
        if ($dockerExitCode -eq 0) {
            $dockerReady = $true
            break
        }
        Start-Sleep -Seconds 5
    }

    if (-not $dockerReady) {
        throw 'Docker did not become ready within five minutes.'
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $null = & $dockerCommand.Source compose --profile ci up -d jenkins 2>&1
    $composeExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($composeExitCode -ne 0) {
        throw 'Docker Compose could not start the Jenkins service.'
    }
    Write-StartupLog 'Jenkins container is running.'

    if (-not (Get-Process -Name ngrok -ErrorAction SilentlyContinue)) {
        $ngrokCommand = Get-Command ngrok.exe -ErrorAction Stop
        Start-Process -FilePath $ngrokCommand.Source -ArgumentList @('http', '8080') -WorkingDirectory $repoRoot -WindowStyle Hidden
        Write-StartupLog 'Started the Ngrok tunnel for Jenkins.'
    }
    else {
        Write-StartupLog 'Ngrok is already running; left the current tunnel alone.'
    }
}
catch {
    Write-StartupLog "Startup failed: $($_.Exception.Message)"
    throw
}
