# PowerShell script to view Streamlit logs
# This will run Streamlit in the foreground so you can see all logs

Write-Host "Stopping any existing Streamlit processes..."
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "Starting Streamlit in foreground mode to view logs..."
Write-Host "Press Ctrl+C to stop the app" -ForegroundColor Yellow
Write-Host ""

streamlit run main.py

