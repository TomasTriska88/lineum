# clean_temp.ps1
# Removes temporary debug/scratch files to keep the workspace clean.

$patterns = @(
    "repro_*.py",
    "repro_*.txt",
    "console_*.txt",
    "final_*.txt",
    "alias_*.txt",
    "test_output*.txt",
    "contract_*.txt",
    "debug_*.py",
    "debug_*.txt"
)

Write-Host "Cleaning up temporary files..." -ForegroundColor Cyan

foreach ($pattern in $patterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -File
    if ($files) {
        foreach ($file in $files) {
            Write-Host "  Removing: $($file.Name)" -ForegroundColor Yellow
            Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
        }
    }
}

# Also clean .scratch (optional, but good practice if everything there is ephemeral)
# Write-Host "Cleaning .scratch directory..." -ForegroundColor Cyan
# Remove-Item -Path .scratch/* -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete." -ForegroundColor Green
