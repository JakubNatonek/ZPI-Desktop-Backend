Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (!(Test-Path ".venv\Scripts\python.exe")) {
    c:/python314/python.exe -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

$env:DATABASE_URL = "postgresql://userzpi:userzpi%23@localhost:5432/zpidb"

python -m pip install -r requirements.txt

.\.venv\Scripts\alembic.exe -c alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) {
    throw "Alembic migration failed. Backend startup aborted."
}
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload