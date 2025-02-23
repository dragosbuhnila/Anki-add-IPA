# Get the root directory (two levels up from this script)
$rootDir = Split-Path (Split-Path $PSScriptRoot) -Parent

# Change to root directory
Set-Location $rootDir

# Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# Run the Python script
python .\menu.py