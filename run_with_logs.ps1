# Run Streamlit and capture logs to a file
# Usage: .\run_with_logs.ps1

$logFile = "streamlit_logs_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

Write-Host "Starting Streamlit and logging to: $logFile" -ForegroundColor Green
Write-Host "The app will be available at http://localhost:8501" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop and view logs" -ForegroundColor Yellow
Write-Host ""

# Stop any existing Streamlit processes
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Run Streamlit and capture output
streamlit run main.py 2>&1 | Tee-Object -FilePath $logFile

Write-Host "`nLogs saved to: $logFile" -ForegroundColor Cyan

