# Installa gli strumenti del sistema video (una volta sola, Windows).
# Uso: powershell -ExecutionPolicy Bypass -File installa.ps1
# Crea un ambiente Python in %LOCALAPPDATA%\mi-video-editing\.venv (percorso corto: evita
# l'errore dei percorsi troppo lunghi di Windows) con ffmpeg, trascrittore e librerie grafiche.

$ErrorActionPreference = "Stop"
$dir = Join-Path $env:LOCALAPPDATA "mi-video-editing"
$venv = Join-Path $dir ".venv"
$req = Join-Path $PSScriptRoot "requirements.txt"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python non trovato. Installa Python 3.10 o superiore da python.org e rilancia."
    exit 1
}
New-Item -ItemType Directory -Force $dir | Out-Null
if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) { python -m venv $venv }
$py = Join-Path $venv "Scripts\python.exe"
& $py -m pip install --quiet --upgrade pip
& $py -m pip install --quiet -r $req
& $py -c "import imageio_ffmpeg, PIL, numpy; print('ffmpeg:', imageio_ffmpeg.get_ffmpeg_exe())"
& $py -c "import os, sys; os.add_dll_directory(sys.prefix); import faster_whisper; print('trascrittore: ok')"
Write-Host ""
Write-Host "Pronto. Python del sistema video:"
Write-Host "  $py"
