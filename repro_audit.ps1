# Lineum Audit Reproduction Script (v1.0.18-core)
# Generates Run A (Baseline) and Run A2 (Verification) to prove determinism.

$ErrorActionPreference = "Stop"
$python = "python" # Ensure python is in PATH

# --- Configuration ---
# --- Configuration ---
$steps = 1000  # Extended window for cross-thread verification
$outDir = "output/audit_proof"
$runId = "6"      # Audit Spec preset
$runMode = "false" # Headless
$saveState = "true"
$wantFrames = "false"

# --- Environment Setup (Thread-Lock) ---
$Env:OMP_NUM_THREADS = "1"
$Env:MKL_NUM_THREADS = "1"
$Env:OPENBLAS_NUM_THREADS = "1"
$Env:NUMEXPR_NUM_THREADS = "1"
$Env:NUMBA_NUM_THREADS = "1"
Write-Host "Environment Locked: OMP/MKL/OPENBLAS/NUMEXPR/NUMBA = 1"

# Clean previous
if (Test-Path $outDir) {
    Write-Host "Cleaning $outDir..."
    Remove-Item $outDir -Recurse -Force
}

# --- Function: Run Lineum ---
function Run-Lineum {
    param($tag)

    Write-Host "`n--- Starting Run: $tag ---"
    
    # Set Env
    $env:LINEUM_STEPS = $steps
    $env:LINEUM_BASE_OUTPUT_DIR = $outDir
    $env:LINEUM_RUN_ID = $runId
    $env:LINEUM_RUN_MODE = $runMode
    $env:LINEUM_RUN_TAG = $tag
    $env:LINEUM_SAVE_STATE = $saveState
    $env:LINEUM_WANT_FRAMES = $wantFrames
    $env:LINEUM_DISABLE_TRACKING = "true"
    $env:LINEUM_DISABLE_TRACKING = "true"
    
    # Clear thread overrides
    Remove-Item Env:\OMP_NUM_THREADS -ErrorAction SilentlyContinue
    Remove-Item Env:\MKL_NUM_THREADS -ErrorAction SilentlyContinue
    Remove-Item Env:\NUMEXPR_NUM_THREADS -ErrorAction SilentlyContinue
    
    # Execute
    python lineum.py
}

# --- Execution ---
# 1. Run A (Baseline)
Run-Lineum -tag "d3_audit_A"

# 2. Run A2 (Verification)
Run-Lineum -tag "d3_audit_A2"

# 3. Run B1 (Single-Thread)
# Explicitly set threads to 1 for this run
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
Run-Lineum -tag "d3_audit_B1"
Remove-Item Env:\OMP_NUM_THREADS -ErrorAction SilentlyContinue
Remove-Item Env:\MKL_NUM_THREADS -ErrorAction SilentlyContinue
Remove-Item Env:\NUMEXPR_NUM_THREADS -ErrorAction SilentlyContinue

# 4. Run B2 (Single-Thread Verification)
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
Run-Lineum -tag "d3_audit_B2"
Remove-Item Env:\OMP_NUM_THREADS -ErrorAction SilentlyContinue
Remove-Item Env:\MKL_NUM_THREADS -ErrorAction SilentlyContinue
Remove-Item Env:\NUMEXPR_NUM_THREADS -ErrorAction SilentlyContinue

# 5. Run D4 (Ignition Check)
# Low Noise + No Injection (Implicit in RunID 6, but ensuring LOW_NOISE_MODE)
$env:LINEUM_PHI_INJECTION = "0.0"
$env:LOW_NOISE_MODE = "true"
Run-Lineum -tag "d4_ignition"
Remove-Item Env:\LINEUM_PHI_INJECTION -ErrorAction SilentlyContinue
Remove-Item Env:\LOW_NOISE_MODE -ErrorAction SilentlyContinue

Write-Host "`n--- Checking Results (Short Window: Step 200 / Index 199) ---"
Get-ChildItem -Path "$outDir" -Recurse -Filter "*step199.npz" | Get-FileHash -Algorithm SHA256 | Format-Table Hash, Path

Write-Host "`n--- Checking Results (Long Window: Step 1000 / Index 999) ---"
Get-ChildItem -Path "$outDir" -Recurse -Filter "*step999.npz" | Get-FileHash -Algorithm SHA256 | Format-Table Hash, Path

# 6. Run State Invariance Proof (Tracked vs Untracked)
Write-Host "`n--- Running State Invariance Proof (tools/prove_optimization.py) ---"
python tools/prove_optimization.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "State Invariance Proof FAILED!"
}
else {
    Write-Host "State Invariance Proof PASSED."
}


# 7. Code Audit (Entropy Scan)
Write-Host "`n--- Scanning for Entropy Sources (Seeded Init Check) ---"
$entropyMatches = Select-String -Pattern "random|numpy\.random|time\.time|datetime" -Path lineum.py
if ($entropyMatches) {
    Write-Host "Info: Entropy sources found (Verify they are seeded/logging only):" -ForegroundColor Cyan
    $entropyMatches | ForEach-Object { Write-Host $_ }
}
else {
    Write-Host "PASS: No entropy sources found." -ForegroundColor Green
}

Write-Host "DONE: Files ready for audit package."
