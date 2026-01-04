# won't work some of the requirements aren't supported on window :/

# Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Set-Location ..

# if (-not (Test-Path ".venv")) {
#     python -m venv .venv
# }

# & ".\.venv\Scripts\Activate.ps1"

# Set-Location api

# $NEW_DEPS = $false
# foreach ($arg in $args) {
#     if ($arg -eq "--new-deps") {
#         $NEW_DEPS = $true
#     }
# }

# if ($NEW_DEPS) {
#     pip-compile requirements.in
# }

# pip install -r requirements.txt

# Set-Location app
# fastapi run main.py

cd ../api

docker stop messenger-api

docker rm messenger-api

docker rmi messenger

docker build -t messenger:latest .

docker run -d -p 8000:8000  --name messenger-api --env-file ../.env messenger:latest

cd ../build-scripts
