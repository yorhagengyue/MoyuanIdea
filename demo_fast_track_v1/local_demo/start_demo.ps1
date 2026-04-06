$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:FOURSAPI_API_KEY) {
  Write-Warning "FOURSAPI_API_KEY is not set. The classroom flow will run with fallback guidance."
}
if (-not $env:FOURSAPI_GEMINI_API_KEY) {
  Write-Warning "FOURSAPI_GEMINI_API_KEY is not set. Option images may fail to generate."
}

if (-not $env:FOURSAPI_MODEL) {
  $env:FOURSAPI_MODEL = "claude-sonnet-4-5-20250929"
}

if (-not $env:FOURSAPI_THINKING_MODEL) {
  $env:FOURSAPI_THINKING_MODEL = "claude-sonnet-4-5-20250929-thinking"
}
if (-not $env:GEMINI_IMAGE_MODEL) {
  $env:GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"
}

Write-Host "Starting Moyuan local demo on http://127.0.0.1:8000 ..."
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
