# Get the root directory (two levels up from this script)
$rootDir = Split-Path (Split-Path $PSScriptRoot) -Parent

# Change to root directory
Set-Location $rootDir

# Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# Prompt user for word and language
Write-Host "`nEnter the word you want to test: " -NoNewline
$word = Read-Host
Write-Host "Enter the language (e.g., english, japanese, korean): " -NoNewline
$language = Read-Host

# Run the Python script with user input
Write-Host "`nTesting word '$word' for language '$language'...`n"
python .\main.py --test_phrase $word $language