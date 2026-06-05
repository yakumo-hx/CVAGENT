$ErrorActionPreference = "Stop"
$Root = (Resolve-Path ".").Path
$PromptData = Join-Path $Root "src\prompts"
$Entry = Join-Path $Root "apps\desktop\desktop_app.py"

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pyinstaller

if (Test-Path "build\desktop") {
  Remove-Item -Recurse -Force "build\desktop"
}
if (Test-Path "dist\desktop") {
  Remove-Item -Recurse -Force "dist\desktop"
}

.\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "CVAGENT-Desktop" `
  --distpath "dist\desktop" `
  --workpath "build\desktop" `
  --specpath "build\desktop" `
  --add-data "$PromptData;src\prompts" `
  "$Entry"

New-Item -ItemType Directory -Force -Path "release\desktop" | Out-Null
Copy-Item -Force "dist\desktop\CVAGENT-Desktop.exe" "release\desktop\CVAGENT-Desktop.exe"

Write-Output "Built release\desktop\CVAGENT-Desktop.exe"
