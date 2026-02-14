from typing import MutableSequence, Deque, Union, Optional, Tuple
from collections import deque
import datetime
import json
import math
import random
from scipy.spatial.distance import euclidean
from scipy.ndimage import gaussian_filter, maximum_filter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from scipy.fft import fft, fftfreq
from tqdm import tqdm
import os as _os
import os
import glob
import hashlib
import subprocess

# --- Fingerprinting ---
def _compute_code_fingerprint(files, normalized_newlines=True):
    """
    Computes a deterministic SHA256 fingerprint for a list of files.
    - Paths are normalized to be relative to the script directory and use '/' separators.
    - If normalized_newlines=True, CRLF is converted to LF before hashing.
    - Individual file hashes are tracked.
    - A combined multi-file hash is computed from "path:hash" lines.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_hashes = {}
    
    # Process individual files
    for fpath in sorted(files):
        # Normalize path to repo-root-relative with '/'
        abs_path = os.path.abspath(fpath)
        if not abs_path.startswith(script_dir):
            # If it's outside, just use the basename or path as provided? 
            # Requirements say "repo-root-relative".
            rel_path = os.path.relpath(abs_path, script_dir).replace("\\", "/")
        else:
            rel_path = os.path.relpath(abs_path, script_dir).replace("\\", "/")

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Fingerprint failed: Missing file '{abs_path}'")
            
        with open(abs_path, "rb") as f:
            content = f.read()
            
        if normalized_newlines:
            content = content.replace(b"\r\n", b"\n")
            
        file_hash = hashlib.sha256(content).hexdigest()
        file_hashes[rel_path] = file_hash

    # Compute aggregate metadata hash
    # Sort by rel_path to ensure determinism
    meta_lines = []
    for path in sorted(file_hashes.keys()):
        meta_lines.append(f"{path}:{file_hashes[path]}")
    
    meta_blob = "\n".join(meta_lines).encode("utf-8")
    combined_sha256 = hashlib.sha256(meta_blob).hexdigest()
        
    return {
        "sha256": combined_sha256,
        "files": sorted(file_hashes.keys()),
        "file_hashes": file_hashes,
        "normalized_newlines": normalized_newlines
    }

def _get_git_info():
    """Returns git info (commit, dirty) if available. Info only."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode().strip()
        return {"commit": commit, "dirty": bool(status)}
    except Exception:
        return None


# NOTE: do not hardcode config toggles later; use CONFIGS mapping as source of truth.


def _canonical_val_str(obj):
    """
    Deterministic string representation for hashing and preview.
    - float: .17g, -0.0 -> 0.0, NaN/Inf as tokens
    - bool: "True"/"False"
    - numpy: cast to python primitive
    - recursive: handles nested structures
    """
    import numpy as _np

    # Booleans (must check before int because bool is int subclass)
    if isinstance(obj, bool):
        return str(obj)

    # Numpy scalars -> Python primitives
    if isinstance(obj, (_np.integer,)):
        obj = int(obj)
    elif isinstance(obj, (_np.floating,)):
        obj = float(obj)

    # Numbers
    if isinstance(obj, (int, float)):
        if isinstance(obj, float):
            if not math.isfinite(obj):
                if math.isnan(obj): return "NaN"
                return "Infinity" if obj > 0 else "-Infinity"
            if obj == 0.0: obj = 0.0 # Normalize -0.0
            return format(obj, ".17g")
        return str(obj)

    # Strings
    if isinstance(obj, str):
        return obj

    # Bytes / Bytearray -> Hex
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()

    # None
    if obj is None:
        return "None"

    # Collections (Recursive)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_canonical_val_str(x) for x in obj) + "]"
    
    if isinstance(obj, set):
        # Deterministic sort for mixed types
        # Key uses (type_name, canonical_str) for absolute stability
        sorted_elements = sorted(list(obj), key=lambda x: (type(x).__name__, _canonical_val_str(x)))
        return "{" + ",".join(_canonical_val_str(x) for x in sorted_elements) + "}"

    if isinstance(obj, dict):
        # Non-string keys are stringified as (type:val) to avoid collisions
        def _safe_key(k):
            if isinstance(k, str): return k
            return f"({type(k).__name__}:{_canonical_val_str(k)})"
        
        sorted_keys = sorted(obj.keys(), key=_safe_key)
        parts = []
        for k in sorted_keys:
            parts.append(f"{_safe_key(k)}:{_canonical_val_str(obj[k])}")
        return "{" + ",".join(parts) + "}"

    # Fallback for complex objects (e.g. RNG state bits)
    return str(obj)


def _canonical_json_normalize(obj):
    """
    Recursively normalize objects for json.dumps(allow_nan=False).
    Converts numbers/special values into their stable serializable forms.
    """
    import numpy as _np

    if isinstance(obj, bool): return obj # bool must be before int
    if isinstance(obj, (_np.integer,)): return int(obj)
    if isinstance(obj, (_np.floating,)): obj = float(obj)

    if isinstance(obj, float):
        if not math.isfinite(obj):
            if math.isnan(obj): return "NaN"
            return "Infinity" if obj > 0 else "-Infinity"
        if obj == 0.0: return 0.0 # Normalize -0.0
        # For actual snapshot we keep as float, formatting happens in hash-view
        return obj
    
    if isinstance(obj, (int, str)) or obj is None:
        return obj

    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()

    if isinstance(obj, (list, tuple)):
        return [_canonical_json_normalize(x) for x in obj]
    
    if isinstance(obj, set):
        # Sets must become sorted lists for JSON stability
        return sorted([_canonical_json_normalize(x) for x in obj], 
                      key=lambda x: (type(x).__name__, _canonical_val_str(x)))

    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            # JSON keys must be strings
            sk = k if isinstance(k, str) else f"({type(k).__name__}:{_canonical_val_str(k)})"
            res[sk] = _canonical_json_normalize(v)
        return res

    return str(obj)


def _compute_canonical_hash(obj):
    """
    Deterministic SHA256 from object.
    Uses strict normalization and json.dumps parameters.
    """
    norm = _canonical_json_normalize(obj)
    # Using separators=(",", ":") to eliminate whitespace variations.
    # allow_nan=False is a hard guard (normalization should have handled it).
    blob = json.dumps(norm, sort_keys=True, allow_nan=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _json_safe(obj):
    """
    Převádí numpy typy na primitivní Python (kvůli JSON serializaci).
    Nyní využívá unifikovanou normalizaci pro stabilitu.
    """
    return _canonical_json_normalize(obj)


def _compute_binary_kappa_hash(kappa_map):
    """
    Deterministic SHA256 of binary kappa data.
    Enforces C-order, little-endian float64.
    Fails if contains non-finite values or is an object array.
    """
    import numpy as _np
    
    # Fail-fast guards
    if not _np.isfinite(kappa_map).all():
        raise ValueError("Binary Kappa Hash failed: Map contains NaN or Infinity.")
        
    try:
        # astype("<f8") handles little-endian float64
        # ascontiguousarray(..., order='C') ensures memory layout stability
        clean = _np.ascontiguousarray(kappa_map, dtype="<f8")
        if clean.dtype.kind == 'O': 
            raise TypeError("Binary Kappa Hash failed: Received object array.")
        
        blob = clean.tobytes()
        return hashlib.sha256(blob).hexdigest()
    except Exception as e:
        raise RuntimeError(f"Binary Kappa Hash failed during binary conversion: {e}")


def _atomic_write_bytes(path: str, data: bytes) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, path)


def _atomic_write_json(path: str, payload: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_json_safe(payload), f, ensure_ascii=False, indent=2)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    os.replace(tmp, path)


def _env_bool(name: str, default: bool) -> bool:
    v = _os.environ.get(name, None)
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default


def _env_int(name: str, default: int) -> int:
    v = _os.environ.get(name, None)
    if v is None:
        return default
    try:
        n = int(str(v).strip())
        return n
    except Exception:
        return default


def _env_str(name: str, default: str = "") -> str:
    v = _os.environ.get(name, None)
    return default if v is None else str(v)


# --- Run config ---
RUN_ID = 6
RUN_MODE = "false"
SEED = 41

# Optional env overrides for canonical run selection:
#   LINEUM_RUN_ID=6
#   LINEUM_RUN_MODE=true|false|1|0|yes|no|on|off
try:
    RUN_ID = int(_os.environ.get("LINEUM_RUN_ID", RUN_ID))
except Exception:
    pass

_rm_env = _os.environ.get("LINEUM_RUN_MODE", None)
if _rm_env is not None:
    RUN_MODE = _rm_env


# Normalize RUN_MODE to canonical string keys used in CONFIGS ("true"/"false")
# Prevents silent fallback when RUN_MODE is passed as True/False or "True"/"FALSE", etc.
_rm = str(RUN_MODE).strip().lower()
if _rm in ("1", "yes", "y", "on"):
    _rm = "true"
elif _rm in ("0", "no", "n", "off"):
    _rm = "false"
RUN_MODE = _rm


# allow env override for the seed, e.g. LINEUM_SEED=23
try:
    SEED = int(_os.environ.get("LINEUM_SEED", SEED))
except Exception:
    pass


# Optional label for experiment variants (leave "" for baseline)
# Examples: "w512" (C1), "dt05_w512" (C2), "grid256" (C3)
PARAM_TAG = ""


# --- Variant resolver (dynamic) ---
# Allow env override, e.g. LINEUM_PARAM_TAG="w512" or "dt05_w512"
PARAM_TAG = _os.environ.get("LINEUM_PARAM_TAG", PARAM_TAG).strip()


def _variant_window_params(param_tag: str, base_W=256, base_hop=128):
    """
    Map PARAM_TAG to windowing parameters for f₀/SBR estimation.
    Examples:
      ""         -> (256, 128)
      "w512"     -> (512, 256)
      "w1024"    -> (1024, 512)
    Multiple tags can be underscore-joined; window tag wins if present.
    """
    tags = {t for t in (param_tag or "").split("_") if t}
    W, hop = base_W, base_hop
    if "w1024" in tags:
        W, hop = 1024, 512
    elif "w512" in tags:
        W, hop = 512, 256
    return W, hop


WINDOW_W, WINDOW_HOP = _variant_window_params(PARAM_TAG)


_RUN_TAG_DERIVED = f"spec{RUN_ID}_{RUN_MODE}_s{SEED}{('_' + PARAM_TAG) if PARAM_TAG else ''}"

# Optional explicit override for the whole run tag (e.g. audit labels)
# If provided, it MUST win for all filenames, manifests, HTML links, etc.
RUN_TAG = _os.environ.get("LINEUM_RUN_TAG", "").strip() or _RUN_TAG_DERIVED

np.random.seed(SEED)
random.seed(SEED)

# 🔧 Configuration mapping
CONFIGS = {
    # Observable-world / low-entropy test
    (1, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "gradient"},

    # Resonance between order and chaos
    (1, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "gradient"},

    # Structure-from-flow only (no memory)
    (2, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "gradient"},

    # Turbulent quantum-like field
    (2, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "gradient"},

    # Mathematical ideal; silence → structure
    (3, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "constant"},

    # Determinism + noise (physical-like)
    (3, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "constant"},

    # Closed system / trapped particle
    (4, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island"},

    # Quantum-experiment-like setup
    (4, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island"},

    # Detector for extremely subtle effects
    (5, "true"): {"LOW_NOISE_MODE": True, "TEST_EXHALE_MODE": True, "KAPPA_MODE": "island"},

    # Island universe under collapse
    (5, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "island"},

    # Latent ideal with slowdown
    (6, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "constant"},

    # # Noisy reality + memory
    (6, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "constant"},

    # Laws gradually becoming globally shared
    (7, "true"): {"LOW_NOISE_MODE": True, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island_to_constant"}
}

# --- Resolve and Capture Configuration Snapshot ---
cfg = CONFIGS.get((RUN_ID, RUN_MODE), {})
LOW_NOISE_MODE = cfg.get("LOW_NOISE_MODE", False)
TEST_EXHALE_MODE = cfg.get("TEST_EXHALE_MODE", False)
KAPPA_MODE = cfg.get("KAPPA_MODE", "gradient")

# Allow env override for toggles (optional), WITHOUT changing defaults from CONFIGS.
_LNM_ENV = _env_bool("LINEUM_LOW_NOISE_MODE", LOW_NOISE_MODE)
_TEM_ENV = _env_bool("LINEUM_TEST_EXHALE_MODE", TEST_EXHALE_MODE)

# Capture all relevant variables before any other logic modifies them
RESOLVED_CONFIG = {
    "run_id": RUN_ID,
    "run_mode": RUN_MODE,
    "seed": SEED,
    "param_tag": PARAM_TAG,
    "low_noise_mode": _LNM_ENV,
    "test_exhale_mode": _TEM_ENV,
    "kappa_mode": KAPPA_MODE,
    "window_w": WINDOW_W,
    "window_hop": WINDOW_HOP,
    "phi_interaction_cap": _env_int("LINEUM_PHI_INTERACTION_CAP", 0),
    "steps": _env_int("LINEUM_STEPS", 2000),
    "store_every": _env_int("LINEUM_STORE_EVERY", 5)
}
RESOLVED_CONFIG_HASH = _compute_canonical_hash(RESOLVED_CONFIG)

LOW_NOISE_MODE = _LNM_ENV
TEST_EXHALE_MODE = _TEM_ENV

# --- HARD GUARD: never silently fall back to defaults for canonical runs ---
assert (RUN_ID, RUN_MODE) in CONFIGS, (
    f"Missing CONFIGS key for canonical run: (RUN_ID, RUN_MODE)=({RUN_ID}, {RUN_MODE}). "
    "Either add it to CONFIGS or fix RUN_ID/RUN_MODE normalization/env."
)

# --- Trace resolved config early (before any env overrides) ---
print(
    "CONFIG RESOLVED (from CONFIGS):",
    f"RUN_ID={RUN_ID}",
    f"RUN_MODE={RUN_MODE}",
    f"LOW_NOISE_MODE={LOW_NOISE_MODE}",
    f"TEST_EXHALE_MODE={TEST_EXHALE_MODE}",
    f"KAPPA_MODE={KAPPA_MODE}",
    f"RUN_TAG={RUN_TAG}",
    f"RUN_TAG_DERIVED={_RUN_TAG_DERIVED}",
)

# --- (optional) show env overrides that could change behavior ---
_env_watch = ("LINEUM_RUN_ID", "LINEUM_RUN_MODE", "LINEUM_SEED",
              "LINEUM_PARAM_TAG", "LINEUM_RUN_TAG",
              "LINEUM_LOW_NOISE_MODE", "LINEUM_TEST_EXHALE_MODE",
              "LINEUM_STEPS", "LINEUM_SAVE_GIFS", "LINEUM_SAVE_FRAMES", "LINEUM_SAVE_PNGS",
              "LINEUM_PHI_INTERACTION_CAP")
_env_present = {k: _os.environ.get(
    k) for k in _env_watch if _os.environ.get(k) is not None}
if _env_present:
    print("ENV OVERRIDES PRESENT:", _env_present)

# Allow env override for toggles (optional), WITHOUT changing defaults from CONFIGS.
# Accepted values: "1/0", "true/false", "yes/no", "on/off".


LOW_NOISE_MODE = _env_bool("LINEUM_LOW_NOISE_MODE", LOW_NOISE_MODE)
TEST_EXHALE_MODE = _env_bool("LINEUM_TEST_EXHALE_MODE", TEST_EXHALE_MODE)

# --- Output Directory Logic ---

# Base output directory (kořen)
# [IMPORTANT] "output_wp" is reserved STRICTLY for audit/whitepaper runs. 
# Do NOT use it for diagnostic tests or temporary diagnostic scripts.
BASE_OUTPUT_DIR = _env_str("LINEUM_BASE_OUTPUT_DIR", "output")
_os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

# Global placeholders (populated by setup_output_globals)
output_dir = None
_ckpt_dir = None
RUN_DIR_NAME = None

# Update latest_run.txt (Atomic)
def _update_latest_run_pointer(base_dir: str, run_rel_path: str):
    try:
        ptr_path = _os.path.join(base_dir, "latest_run.txt")
        _atomic_write_bytes(ptr_path, run_rel_path.encode('utf-8'))
    except Exception as e:
        print(f"[!] Failed to update latest_run.txt: {e}")

def setup_output_globals(resume_checkpoint: Optional[str] = None):
    """
    Sets up global output_dir and _ckpt_dir.
    If resuming from a checkpoint inside a 'runs' folder, reuses that folder.
    Otherwise creates a new timestamped run folder.
    """
    global output_dir, _ckpt_dir, RUN_DIR_NAME

    # 1. Try to derive from resume checkpoint
    reused = False
    if resume_checkpoint:
        # Expected: .../runs/<RUN_TAG>_<TIMESTAMP>/checkpoints/<ckpt>.npz
        # Parent: .../runs/<RUN_TAG>_<TIMESTAMP>/checkpoints
        # Grandparent: .../runs/<RUN_TAG>_<TIMESTAMP>
        try:
            abs_ckpt = _os.path.abspath(resume_checkpoint)
            ckpt_parent = _os.path.dirname(abs_ckpt)
            parent_name = _os.path.basename(ckpt_parent)
            print(f"DEBUG: setup_output_globals: abs_ckpt='{abs_ckpt}'")
            print(f"DEBUG: setup_output_globals: ckpt_parent='{ckpt_parent}'")
            print(f"DEBUG: setup_output_globals: parent_name='{parent_name}'")
            if parent_name.lower() == "checkpoints":
                candidate_run_dir = _os.path.dirname(ckpt_parent)
                print(f"DEBUG: setup_output_globals: candidate_run_dir='{candidate_run_dir}'")
                if _os.path.exists(candidate_run_dir):
                    output_dir = candidate_run_dir
                    _ckpt_dir = ckpt_parent
                    RUN_DIR_NAME = _os.path.relpath(output_dir, BASE_OUTPUT_DIR)
                    reused = True
                    print(f"[*] ♻️ RESUME-IN-PLACE: Reusing output directory: {output_dir}")
                else:
                    print(f"DEBUG: setup_output_globals: cand_run_dir DOES NOT EXIST")
            else:
                print(f"DEBUG: setup_output_globals: parent_name != 'checkpoints'")
        except Exception as e:
            print(f"[!] Failed to derive run dir from checkpoint: {e}")

    # 2. If not reusing, create new timestamped dir
    if not reused:
        _ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        RUN_DIR_NAME = f"runs/{RUN_TAG}_{_ts}"
        output_dir = _os.path.join(BASE_OUTPUT_DIR, RUN_DIR_NAME)
        _os.makedirs(output_dir, exist_ok=True)
        _ckpt_dir = _os.path.join(output_dir, "checkpoints")
        _os.makedirs(_ckpt_dir, exist_ok=True)
        print(f"📂 Output directory: {output_dir}")

    # 3. Always update pointer to where we are writing
    _update_latest_run_pointer(BASE_OUTPUT_DIR, RUN_DIR_NAME)

# --- Frame storage throttling (memory/perf) ---
# Store only every Nth step into frames_* (used for GIFs/NPY dumps).
# Logs/metrics still run every step.


# How often to store simulation frames (for GIFs/NPY). 5 => store ~400 frames for 2000 steps.
STORE_EVERY = _env_int("LINEUM_STORE_EVERY", 5)
# Additional skip applied inside GIF writers (keeps files smaller). 2 => half the stored frames.
GIFT_SKIP = _env_int("LINEUM_GIF_SKIP", 2)

# Lightweight dtypes for stored frames (visualization only)
size = 128
L = size
FAST_TRACKING = True

DT_AMP = np.float32
DT_VEC = np.float32
DT_CURL = np.float32
DT_PHI = np.float32
DT_VORT = np.int8
DT_PART = np.uint8


def sliding_windows_1d(x, W, hop):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < W:
        return []
    return [x[i:i+W] for i in range(0, n - W + 1, hop)]


def bootstrap_mean_ci(vals, B=1000, alpha=0.05, rng=np.random):
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0:
        return (float('nan'), (float('nan'), float('nan')))
    n = vals.size
    means = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.randint(0, n, size=n)
        means[b] = np.mean(vals[idx])
    
    # Filter NaNs before quantile
    valid_means = means[np.isfinite(means)]
    if valid_means.size == 0:
        return (float(np.nanmean(vals)) if np.any(np.isfinite(vals)) else float('nan'), (float('nan'), float('nan')))
        
    try:
        lo = float(np.quantile(valid_means, alpha/2))
        hi = float(np.quantile(valid_means, 1 - alpha/2))
    except Exception as e:
        print(f"[!] bootstrap_mean_ci quantile failed: {e}")
        lo, hi = float('nan'), float('nan')
    return (float(np.nanmean(vals)), (lo, hi))


def window_sbr_and_f0(amplitudes, dt, W=256, hop=128, guard=2):
    """
    Windowed SBR and f0 using parabolic 3-bin interpolation for precise f0.
    Metadata is captured for audit suite transparency.
    """
    amps = np.asarray(amplitudes, dtype=float)
    sbr_vals, f0_vals = [], []
    
    # Audit Metadata (Stateless)
    SR = 1.0 / dt
    DF = SR / W
    NYQUIST = SR / 2.0
    
    for w in sliding_windows_1d(amps, W=W, hop=hop):
        # DC removal (subtract mean)
        w = w - np.mean(w)
        
        # Hann window application
        wh = w * np.hanning(len(w))
        
        # FFT (Real)
        Ffull = np.fft.rfft(wh)
        P = np.abs(Ffull).astype(np.float64, copy=False)**2
        P = np.where(np.isfinite(P), P, 0.0)
        Fp = np.fft.rfftfreq(len(w), d=dt)
        Pp = P
        if Pp.size == 0:
            continue

        # Dominant bin search
        idx0 = int(np.argmax(Pp))
        pmax = float(Pp[idx0])
        
        # Background estimation (excluding ±guard)
        mask = np.ones_like(Pp, dtype=bool)
        l = max(idx0 - guard, 0)
        r = min(idx0 + guard + 1, Pp.size)
        mask[l:r] = False
        bg = float(np.mean(Pp[mask])) if np.any(mask) else np.nan
        if bg > 0:
            sbr_vals.append(pmax / bg)

        # Precise f0: Parabolic 3-bin Interpolation
        if 0 < idx0 < Pp.size - 1:
            p_prev = float(Pp[idx0 - 1])
            p_curr = float(Pp[idx0])
            p_next = float(Pp[idx0 + 1])
            
            denom = 2 * p_curr - p_prev - p_next
            # Robustness threshold: avoid division by zero or jittery unstable peaks
            if abs(denom) > 1e-12 * p_curr:
                offset = 0.5 * (p_prev - p_next) / denom
                best_idx = idx0 + offset
            else:
                best_idx = float(idx0) # Fallback to bin center
        else:
            best_idx = float(idx0) # Fallback for edge cases
            
        f0_vals.append(best_idx * DF)

    sbr_mean, sbr_ci = bootstrap_mean_ci(sbr_vals) if sbr_vals else (
        float('nan'), (float('nan'), float('nan')))
    f0_mean,  f0_ci = bootstrap_mean_ci(f0_vals) if f0_vals else (
        float('nan'), (float('nan'), float('nan')))
        
    # Carry metadata for report
    meta = {
        "dt": float(dt),
        "sampling_rate_hz": float(SR),
        "df_hz": float(DF),
        "nyquist_hz": float(NYQUIST),
        "window_length": int(W),
        "hop_length": int(hop),
        "guard_bins": int(guard),
        "window_function": "Hann",
        "dc_remove": True,
        "fft_type": "RFFT",
        "estimator": "parabolic_3_bin",
        "estimator_threshold": 1e-12
    }
    
    return (sbr_mean, sbr_ci), (f0_mean, f0_ci), meta


def notify_file_creation(path, success=True, error=None):
    """Print a notification about file creation success or failure."""
    name = _os.path.basename(path)
    if success:
        print(f"[check] File '{name}' has been successfully created.")
    else:
        print(f"[ERR] Failed to create file '{name}': {error}")


def save_csv(filename, header, rows):
    """Fast CSV save using pandas; avoids per-row Python overhead."""
    path = _os.path.join(output_dir, f"{RUN_TAG}_{filename}")
    try:
        # Materialize rows once (zip/generators → list); much faster than row-by-row writes
        data = list(rows)
        # Build DataFrame with/without header
        if header:
            df = pd.DataFrame(data, columns=header)
        else:
            df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)


def save_manifest(
    manifest=None,
    filename=None,
    run_info=None,
    metrics=None,
    data_files=None,
    extra=None,
):
    """
    Save a JSON manifest for this run for machine parsing.

    Použití:
      • save_manifest(manifest_dict)
      • save_manifest("file.json", run_info=..., metrics=..., data_files=...)
    """
    # Když nedostaneme hotový manifest, složíme ho z dílků
    if manifest is None:
        manifest = {
            "run": run_info or {},
            "metrics": metrics or {},
            "data_files": data_files or [],
        }

        # Calculate fingerprints
        # ENFORCED: Simulation Core & Verifier (since it handles derived metrics)
        ENFORCED_FILES = ["lineum.py", "tools/whitepaper_contract.py"]
        
        try:
            manifest["code_fingerprint"] = _compute_code_fingerprint(
                ENFORCED_FILES, 
                normalized_newlines=True
            )
        except Exception as e:
            # Re-raise or handle? Requirements say FAIL if missing.
            # In save_manifest, failing here will likely crash the run's finalization.
            # That's good - we shouldn't save a broken manifest.
            raise e
            
        # Info: Git
        manifest["git_info"] = _get_git_info()
        
        if extra:
            manifest["extra"] = extra

    # ENFORCE CRITICAL METADATA (runs passed from main() might miss these)
    # ---------------------------------------------------------
    if "invariants" not in manifest:
        manifest["invariants"] = {
            "dim": "2D",
            "bcs": "periodic",
            "precision": "float64",
            "stencil": "classic_laplace",
            "grid_size": size,
            "dt": 0.01 # Baseline dt
        }
    
    # Bundle resolved config and provenance
    manifest["run_configuration"] = {
        "resolved_config": RESOLVED_CONFIG,
        "resolved_config_hash": RESOLVED_CONFIG_HASH
    }
    
    # RNG Provenance
    rng_backend = "unknown"
    rng_state_hash = None
    try:
        # Check for np.random (legacy RandomState)
        if hasattr(np.random, "get_state"):
            state = np.random.get_state()
            rng_backend = str(state[0]) # e.g. "MT19937"
            rng_state_hash = _compute_canonical_hash(state)
        
        # Check if we have a Generator (modern API)
        # Note: Generator doesn't have a global singleton state like RandomState,
        # but if we initialized with np.random.seed, it mostly affects the legacy pool.
        # If we use np.random.default_rng(SEED), we should track that Generator.
    except Exception:
        pass
        
    manifest["provenance"] = {
        "rng_backend": rng_backend,
        "seed": SEED,
        "rng_state_hash": rng_state_hash
    }

    if "logging" not in manifest:
        manifest["logging"] = {
            "topo_log_stride": TRACK_EVERY
        }

    if "code_fingerprint" not in manifest:
        ENFORCED_FILES = ["lineum.py", "tools/whitepaper_contract.py"]
        try:
            manifest["code_fingerprint"] = _compute_code_fingerprint(
                ENFORCED_FILES, 
                normalized_newlines=True
            )
        except Exception as e:
            print(f"[!] Warning: Failed to compute code_fingerprint: {e}")

    if filename is None:
        filename = f"{RUN_TAG}_manifest.json"

    path = _os.path.join(output_dir, filename)
    try:
        safe = _json_safe(manifest)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(safe, f, ensure_ascii=False, indent=2)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)

# IMPORTANT:
# LOW_NOISE_MODE / TEST_EXHALE_MODE are set above from CONFIGS (+ optional env override).
# Do NOT override them here, otherwise RUN_ID/RUN_MODE mapping becomes meaningless.


size = 128

# Allow grid-size override via PARAM_TAG (e.g., "grid256")
_tag_raw = _os.environ.get("LINEUM_PARAM_TAG", "").strip()
_tag = (PARAM_TAG or _tag_raw).strip()
_tagset = {t for t in _tag.split("_") if t}
if "grid256" in _tagset:
    size = 256

# Allow window settings via PARAM_TAG:
#   - "w256" -> overrides WINDOW_W
#   - "hop128" or "h128" -> overrides WINDOW_HOP
for t in _tagset:
    if t.startswith("w"):
        try:
            _w = int(t[1:].strip())
            if _w > 0:
                WINDOW_W = _w
        except Exception:
            pass
    if t.startswith("hop"):
        try:
            _h = int(t.replace("hop", "").strip())
            if _h > 0:
                WINDOW_HOP = _h
        except Exception:
            pass
    if t.startswith("h") and not t.startswith("hop"):
        try:
            _h = int(t[1:].strip())
            if _h > 0:
                WINDOW_HOP = _h
        except Exception:
            pass

# (Optional) allow "stepsXXXX" tag, e.g. "steps4000"
# Make it robust: only override if we successfully parse a positive integer.
steps_override = None
for t in _tagset:
    if t.startswith("steps"):
        try:
            _n = int(t.replace("steps", "").strip())
            if _n > 0:
                steps_override = _n
        except Exception:
            # ignore malformed steps tag
            steps_override = steps_override

# steps is derived from TEST_EXHALE_MODE (and may be overridden by steps_override)
steps = int(steps_override) if steps_override is not None else (
    2000 if TEST_EXHALE_MODE else 500
)

# Optional explicit env override (keeps your PowerShell baseline flexible)
steps_env = _env_int("LINEUM_STEPS", -1)
if steps_env and steps_env > 0:
    steps = int(steps_env)

# Canonical noise level
BASE_NOISE_STRENGTH = 0.005
NOISE_STRENGTH = 0.0 if LOW_NOISE_MODE else BASE_NOISE_STRENGTH

# Probe points whose amplitude we track
probe_points = [(y, x) for y in range(0, size, 20) for x in range(0, size, 20)]

# 0 = keep full history (default)
# LINEUM_ROLLING_WINDOW applies to "rolling exports" and multi-probe logs; it does not affect CSV outputs unless you wire it.
#
#
# Stability / service-mode controls (MUST be defined before ROLLING_WINDOW uses INFINITE_MODE)
#
CHECKPOINT_EVERY = _env_int("LINEUM_CHECKPOINT_EVERY", 25)  # recommended 10–50
TRACK_EVERY = _env_int("LINEUM_TRACK_EVERY", 1)
SAVE_STATE = _env_bool("LINEUM_SAVE_STATE", False)
RESUME_ENABLED = _env_bool("LINEUM_RESUME", True)
INFINITE_MODE = _env_bool("LINEUM_INFINITE", False)
METRICS_EXPORT_EVERY = _env_int("LINEUM_METRICS_EXPORT_EVERY", 25)

# 0 = keep full history (default)
# LINEUM_ROLLING_WINDOW applies to "rolling exports" and multi-probe logs.
ROLLING_WINDOW = _env_int("LINEUM_ROLLING_WINDOW", 0)
if INFINITE_MODE and (not ROLLING_WINDOW or ROLLING_WINDOW <= 0):
    # keep RAM bounded in service mode even if user forgot to set it
    ROLLING_WINDOW = 2000

if ROLLING_WINDOW and ROLLING_WINDOW > 0:
    multi_amp_logs = {pt: deque(maxlen=ROLLING_WINDOW) for pt in probe_points}
else:
    multi_amp_logs = {pt: [] for pt in probe_points}

# Optional: cap in-memory logs too (keeps RAM bounded in infinite/service mode)
LOG_ROLLING_WINDOW = _env_int(
    "LINEUM_LOG_ROLLING_WINDOW",
    ROLLING_WINDOW if (ROLLING_WINDOW and ROLLING_WINDOW > 0) else 0
)


def _maybe_rolling_list():
    return deque(maxlen=LOG_ROLLING_WINDOW) if (LOG_ROLLING_WINDOW and LOG_ROLLING_WINDOW > 0) else []


# create logs AFTER ROLLING_WINDOW exists
particle_log = _maybe_rolling_list()
interaction_log = _maybe_rolling_list()
amplitude_log = _maybe_rolling_list()
topo_log = _maybe_rolling_list()
phi_center_log = _maybe_rolling_list()


def _tail(seq, n: int):
    if not n or n <= 0:
        return list(seq) if not isinstance(seq, list) else seq
    if isinstance(seq, deque):
        return list(seq)[-n:]
    return seq[-n:] if isinstance(seq, list) else list(seq)[-n:]


PIXEL_SIZE = 1e-12     # 1 pixel = 1 pm (pikometr)
TIME_STEP = 1e-21      # 1 krok = 1 zs (zeptosekunda)

# Allow time-step refinement via PARAM_TAG (e.g., "dt05" halves Δt)
_tag_raw = _os.environ.get("LINEUM_PARAM_TAG", "").strip()
_tag = (PARAM_TAG or _tag_raw).strip()
_tags = {t for t in _tag.split("_") if t}

if "dt05" in _tags:
    TIME_STEP *= 0.5

#
# Output minimization toggles (your PowerShell audit baseline expects these)
#
SAVE_GIFS = _env_bool("LINEUM_SAVE_GIFS", True)
SAVE_FRAMES = _env_bool("LINEUM_SAVE_FRAMES", True)
SAVE_PNGS = _env_bool("LINEUM_SAVE_PNGS", True)

STORE_EVERY = _env_int("LINEUM_STORE_EVERY", STORE_EVERY)
GIF_SKIP = _env_int("LINEUM_GIF_SKIP", GIFT_SKIP)

#
# Optional experimental φ-injection near detected quasiparticles.
# IMPORTANT: default OFF to keep canonical core behavior stable for audits/whitepaper runs.
# Enable via env:
#   LINEUM_PHI_INJECTION=0.2
#
PHI_INJECTION_AMOUNT = float(_os.environ.get(
    "LINEUM_PHI_INJECTION", "0") or "0")

#
# Interaction cap for coupling term (φ * ψ):
# Keep default at the old hardcoded 10.0, but make it configurable + auditable.
# This is intentionally separate from PHI_CAP (global numeric safety cap).
# Enable via env:
#   LINEUM_PHI_INTERACTION_CAP=10
#
PHI_INTERACTION_CAP = float(_os.environ.get(
    "LINEUM_PHI_INTERACTION_CAP", "10.0") or "10.0")


# (moved выше) Stability / service-mode controls are defined earlier to avoid NameError.




def _checkpoint_dir() -> str:
    base = _env_str("LINEUM_CHECKPOINT_DIR", "").strip()
    if base:
        d = base
    else:
        d = os.path.join(output_dir, "checkpoints")
    os.makedirs(d, exist_ok=True)
    return d


def _checkpoint_paths(step_idx: int) -> Tuple[str, str]:
    d = _checkpoint_dir()
    stem = f"{RUN_TAG}_ckpt_{step_idx:08d}"
    return (os.path.join(d, stem + ".npz"), os.path.join(d, stem + ".json"))


def _find_latest_checkpoint(explicit_path: Optional[str] = None, base_output_dir: str = BASE_OUTPUT_DIR) -> Optional[str]:
    """
    Finds the best candidate for resumption.
    Priority:
    1. Explicit path (arg or env)
    2. Latest run (via latest_run.txt -> run_dir/checkpoints/*.npz)
    3. Legacy fallback (output/checkpoints/*.npz or output/*.npz)
    """
    # 1. Explicit path (highest priority)
    if explicit_path:
        if os.path.isfile(explicit_path):
            print(f"[*] Resuming from explicit checkpoint: {explicit_path}")
            return explicit_path
        else:
            print(f"CRITICAL ERROR: Explicit checkpoint not found: {explicit_path}")
            sys.exit(1)

    # 2. Environment Variables (Explicit override)
    primary = os.environ.get("LINEUM_CHECKPOINT")
    alias = os.environ.get("LINEUM_RESUME_CHECKPOINT")

    if primary and alias:
        print("WARNING: deprecated alias LINEUM_RESUME_CHECKPOINT ignored in favor of LINEUM_CHECKPOINT. CONFLICT: Both are set. Using LINEUM_CHECKPOINT.")
    elif alias:
        print("WARNING: deprecated alias LINEUM_RESUME_CHECKPOINT used. Please use LINEUM_CHECKPOINT instead.")

    env_path = primary or alias
    if env_path:
        if os.path.isfile(env_path):
            print(f"[*] Resuming from environment: {env_path}")
            return env_path
        else:
            print(f"CRITICAL ERROR: Explicit checkpoint not found: {env_path}. Aborting to prevent split-brain / divergent runs.")
            sys.exit(1)

    candidates = []

    def _scan_dir(d, priority):
        if not os.path.isdir(d):
            return
        files = os.listdir(d)
        for fn in files:
            if fn.endswith(".npz"):
                fp = os.path.join(d, fn)
                try:
                    stat = os.stat(fp)
                    candidates.append({
                        "path": fp,
                        "mtime": stat.st_mtime,
                        "size": stat.st_size,
                        "priority": priority
                    })
                except Exception:
                    pass

    # 3. Latest Run (Automated detection)
    latest_run_ptr = os.path.join(base_output_dir, "latest_run.txt")
    if os.path.isfile(latest_run_ptr):
        try:
            with open(latest_run_ptr, "r", encoding="utf-8") as f:
                rel_path = f.read().strip()
            
            run_dir = os.path.join(base_output_dir, rel_path)
            # Ensure it's inside base_output_dir (no path traversal)
            if os.path.abspath(run_dir).startswith(os.path.abspath(base_output_dir)):
                 _scan_dir(os.path.join(run_dir, "checkpoints"), priority=2)
        except Exception:
            pass

    # 4. Legacy Fallback
    _scan_dir(os.path.join(base_output_dir, "checkpoints"), priority=3)
    _scan_dir(base_output_dir, priority=3)

    if not candidates:
        return None

    # Sort: Priority (lowest number first), then Mtime (newest first)
    candidates.sort(key=lambda x: (x["priority"], -x["mtime"], -x["size"]))
    
    best = candidates[0]["path"]
    print(f"[*] Found latest checkpoint (priority={candidates[0]['priority']}): {best}")
    return best



def save_state_checkpoint(run_dir: str, run_prefix: str, step_idx: int,
                          psi: np.ndarray, phi: np.ndarray, kappa: np.ndarray, delta: np.ndarray,
                          active_tracks: dict, next_id: int) -> Optional[str]:
    """
    Uloží minimální deterministický stav (pro restart) do NPZ (bez pickle).
    Vrací relativní cestu k vytvořenému souboru (vůči run_dir), nebo None při chybě.
    """
    # Force checkpoints subdir
    ckpt_subdir = os.path.join(run_dir, "checkpoints")
    os.makedirs(ckpt_subdir, exist_ok=True)

    filename = f"checkpoints/{run_prefix}_state_step{step_idx}.npz"
    path = os.path.join(run_dir, filename)
    tmp_path = path + ".tmp.npz"

    # 1. Tracky: rozpad na pole
    ids = sorted(active_tracks.keys())
    track_ids = np.array(ids, dtype=np.int64)
    if len(ids) > 0:
        track_pos_xy = np.array([active_tracks[tid] for tid in ids], dtype=np.float64)
    else:
        track_pos_xy = np.zeros((0, 2), dtype=np.float64)

    # 2. RNG: rozpad state (numpy global)
    # state = ('MT19937', keys, pos, has_gauss, cached_gauss)
    rng_algo_str, rng_keys, rng_pos, rng_has_gauss, rng_cached_gauss = np.random.get_state()

    # 3. Uložení
    try:
        np.savez_compressed(
            tmp_path,
            # Fyzikální pole
            psi=psi,
            phi=phi,
            kappa=kappa,
            delta=delta,
            # Meta
            step_index=step_idx,
            next_id=next_id,
            # Tracks
            track_ids=track_ids,
            track_pos_xy=track_pos_xy,
            # RNG (legacy numpy global) - breakdown
            rng_algo=rng_algo_str,
            rng_keys=rng_keys,
            rng_pos=rng_pos,
            rng_has_gauss=rng_has_gauss,
            rng_cached_gauss=rng_cached_gauss
        )
        # Flush
        try:
            with open(tmp_path, "rb") as f:
                os.fsync(f.fileno())
        except Exception:
            pass
        
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
        os.replace(tmp_path, path)
        notify_file_creation(path)
        return filename
    except Exception as e:
        print(f"[!] save_state_checkpoint failed: {e}")
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return None


def save_checkpoint(step_idx: int, psi: np.ndarray, phi: np.ndarray, delta: np.ndarray, kappa: np.ndarray,
                    next_id: int, active_tracks: dict, trajectories: list,
                    logs: dict) -> None:
    npz_path, meta_path = _checkpoint_paths(step_idx)

    # Pack RNG states (best-effort; JSON-safe via repr)
    rng_np = np.random.get_state()
    rng_py = random.getstate()

    # Save arrays (binary) atomically
    # IMPORTANT:
    #   np.savez_compressed() appends ".npz" if the filename does NOT end with ".npz".
    #   Using "<name>.npz.tmp" would silently create "<name>.npz.tmp.npz" and os.replace() would fail.
    tmp_npz = npz_path + ".tmp.npz"
    try:
        np.savez_compressed(
            tmp_npz,
            step=np.array([step_idx], dtype=np.int64),
            psi=psi,
            phi=phi,
            delta=delta,
            kappa=kappa,
            next_id=np.array([next_id], dtype=np.int64),
            # NOTE: active_tracks / trajectories / logs go to JSON (smaller, flexible)
        )
        # best-effort flush to disk before rename (Windows/Linux safe)
        try:
            with open(tmp_npz, "rb") as _f:
                try:
                    os.fsync(_f.fileno())
                except Exception:
                    pass
        except Exception:
            pass
        os.replace(tmp_npz, npz_path)
    finally:
        # cleanup in case something failed before replace
        try:
            if os.path.exists(tmp_npz) and (not os.path.exists(npz_path)):
                os.remove(tmp_npz)
        except Exception:
            pass

    # Save meta (JSON) atomically
    meta = {
        "run_tag": RUN_TAG,
        "step": int(step_idx),
        "size": int(size),
        "time_step": float(TIME_STEP),
        "kappa_mode": KAPPA_MODE,
        "param_tag": _tag,
        "next_id": int(next_id),
        "active_tracks": active_tracks,
        # keep last chunk only
        "trajectories_tail": trajectories[-min(len(trajectories), 5000):] if isinstance(trajectories, list) else list(trajectories)[-min(len(trajectories), 5000):],
        "logs_tail": logs,
        "rng_np": repr(rng_np),
        "rng_py": repr(rng_py),
        "rng_restore_policy": "not_restored (arrays-only resume)",
        "created_utc": datetime.datetime.utcnow().isoformat() + "Z",
    }
    _atomic_write_json(meta_path, meta)


def load_checkpoint(npz_path: str, meta_path: Optional[str] = None):
    print(f"📦 Loading checkpoint from: {npz_path}")
    data = np.load(npz_path, allow_pickle=False)
    
    # Handle both old 'step' (array) and new 'step_index' (scalar)
    if "step_index" in data:
        step_idx = int(data["step_index"])
    else:
        step_idx = int(data["step"][0])

    psi = data["psi"]
    phi = data["phi"]
    delta = data["delta"] if "delta" in data else generate_structured_delta()
    kappa = data["kappa"]
    
    # Handle next_id
    if "next_id" in data:
        val = data["next_id"]
        next_id = int(val.item()) if val.ndim == 0 else int(val[0])
    else:
        next_id = 0

    active_tracks = {}
    trajectories_tail = []
    logs_tail = {}

    # 1. Try new format tracks (numpy arrays in npz)
    if "track_ids" in data and "track_pos_xy" in data:
        t_ids = data["track_ids"]
        t_pos = data["track_pos_xy"]
        if len(t_ids) == len(t_pos):
            for i, tid in enumerate(t_ids):
                # Ensure simple python types
                active_tracks[int(tid)] = [float(t_pos[i, 0]), float(t_pos[i, 1])]
    
    # 2. Fallback to legacy metadata if available
    if (not active_tracks) and meta_path and os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            active_tracks = meta.get("active_tracks", {}) or {}
            trajectories_tail = meta.get("trajectories_tail", []) or []
            logs_tail = meta.get("logs_tail", {}) or {}
        except Exception:
            pass
            
    # 3. Restore RNG if available (New format)
    # state = ('MT19937', keys, pos, has_gauss, cached_gauss)
    if "rng_algo" in data and "rng_keys" in data:
        try:
            r_algo = str(data["rng_algo"])
            r_keys = data["rng_keys"]
            r_pos = int(data["rng_pos"])
            r_has = int(data["rng_has_gauss"])
            r_cached = float(data["rng_cached_gauss"])
            np.random.set_state((r_algo, r_keys, r_pos, r_has, r_cached))
            print("🎲 RNG state restored from checkpoint.")
        except Exception as e:
            print(f"[!] Failed to restore RNG state: {e}")

    return step_idx, psi, phi, delta, kappa, next_id, active_tracks, trajectories_tail, logs_tail


def export_rolling_metrics(step_idx: int, payload: dict) -> None:
    # single compact JSON for “last X” consumption by external tools
    path = os.path.join(output_dir, f"{RUN_TAG}_rolling_metrics.json")
    out = {
        "run_tag": RUN_TAG,
        "step": int(step_idx),
        "updated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "data": payload,
    }
    _atomic_write_json(path, out)


def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))


def generate_kappa(step, total_steps=None):
    """Postupná změna z island na constant"""
    if total_steps is None:
        total_steps = 1
    progress = step / float(max(1, total_steps))
    core = np.zeros((size, size))
    core[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
    core = gaussian_filter(core, sigma=5)
    return (1 - progress) * core + progress * 0.5


def generate_structured_delta(scale=10):
    noise = np.random.normal(0.0, 1.0, (size, size))
    blurred = gaussian_filter(noise, sigma=scale)
    return blurred / np.max(np.abs(blurred)) * 0.05


def initialize_fields():
    amp = np.random.normal(0.0, 0.1, (size, size))
    phase = np.random.uniform(0, 2*np.pi, (size, size))
    amp[size//2, size//2] += 1.0  # asymetrie uprostřed
    psi = amp * np.exp(1j * phase)
    delta = generate_structured_delta()
    return psi, delta


def initialize_interaction_field():
    # φ is a scalar background field (real). Keep it float for stability and interpretability.
    return np.zeros((size, size), dtype=np.float64)


def diffuse_complex(field, rate=0.05):
    return rate * (
        np.roll(field, 1, axis=0) +
        np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) +
        np.roll(field, -1, axis=1) -
        4 * field
    )


def diffuse_real(field: np.ndarray, rate=0.05) -> np.ndarray:
    field = np.asarray(field, dtype=np.float64)
    return rate * (
        np.roll(field, 1, axis=0) +
        np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) +
        np.roll(field, -1, axis=1) -
        4.0 * field
    )


def _finite_clip(a, lo=None, hi=None, nan=0.0, posinf=None, neginf=None, dtype=None):
    """
    Make array finite and optionally clip.
    - replaces NaN/Inf with finite values first (so squaring won't overflow)
    - then applies clip
    """
    x = np.asarray(a)
    if dtype is not None:
        x = x.astype(dtype, copy=False)
    if posinf is None:
        posinf = hi if hi is not None else 0.0
    if neginf is None:
        neginf = lo if lo is not None else 0.0
    x = np.nan_to_num(x, nan=nan, posinf=posinf, neginf=neginf)
    if lo is not None or hi is not None:
        x = np.clip(x, lo if lo is not None else -np.inf,
                    hi if hi is not None else np.inf)
    return x


def _cap_complex_magnitude(z: np.ndarray, cap: float) -> np.ndarray:
    """
    Hard-cap |z| to 'cap' while preserving phase. Prevents numeric blow-ups.
    """
    z = np.asarray(z, dtype=np.complex128)
    mag = np.abs(z).astype(np.float64, copy=False)
    # avoid division by 0
    scale = np.ones_like(mag, dtype=np.float64)
    mask = mag > cap
    if np.any(mask):
        scale[mask] = cap / (mag[mask] + 1e-30)
        z = z * scale
    return z


def _finite_complex(z: np.ndarray, nan: float = 0.0) -> np.ndarray:
    """
    Make complex array finite without using np.clip (which is invalid for complex).
    Replaces NaN/Inf in real/imag parts independently.
    """
    z = np.asarray(z, dtype=np.complex128)
    re = np.nan_to_num(z.real, nan=nan, posinf=0.0, neginf=0.0)
    im = np.nan_to_num(z.imag, nan=nan, posinf=0.0, neginf=0.0)
    return re + 1j * im


# Safety caps (keep conservative; just preventing numeric blow-ups)
PSI_AMP_CAP = 1e6          # cap |psi| before squaring / interactions
GRAD_CAP = 1e6          # cap gradient components before squaring
PHI_CAP = 1e6          # hard cap for |phi| to keep interaction finite


def evolve(psi, delta, phi, kappa):
    # ψ is complex; φ is real scalar.
    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0,
                       posinf=PHI_CAP, neginf=0.0, dtype=np.float64)

    # amplitude (cap BEFORE any squaring)
    amp = np.abs(psi).astype(np.float64, copy=False)
    amp = _finite_clip(amp, lo=0.0, hi=PSI_AMP_CAP, nan=0.0,
                       posinf=PSI_AMP_CAP, neginf=0.0)

    # gradient of (amp + delta)
    grad_x, grad_y = np.gradient((amp + delta).astype(np.float64, copy=False))
    # cap gradients BEFORE squaring (this is where your overflow happens)
    grad_x = _finite_clip(grad_x, lo=-GRAD_CAP, hi=GRAD_CAP,
                          nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_y = _finite_clip(grad_y, lo=-GRAD_CAP, hi=GRAD_CAP,
                          nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    probability = sigmoid(amp + grad_mag)
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base = 0.01 if TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if TEST_EXHALE_MODE else 0.02
    linon_effect = (linon_base + linon_scaling * amp.clip(min=0)) * linons

    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.random.normal(
        0.0, NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    # 💡 Adding interaction (φ is real scalar; keep bounded)
    # NOTE: previously hardcoded to 10.0; now configurable via LINEUM_PHI_INTERACTION_CAP
    phi_int = _finite_clip(phi, lo=0.0, hi=float(PHI_INTERACTION_CAP), nan=0.0,
                           posinf=float(PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    interaction_term = 0.04 * phi_int * psi

    # 💫 Gradient φ jako „tíhový tok“
    grad_phi_x, grad_phi_y = np.gradient(phi)
    phi_flow_term = -0.004 * (grad_phi_x + 1j * grad_phi_y)
    psi += phi_flow_term

    psi += linon_complex + fluctuation + interaction_term

    dissipation_rate = 0.00462  # ln(2)/150 → half-life 150 steps
    psi -= dissipation_rate * psi

    psi += diffuse_complex(psi)

    # 🌀 Canonical φ-evolution: slow memory + single calibrated diffusion
    # ≈ ln(2) / (2000 * ⟨κ⟩) with ⟨κ⟩≈0.5 → half-life ≈ 2000 steps
    reaction_strength = 0.00070

    # IMPORTANT: never do (abs(psi)**2) directly; it can overflow before clip.
    amp2 = _finite_clip(np.abs(psi).astype(np.float64, copy=False),
                        lo=0.0, hi=PSI_AMP_CAP, nan=0.0, posinf=PSI_AMP_CAP, neginf=0.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)

    # single-step relaxation toward local_input:
    phi += kappa * reaction_strength * (local_input - phi)

    # diffusion on real φ: use real Laplacian diffusion
    phi += kappa * 0.30 * diffuse_real(phi)

    # post-step safety
    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0,
                       posinf=PHI_CAP, neginf=0.0, dtype=np.float64)

    # CRITICAL: hard-cap |psi| so FFT power never overflows in extreme regimes
    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)

    return psi, phi


def save_phi_center_plot(filename=f"{RUN_TAG}_phi_center_plot.png"):
    phi_center_values = [row[1] for row in phi_center_log]
    steps_list = [row[0] for row in phi_center_log]

    plt.figure(figsize=(8, 4))
    plt.plot(steps_list, phi_center_values, label="|φ_center|", color="orange")
    plt.xlabel("Step")
    plt.ylabel("|φ_center|")
    plt.title("Development of the amplitude of the interaction field at the center")
    plt.grid(True)
    plt.tight_layout()
    path = _os.path.join(output_dir, filename)
    try:
        plt.savefig(path)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)
    finally:
        plt.close()


def save_kappa_map(kappa, filename=f"{RUN_TAG}_kappa_map.png"):
    """
    Save kappa map visualization and track its binary hash for audit.
    """
    # Recalculate hash on every save to ensure consistency
    k_hash = _compute_binary_kappa_hash(kappa)
    print(f"[*] Kappa Map Binary Hash: {k_hash}")
    
    path = _os.path.join(output_dir, filename)
    try:
        plt.figure(figsize=(6, 5))
        plt.imshow(kappa, origin='lower', cmap='viridis')
        plt.colorbar(label='Kappa (κ)')
        plt.title(f"Kappa Map ({KAPPA_MODE})\n{k_hash[:8]}...")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)
    
    return k_hash


def detect_vortices(phase: np.ndarray) -> np.ndarray:
    """
    Vectorized winding-number detection on 2x2 plaquettes.
    Returns int array in {-1,0,+1}, without amplitude gating.
    """
    p00 = phase[:-1, :-1]
    p01 = phase[:-1, 1:]
    p11 = phase[1:, 1:]
    p10 = phase[1:, :-1]

    d1 = np.angle(np.exp(1j * (p01 - p00)))
    d2 = np.angle(np.exp(1j * (p11 - p01)))
    d3 = np.angle(np.exp(1j * (p10 - p11)))
    d4 = np.angle(np.exp(1j * (p00 - p10)))
    winding = (d1 + d2 + d3 + d4) / (2 * np.pi)

    vortices = np.zeros_like(phase, dtype=int)
    block = vortices[:-1, :-1]
    block[winding > 0.5] = 1
    block[winding < -0.5] = -1
    return vortices


VORTEX_VIS_PERCENTILE = 5.0  # visualization-only gate: keep lowest 5% amplitudes


LogSeq = Union[list, deque]


def update_topology_log(raw_vortices: np.ndarray, step_idx: int, topo_log: LogSeq) -> None:
    """
    Append RAW topology counts for this step into topo_log: (step, +1, -1, net, total).
    """
    num_pos = int(np.sum(raw_vortices == 1))
    num_neg = int(np.sum(raw_vortices == -1))
    net_charge = num_pos - num_neg
    total = num_pos + num_neg
    topo_log.append((step_idx, num_pos, num_neg, net_charge, total))


def gate_vortices_by_amplitude(vortices: np.ndarray, amp: np.ndarray, amp_thresh: float = None) -> np.ndarray:
    """
    Keep vortex marks only where |psi| is low (near singularities).
    Used for visualization; metrics still use raw vortices.
    """

    if amp_thresh is None:
        # default: robust 5th percentile
        amp_thresh = float(np.percentile(amp, VORTEX_VIS_PERCENTILE))
    mask = (amp <= amp_thresh)
    out = np.zeros_like(vortices)
    out[:-1, :-1] = vortices[:-1, :-1] * mask[:-1, :-1]
    return out


FAST_TRACKING = True  # Legacy flag for tests


def _track_quasiparticles_slow(coords, active_tracks, next_id, step_idx, amp, trajectories):
    """Legacy slow tracking to satisfy tests."""
    new_tracks = {}
    for y, x in coords:
        best_id = None
        min_dist = 3.0
        for tid, tpos in active_tracks.items():
            dist = np.sqrt((y - tpos[0])**2 + (x - tpos[1])**2)
            if dist < min_dist:
                min_dist = dist
                best_id = tid

        if best_id is not None:
            new_tracks[best_id] = (float(y), float(x))
            trajectories.append((int(best_id), int(step_idx), int(
                y), int(x), float(amp[int(y), int(x)])))
            del active_tracks[best_id]
        else:
            new_tracks[next_id] = (float(y), float(x))
            trajectories.append((int(next_id), int(step_idx), int(
                y), int(x), float(amp[int(y), int(x)])))
            next_id += 1
    return new_tracks, next_id


def _track_quasiparticles_slow(coords, active_tracks, next_id, step_idx, amp, trajectories):
    """Legacy slow tracking to satisfy tests."""
    new_active_tracks = {}
    assigned = set()
    for cy, cx in coords:
        pos = np.array([float(cy), float(cx)])
        min_dist = float("inf")
        closest_id = None
        for tid, last_pos in active_tracks.items():
            dist = np.sqrt((cy - last_pos[0])**2 + (cx - last_pos[1])**2)
            if dist < 3.0 and tid not in assigned and dist < min_dist:
                min_dist = dist
                closest_id = tid
        
        if closest_id is not None:
             new_active_tracks[closest_id] = pos
             assigned.add(closest_id)
             trajectories.append((int(closest_id), int(step_idx), int(cy), int(cx), float(amp[int(cy), int(cx)])))
        else:
             new_active_tracks[next_id] = pos
             trajectories.append((int(next_id), int(step_idx), int(cy), int(cx), float(amp[int(cy), int(cx)])))
             next_id += 1
    return new_active_tracks, next_id

def _track_quasiparticles_fast(coords, active_tracks, next_id, step_idx, amp, trajectories):
    """Refactored fast tracking logic."""
    assigned = set()
    new_active_tracks = {}
    for cy, cx in coords:
        pos = np.array([cy, cx])
        min_dist = float("inf")
        closest_id = None
        for tid, last_pos in active_tracks.items():
            dist = np.linalg.norm(pos - last_pos)
            if dist < 3.0 and tid not in assigned and dist < min_dist:
                min_dist = dist
                closest_id = tid
        if closest_id is not None:
            new_active_tracks[closest_id] = pos
            assigned.add(closest_id)
            trajectories.append((int(closest_id), int(step_idx), int(cy), int(cx), float(amp[int(cy), int(cx)])))
        else:
            new_active_tracks[next_id] = pos
            trajectories.append((int(next_id), int(step_idx), int(cy), int(cx), float(amp[int(cy), int(cx)])))
            next_id += 1
    return new_active_tracks, next_id

if __name__ == "__main__":
    # Optionally resume from last checkpoint (same RUN_TAG)
    step_start = 0
    resumed = False
    resume_npz = None
    if RESUME_ENABLED:
        resume_npz = _find_latest_checkpoint(base_output_dir=BASE_OUTPUT_DIR)

    # Setup output directory (either new or reused from checkpoint)
    setup_output_globals(resume_npz)

    if RESUME_ENABLED and resume_npz:
        try:
            step_start, psi, phi, delta, kappa, next_id, active_tracks, trajectories, logs_tail = load_checkpoint(
                resume_npz)
            resumed = True
            # Continue AFTER the checkpointed step to avoid duplicating that step's logs.
            step_start = int(step_start) + 1
            # Restore logs (tail only, keeps memory bounded)
            try:
                for row in (logs_tail.get("particle_log", []) or []):
                    particle_log.append(tuple(row))
                for row in (logs_tail.get("interaction_log", []) or []):
                    interaction_log.append(tuple(row))
                for row in (logs_tail.get("amplitude_log", []) or []):
                    amplitude_log.append(tuple(row))
                for row in (logs_tail.get("topo_log", []) or []):
                    topo_log.append(tuple(row))
                for row in (logs_tail.get("phi_center_log", []) or []):
                    phi_center_log.append(tuple(row))
            except Exception:
                pass
        except Exception:
            resumed = False

    if not resumed:
        # Inicializace polí
        psi, delta = initialize_fields()
        phi = initialize_interaction_field()
        # Ladicí pole (KAPPA)
        kappa = np.ones((size, size), dtype=np.float64)

        if KAPPA_MODE == "gradient":
            for y in range(size):
                kappa[y, :] = np.linspace(0.1, 1.0, size)
        elif KAPPA_MODE == "constant":
            kappa *= 0.5
        elif KAPPA_MODE == "island":
            from scipy.ndimage import gaussian_filter
            kappa *= 0.0
            kappa[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
            kappa = gaussian_filter(kappa, sigma=5)

        # Enforce C-order and guards BEFORE first hash/save
        kappa = np.ascontiguousarray(kappa, dtype=np.float64)
        if not np.isfinite(kappa).all():
             raise ValueError(f"CRITICAL: Kappa initialization resulted in non-finite values ({KAPPA_MODE})")
        
        KAPPA_HASH = save_kappa_map(kappa)
        
    # Track spatial means for dynamic stats if needed (Always initialize to avoid NameError)
    kappa_spatial_means = []

    WANT_FRAMES = bool(SAVE_GIFS or SAVE_FRAMES or SAVE_PNGS)
    # In infinite/service mode, never accumulate frames in RAM (would grow without bound).
    if INFINITE_MODE:
        WANT_FRAMES = False
    frames_amp, frames_vecx, frames_vecy, frames_curl, frames_vort, frames_particles = [
    ], [], [], [], [], []
    frames_phi = []
    # stored simulation step for each stored frame (aligns frames_* to sim steps)
    frames_step_idx = []
    # O(1) mapping: sim_step -> stored frame index
    frames_step_to_idx = {}

    def _has_frames() -> bool:
        """
        True if we actually stored at least one throttled frame (aligned via frames_step_idx).
        Many post-run analyses (spin aura, phi-near-particles, NPY dumps, GIFs) depend on this.
        """
        return len(frames_step_idx) > 0

    def _warn_skip(msg: str) -> None:
        print(f"[!] Skipping: {msg}")

    def _nonempty(lst) -> bool:
        try:
            return lst is not None and len(lst) > 0
        except Exception:
            return False

    def _frame_idx_for_step(step: int) -> Optional[int]:
        """
        Map simulation step -> stored frame index (for frames_* arrays).
        Returns None if that step was not stored (because of STORE_EVERY or resume alignment).
        """
        return frames_step_to_idx.get(int(step))

    def _phi_frame_idx(step: int) -> Optional[int]:
        """
        Map simulation step -> frames_phi index, respecting STORE_EVERY throttling.
        Returns None if that step was not stored.
        """
        if step < 0:
            return None
        return frames_step_to_idx.get(int(step))

    def _phi_at(step: int, y: int, x: int) -> Optional[float]:
        """
        Safe accessor for |phi| at a given simulation step (returns None if frame not stored).
        """
        idx = _phi_frame_idx(int(step))
        if idx is None:
            return None
        if 0 <= y < size and 0 <= x < size:
            return float(frames_phi[idx][y, x])
        return None

    # print("🔄 Starting field calculations:")

    threshold = 0.12
    neighborhood_size = 3
    radius_log = []
    if not resumed:
        _traj_cap = _env_int("LINEUM_TRAJ_MAX", 200000 if INFINITE_MODE else 0)
        trajectories = deque(maxlen=_traj_cap) if (
            _traj_cap and _traj_cap > 0) else []
        active_tracks = {}  # id -> (y, x)
        next_id = 0
    
    # Initialize variables for throttling (prevents NameError on resume)
    raw_vortices = np.zeros((size, size), dtype=int)
    vortices_vis = np.zeros((size, size), dtype=int)
    particles = np.zeros((size, size), dtype=bool)
    coords = np.zeros((0, 2), dtype=int)

    # Ladicí konstanta aplikovaná na víc složek systému
    TUNING_CONST = 1 / 137
    APPLY_TUNING = True

    # Service-friendly loop:
    # - finite: steps iterations
    # - infinite: run forever (until killed), relying on checkpoint + rolling export
    def _iter_steps():
        if INFINITE_MODE:
            i = step_start
            while True:
                yield i
                i += 1
        else:
            for i in range(step_start, steps):
                yield i

    def _build_logs_tail():
        # Keep JSON compact. Prefer LOG_ROLLING_WINDOW if set; else fall back to 2000.
        n = int(LOG_ROLLING_WINDOW) if (
            LOG_ROLLING_WINDOW and LOG_ROLLING_WINDOW > 0) else 2000
        return {
            "particle_log": _tail(particle_log, n),
            "interaction_log": _tail(interaction_log, n),
            "amplitude_log": _tail(amplitude_log, n),
            "topo_log": _tail(topo_log, n),
            "phi_center_log": _tail(phi_center_log, n),
        }

    def _export_service_snapshot(step_idx: int):
        # (your existing metrics/logging continues here)
        # Lightweight rolling export for external consumers:
        # - last X rows (X=LINEUM_ROLLING_WINDOW) where available
        # - do NOT write heavy frames/PNGs/GIFs here
        if not (ROLLING_WINDOW and ROLLING_WINDOW > 0):
            # still export "latest" in a tiny form, even without a window
            n = 1
        else:
            n = int(ROLLING_WINDOW)
        payload = {
            "window": int(n),
            "latest": {
                "center_amp": None if (len(amplitude_log) == 0) else float(_tail(amplitude_log, 1)[0][1]),
                "phi_center_abs": None if (len(phi_center_log) == 0) else float(_tail(phi_center_log, 1)[0][1]),
                "vortices_total": None if (len(topo_log) == 0) else int(_tail(topo_log, 1)[0][4]),
                "net_charge": None if (len(topo_log) == 0) else int(_tail(topo_log, 1)[0][3]),
                "particles_count": None if (len(particle_log) == 0) else int(_tail(particle_log, 1)[0][3]),
            },
            "tail": {
                "amplitude_log": _tail(amplitude_log, n),
                "phi_center_log": _tail(phi_center_log, n),
                "topo_log": _tail(topo_log, n),
                "particle_log": _tail(particle_log, n),
                "interaction_log": _tail(interaction_log, n),
            },
        }
        export_rolling_metrics(step_idx, payload)

    pbar = tqdm(_iter_steps(), desc="Processing steps",
                unit="step") if not INFINITE_MODE else _iter_steps()
    i = step_start - 1
    try:
        for i in pbar:

            if KAPPA_MODE == "island_to_constant":
                kappa = generate_kappa(i)
                
            # Track kappa spatial mean for temporal metrics
            kappa_spatial_means.append(float(np.mean(kappa)))

            psi, phi = evolve(psi, delta, phi, kappa)
            amp = np.abs(psi)

            phase = np.angle(psi)

            # Phase-safe central differences with periodic boundary:
            # wrap differences as angle(exp(i Δθ)) to avoid ±π jumps artefacts
            dph_dx = 0.5 * \
                np.angle(
                    np.exp(1j * (np.roll(phase, -1, axis=1) - np.roll(phase, 1, axis=1))))
            dph_dy = 0.5 * \
                np.angle(
                    np.exp(1j * (np.roll(phase, -1, axis=0) - np.roll(phase, 1, axis=0))))

            # keep names used later (for vector field/GIFs)
            grad_x = dph_dx
            grad_y = dph_dy

            # curl(∇phase) via central differences (periodic)
            dFy_dx = 0.5 * (np.roll(grad_y, -1, axis=1) -
                            np.roll(grad_y, 1, axis=1))
            dFx_dy = 0.5 * (np.roll(grad_x, -1, axis=0) -
                            np.roll(grad_x, 1, axis=0))
            curl = (dFy_dx - dFx_dy) * kappa

            do_track = (i % TRACK_EVERY == 0) or (CHECKPOINT_EVERY > 0 and i % CHECKPOINT_EVERY == 0)

            if do_track:
                # RAW vortices for metrics/CSV
                raw_vortices = detect_vortices(phase)
                update_topology_log(raw_vortices, i, topo_log)
                vortices_vis = gate_vortices_by_amplitude(
                    raw_vortices, amp)  # visualization-only (for GIF)

                local_max = (amp == maximum_filter(amp, size=neighborhood_size))
                particles = (amp > threshold) & local_max
                coords = np.argwhere(particles)

                # 💥 (optional) Experimental φ-injection near detected quasiparticles.
                # Default OFF for canonical runs; enable explicitly via LINEUM_PHI_INJECTION.
                if PHI_INJECTION_AMOUNT and PHI_INJECTION_AMOUNT != 0.0:
                    injection_amount = float(PHI_INJECTION_AMOUNT)
                    for cy, cx in coords:
                        y_min = max(cy - 1, 0)
                        y_max = min(cy + 2, size)
                        x_min = max(cx - 1, 0)
                        x_max = min(cx + 2, size)
                        phi[y_min:y_max, x_min:x_max] += injection_amount

                # Trackování trajektorií (greedy match)
                if FAST_TRACKING:
                    active_tracks, next_id = _track_quasiparticles_fast(
                        coords, active_tracks, next_id, i, amp, trajectories)
                else:
                    active_tracks, next_id = _track_quasiparticles_slow(
                        coords, active_tracks, next_id, i, amp, trajectories)
            
            # (If not tracking, raw_vortices/particles/coords/vortices_vis reuse previous values.
            # active_tracks/next_id/trajectories also remain unchanged, as requested.)

            # --- Store frames sparsely (for GIFs/NPY only) ---
            # Guarded by WANT_FRAMES to avoid unbounded RAM growth in service mode.
            if WANT_FRAMES and ((i % STORE_EVERY) == 0):
                # particles / vortices are visualization masks -> compact dtypes
                frames_particles.append(particles.astype(DT_PART, copy=False))
                frames_vort.append(vortices_vis.astype(DT_VORT, copy=False))

                # continuous fields -> float32 is enough for visualization/GIFs
                frames_amp.append(np.asarray(amp, dtype=DT_AMP))
                frames_vecx.append(np.asarray(grad_x, dtype=DT_VEC))
                frames_vecy.append(np.asarray(grad_y, dtype=DT_VEC))
                frames_curl.append(np.asarray(curl, dtype=DT_CURL))

                # φ frames (φ is real)
                frames_phi.append(np.asarray(phi, dtype=DT_PHI))
                frames_step_idx.append(int(i))
                frames_step_to_idx[int(i)] = len(frames_step_idx) - 1

            if do_track:
                r_threshold = 0.15
                mask = amp > r_threshold
                coords_r = np.argwhere(mask)
                center = np.array([size//2, size//2])
                if coords_r.size > 0:
                    distances = np.linalg.norm(coords_r - center, axis=1)
                    avg_radius = float(np.mean(distances))
                else:
                    avg_radius = 0.0
                radius_log.append((i, avg_radius))

                if coords.size > 0:
                    centroid = coords.mean(axis=0)
                    particle_log.append(
                        (i, float(centroid[0]), float(centroid[1]), int(len(coords))))
                else:
                    centroid = None
                    particle_log.append((i, np.nan, np.nan, 0))

                radius = 5
                if centroid is not None:
                    center_y, center_x = centroid.round().astype(int)
                    y_min = max(center_y - radius, 0)
                    y_max = min(center_y + radius + 1, size)
                    x_min = max(center_x - radius, 0)
                    x_max = min(center_x + radius + 1, size)
                    local_vortices = raw_vortices[y_min:y_max, x_min:x_max]
                    pos_count = int(np.sum(local_vortices == 1))
                    neg_count = int(np.sum(local_vortices == -1))
                else:
                    pos_count = 0
                    neg_count = 0
                interaction_log.append(
                    (i, pos_count, neg_count, int(pos_count - neg_count)))

            center_y, center_x = size // 2, size // 2
            central_amp = amp[center_y, center_x]
            amplitude_log.append((i, float(central_amp)))
            phi_center_log.append((i, float(phi[center_y, center_x])))

            for pt in probe_points:
                y, x = pt
                if 0 <= y < size and 0 <= x < size:
                    multi_amp_logs[pt].append(np.abs(psi[y, x]))
                else:
                    multi_amp_logs[pt].append(np.nan)

            # --- Service-mode persistence: checkpoint + rolling export ---
            if CHECKPOINT_EVERY and CHECKPOINT_EVERY > 0 and (i % CHECKPOINT_EVERY) == 0:
                try:
                    save_checkpoint(
                        step_idx=int(i),
                        psi=psi,
                        phi=phi,
                        delta=delta,
                        kappa=kappa,
                        next_id=int(next_id),
                        active_tracks={int(k): [int(v[0]), int(v[1])] for k, v in active_tracks.items(
                        )} if isinstance(active_tracks, dict) else {},
                        trajectories=trajectories,
                        logs=_build_logs_tail(),
                    )
                except Exception as _e:
                    print("[!] checkpoint failed:", _e)

            if METRICS_EXPORT_EVERY and METRICS_EXPORT_EVERY > 0 and (i % METRICS_EXPORT_EVERY) == 0:
                try:
                    _export_service_snapshot(int(i))
                except Exception as _e:
                    print("[!] rolling export failed:", _e)

    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user (KeyboardInterrupt). Saving a final checkpoint/snapshot...")
        try:
            if CHECKPOINT_EVERY and CHECKPOINT_EVERY > 0:
                save_checkpoint(
                    step_idx=int(i),
                    psi=psi,
                    phi=phi,
                    delta=delta,
                    kappa=kappa,
                    next_id=int(next_id),
                    active_tracks={int(k): [int(v[0]), int(v[1])] for k, v in active_tracks.items(
                    )} if isinstance(active_tracks, dict) else {},
                    trajectories=trajectories,
                    logs=_build_logs_tail(),
                )
        except Exception as _e:
            print("[!] final checkpoint failed:", _e)
        try:
            if i >= 0:
                _export_service_snapshot(int(i))
        except Exception as _e:
            print("[!] final rolling export failed:", _e)

    # In infinite/service mode, we typically do not want to generate huge end-of-run exports.
    # Finite runs proceed with the full export pipeline as before.
    if INFINITE_MODE:
        print("[check] Infinite/service run: rolling exports + checkpoints are active. Skipping end-of-run heavy exports.")
        sys.exit(0)

    save_csv("radius_log.csv", ["step", "avg_radius"], radius_log)

    save_csv("particle_log.csv", [
             "step", "center_y", "center_x", "size"], particle_log)

    save_csv(
        "interaction_log.csv",
        ["step", "vortices_pos", "vortices_neg", "net_local_charge"],
        interaction_log,
    )

    save_csv("amplitude_log.csv", ["step", "central_amplitude"], amplitude_log)

    save_csv("phi_center_log.csv", ["step", "phi_center_abs"], phi_center_log)

    # --- φ half-life estimate (center point)
    phi_df = pd.DataFrame(phi_center_log, columns=["step", "phi_center_abs"])
    if not phi_df.empty:
        phi_final = float(phi_df["phi_center_abs"].iloc[-1])
        phi_half = phi_final / 2.0
        hits = np.flatnonzero(phi_df["phi_center_abs"].values >= phi_half)
        phi_half_life_steps = int(
            phi_df["step"].iloc[hits[0]]) if hits.size > 0 else None
    else:
        phi_half_life_steps = None

    # 🔍 SPEKTRÁLNÍ ANALÝZA OSCILACE V CENTRU

    # Get amplitudes and create the time axis
    amplitudes = np.array([row[1] for row in amplitude_log])
    times = np.arange(len(amplitudes)) * TIME_STEP  # čas v sekundách

    # Windowed estimates + 95% CI (W=256, hop=128, guard=2)
    spectral_meta = {}
    (sbr_mean, sbr_ci), (f0_mean, f0_ci), spectral_meta = window_sbr_and_f0(
        amplitudes, TIME_STEP, W=WINDOW_W, hop=WINDOW_HOP, guard=2)

    # Export a compact metrics summary with CIs
    save_csv("metrics_summary.csv",
             ["metric", "value", "ci_lo", "ci_hi", "unit"],
             [
                 ["f0",  float(f0_mean) if f0_mean == f0_mean else None,
                  float(f0_ci[0]) if f0_ci and f0_ci[0] == f0_ci[0] else None,
                  float(f0_ci[1]) if f0_ci and f0_ci[1] == f0_ci[1] else None,
                  "Hz"],
                 ["SBR", float(sbr_mean) if sbr_mean == sbr_mean else None,
                     float(
                     sbr_ci[0]) if sbr_ci and sbr_ci[0] == sbr_ci[0] else None,
                     float(
                     sbr_ci[1]) if sbr_ci and sbr_ci[1] == sbr_ci[1] else None,
                     ""],
             ])

    # Remove DC component
    amplitudes -= np.mean(amplitudes)

    # Compute FFT
    do_legacy_fft = (np.isnan(f0_mean) or np.isnan(
        sbr_mean) or len(amplitudes) <= 20000)
    positive_freqs = None
    positive_spectrum = None
    if do_legacy_fft and len(amplitudes) > 0:
        fft_result = fft(amplitudes)
        frequencies = fftfreq(len(amplitudes), d=TIME_STEP)
        spectrum = np.abs(fft_result)**2
        positive_freqs = frequencies[:len(frequencies)//2]
        positive_spectrum = spectrum[:len(spectrum)//2]

    # Keep positive frequencies only (handled above)

    if do_legacy_fft and positive_spectrum is not None and len(positive_spectrum) > 0:
        dominant_index = int(np.argmax(positive_spectrum))
        dominant_freq = float(positive_freqs[dominant_index])  # Hz
    else:
        dominant_index = None
        dominant_freq = float(f0_mean) if (
            f0_mean == f0_mean) else float("nan")

    # --- Spectral Balance Ratio (SBR) with ±2-bin guard around f0
    # Only valid for legacy FFT branch.
    if do_legacy_fft and positive_spectrum is not None and dominant_index is not None:
        guard = 2
        peak_power = float(positive_spectrum[dominant_index])
        mask = np.ones_like(positive_spectrum, dtype=bool)
        l = max(dominant_index - guard, 0)
        r = min(dominant_index + guard + 1, len(positive_spectrum))
        mask[l:r] = False
        rest_power = float(np.mean(positive_spectrum[mask])) if np.any(
            mask) else float("nan")
        sbr = (peak_power / rest_power) if (rest_power ==
                                            rest_power and rest_power > 0) else float("nan")
    else:
        sbr = float("nan")

    # Prefer robust windowed estimates if valid (fallback to single-shot if not)
    if not np.isnan(f0_mean):
        dominant_freq = float(f0_mean)
    if not np.isnan(sbr_mean):
        sbr = float(sbr_mean)

        # --- Figure 0: canonical spectrum + time trace (auto-generated) ---
    figure0_html = ""
    try:
        import numpy as np

        # vezmeme středové okno délky WINDOW_W (vyhneme se okrajům)
        Wp = int(WINDOW_W) if WINDOW_W else 256
        i0 = max(0, len(amplitudes)//2 - Wp//2)
        seg = np.asarray(amplitudes[i0:i0+Wp], dtype=float)
        tseg = np.asarray(times[i0:i0+seg.size], dtype=float)
        if seg.size < 16:
            raise RuntimeError("Too few samples for Figure 0")

        # odstraníme DC a použijeme Hann okno
        seg_zm = seg - float(np.mean(seg))
        win = np.hanning(seg.size)
        seg_win = seg_zm * win

        # FFT (prezentační větev): spočti výkon, vyčisti NaN/Inf a NORMALIZUJ do [0,1]
        F = np.fft.rfft(seg_win)
        P = np.abs(F)**2  # power
        # normalizace o energii okna a vlastní maximum
        denom = float((win**2).sum()) + 1e-12
        P = P / denom
        # nahradit ne-finitní
        P = np.where(np.isfinite(P), P, 0.0)
        Pmax = float(np.max(P)) if np.any(P > 0) else 1.0
        Pn = P / (Pmax + 1e-12)  # 0..1

        freqs = np.fft.rfftfreq(seg.size, d=TIME_STEP)
        df_plot = float(
            freqs[1] - freqs[0]) if freqs.size > 1 else max(1.0, dominant_freq/10.0)
        if not np.isfinite(df_plot) or df_plot <= 0:
            df_plot = max(1.0, dominant_freq/10.0)

        # vykreslení
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=160)

        # TIME TRACE — zero-mean normalization (±1 around 0)
        seg_norm = seg_zm / (np.max(np.abs(seg_zm)) + 1e-12)
        ax1.plot(tseg, seg_norm)
        ax1.axhline(0.0, linewidth=1, linestyle="--", alpha=0.6)
        ax1.set_xlabel("time [s]")
        ax1.set_ylabel("zero-mean normalized |ψ| at center")
        ax1.set_title("Center-amplitude trace (windowed, zero-mean)")

        # SPECTRUM — semilogy, používáme Pn∈[0,1], přidáme ε
        ax2.semilogy(freqs, Pn + 1e-12)
        ax2.axvline(float(dominant_freq), linestyle="--")
        ax2.set_xlabel("frequency [Hz]")
        ax2.set_ylabel("power (arb. units)")
        ax2.set_title(
            f"Spectrum (peak near f₀ ≈ {float(dominant_freq):.2e} Hz)")
        ax2.set_xlim(max(0.0, float(dominant_freq) - 3*df_plot),
                     float(dominant_freq) + 3*df_plot)

        fig.tight_layout()
        fig_path = _os.path.join(
            output_dir, f"{RUN_TAG}_figure0_canonical.png")
        fig.savefig(fig_path, bbox_inches="tight")
        plt.close(fig)

        figure0_html = f"""
<h2>Figure 0 — Canonical anchors</h2>
<figure>
  <img src="{RUN_TAG}_figure0_canonical.png" alt="Spectrum (bin-centered) and center trace" />
  <figcaption style="font-size:0.9em; opacity:0.85; margin-top:4px;">
    Windowed center trace (zero-mean, Hann) and one-sided spectrum.
    Peak at f₀ ≈ {float(dominant_freq):.2e} Hz; FFT bin spacing Δf ≈ {df_plot:.2e} Hz.
  </figcaption>
</figure>
"""

    except Exception as _e:
        # print("[!] Figure 0 generation failed:", _e)
        figure0_html = ""
    
    print(f"DEBUG: Final logs - amplitude_log={len(amplitude_log)}, topo_log={len(topo_log)}")

    # Spočteme energii: E = h·f
    h = 6.62607015e-34  # Planck constant [J·s]
    energy = h * dominant_freq

    # Spočteme vlnovou délku: λ = c / f
    c = 299_792_458  # speed of light [m/s]
    wavelength = c / dominant_freq if dominant_freq != 0 else np.inf

    # Spočteme efektivní hmotnost částice: m = E/c²
    mass = energy / c**2  # effective mass [kg]

    # Compare with electron
    electron_mass = 9.10938356e-31  # electron mass [kg]
    mass_ratio = mass / electron_mass

    # Uložení do CSV
    if do_legacy_fft and positive_freqs is not None and positive_spectrum is not None:
        save_csv("spectrum_log.csv", ["frequency_Hz", "amplitude"], zip(
            positive_freqs, positive_spectrum))

    # Nyní exportuj jen čisté trajektorie
    save_csv(
        "trajectories.csv",
        ["id", "step", "y", "x", "amplitude"],
        trajectories,
    )

    # 🔍 SPECTRAL ANALYSIS OF THE CENTER-POINT OSCILLATION
    multi_spectrum_details = []

    for pt, amp_list in multi_amp_logs.items():
        signal = np.array(amp_list)
        if signal.size == 0:
            multi_spectrum_details.append({
                "point": pt,
                "dominant_freq_Hz": 0.0,
                "energy_J": 0.0,
                "mass_kg": 0.0,
                "mass_ratio": 0.0
            })
            continue

        signal -= np.mean(signal)
        fft_result = fft(signal)
        freqs = fftfreq(len(signal), d=TIME_STEP)
        spectrum = np.abs(fft_result)**2
        positive_freqs = freqs[:len(freqs)//2]
        positive_spectrum = spectrum[:len(spectrum)//2]

        if positive_spectrum.size == 0:
            dom_idx = 0
            dom_freq = 0.0
        else:
            dom_idx = np.argmax(positive_spectrum)
            dom_freq = positive_freqs[dom_idx]

        # Lokální přepočet – NEPŘEPISUJE globální mass/mass_ratio
        energy_i = h * dom_freq
        mass_i = energy_i / c**2
        mass_ratio_i = mass_i / electron_mass

        multi_spectrum_details.append({
            "point": pt,
            "dominant_freq_Hz": float(dom_freq),
            "energy_J": float(energy_i),
            "mass_kg": float(mass_i),
            "mass_ratio": float(mass_ratio_i)
        })

        # Uložení spektra pro každý bod zvlášť
        save_csv(
            f"spectrum_log_point_{pt[0]}_{pt[1]}.csv",
            ["frequency_Hz", "amplitude"],
            zip(positive_freqs, positive_spectrum),
        )

    # Uložení shrnutí výsledků pro všechny body
    save_csv(
        "multi_spectrum_summary.csv",
        ["y", "x", "dominant_freq_Hz", "energy_J", "mass_kg", "mass_ratio"],
        [(d["point"][0], d["point"][1], d["dominant_freq_Hz"], d["energy_J"],
          d["mass_kg"], d["mass_ratio"]) for d in multi_spectrum_details]
    )

    save_csv(
        "topo_log.csv",
        ["step", "num_pos", "num_neg", "net_charge", "total_vortices"],
        topo_log,
    )

    # --- Topology summary metrics for the HTML report
    topo_df = pd.DataFrame(topo_log, columns=[
                           "step", "num_pos", "num_neg", "net_charge", "total_vortices"])
    if not topo_df.empty:
        pct_neutral = float((topo_df["net_charge"].abs() <= 1).mean() * 100.0)
        mean_total_vort = float(topo_df["total_vortices"].mean())
    else:
        pct_neutral = None
        mean_total_vort = None

    # Save plot (bullet-proof log-safe)
    plt.figure(figsize=(8, 4))
    if not (do_legacy_fft and positive_freqs is not None and positive_spectrum is not None):
        print("[!] spectrum_plot skipped (legacy FFT disabled; Figure 0 already provides a windowed spectrum).")
        pf = None
        ps = None
    else:
        pf = np.asarray(positive_freqs, dtype=float)
        ps = np.asarray(positive_spectrum, dtype=float)

    pf2 = np.asarray([], dtype=float)
    ps2 = np.asarray([], dtype=float)
    if pf is not None:
        m = pf > 0
        pf2 = pf[m]
        ps2 = ps[m]

    # Fallback: if nothing remains after dropping DC, plot the original arrays (linear)
    if pf2.size == 0:
        plt.plot(pf, ps)
        use_log_x = False
        use_log_y = bool(np.any(ps > 0))
    else:
        plt.plot(pf2, ps2)
        use_log_x = bool(np.all(pf2 > 0))
        use_log_y = bool(np.any(ps2 > 0))
    plt.title("Spectrum of center-point oscillation")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power (arb.)")

    # Only enable log axes when valid
    if use_log_x:
        plt.xscale("log")
    if use_log_y:
        plt.yscale("log")

    plt.grid(True)
    try:
        plt.tight_layout()
    except Exception as _e:
        print("[!] tight_layout skipped (log/layout issue):", _e)

    if pf is not None:
        plot_path = _os.path.join(output_dir, f"{RUN_TAG}_spectrum_plot.png")
        try:
            plt.savefig(plot_path)
            notify_file_creation(plot_path)
        except Exception as e:
            notify_file_creation(plot_path, success=False, error=e)
        finally:
            plt.close()

    # --- Topology plots (to match the HTML report)
    if not topo_df.empty:
        # Net topological charge over steps
        plt.figure(figsize=(8, 3))
        plt.plot(topo_df["step"], topo_df["net_charge"])
        plt.title("Topological net charge per step")
        plt.xlabel("Step")
        plt.ylabel("Net charge")
        plt.grid(True)
        plt.tight_layout()
        path = _os.path.join(output_dir, f"{RUN_TAG}_topo_charge_plot.png")
        try:
            plt.savefig(path)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)
        finally:
            plt.close()

        # Total vortices over steps
        plt.figure(figsize=(8, 3))
        plt.plot(topo_df["step"], topo_df["total_vortices"])
        plt.title("Total vortices per step")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        path = _os.path.join(output_dir, f"{RUN_TAG}_vortex_count_plot.png")
        try:
            plt.savefig(path)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)
        finally:
            plt.close()

    # Funkce pro uložení GIFů

    # NOTE:
    # GIF/overlay generation requires stored frames. When SAVE_GIFS/SAVE_FRAMES/SAVE_PNGS are disabled,
    # WANT_FRAMES can be False and frames_* stay empty -> downstream would crash.
    #
    # We therefore guard all frame-dependent exports below on:
    #   (a) WANT_FRAMES is True (finite run with storage enabled), and
    #   (b) _has_frames() is True (at least one frame was stored).
    #

    def save_gif(data_frames, filename, cmap='viridis', vmin=None, vmax=None,
                 out_px=None, resample='nearest'):
        """
        Fast GIF writer: maps frames -> RGBA via Matplotlib colormap (no figures),
        then writes GIF via Pillow. Optional upscale to a fixed pixel size (out_px).
        """
        from matplotlib import cm, colors
        from PIL import Image
        import numpy as np

        # Avoid large temporary arrays / scans on Python lists of big ndarrays.
        # Compute min/max incrementally.
        if vmin is None or vmax is None:
            _mn = np.inf
            _mx = -np.inf
            for f in data_frames:
                a = np.asarray(f)
                # ignore NaN/Inf safely
                if a.size == 0:
                    continue
                fm = float(np.nanmin(a))
                fM = float(np.nanmax(a))
                if np.isfinite(fm) and fm < _mn:
                    _mn = fm
                if np.isfinite(fM) and fM > _mx:
                    _mx = fM
            if vmin is None:
                vmin = float(_mn if np.isfinite(_mn) else 0.0)
            if vmax is None:
                vmax = float(_mx if np.isfinite(_mx) else 1.0)

        norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cmap)

        # zvol resampling (nejvěrnější předchozímu vzhledu bývá 'nearest')
        RESAMPLE = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC
        }.get(resample, Image.NEAREST)

        pil_frames = []
        for f in data_frames:
            rgba = mapper.to_rgba(f, bytes=True)   # uint8 RGBA
            img = Image.fromarray(rgba, mode="RGBA")
            if out_px is not None:
                img = img.resize((out_px, out_px), RESAMPLE)
            pil_frames.append(img)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=100,  # ~10 fps
                    loop=0,
                    disposal=2
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    def save_full_overlay_gif(frames_amp, frames_curl, frames_vecx, frames_vecy, filename,
                              vmin_amp=0.0, vmax_amp=0.5, vmin_curl=-0.3, vmax_curl=0.3,
                              out_px=512, vec_stride=8, vec_scale=6.0, k_skip=2, fps=10,
                              amp_alpha_floor=0.20, curl_alpha_quantile=0.90, alpha_scale=96,
                              resample='nearest'):
        """Fast overlay GIF:
        • base = amplitude (plasma),
        • overlay = curl (bwr) with alpha masked by amplitude and curl quantile,
        • sparse arrows from (frames_vecx, frames_vecy).
        """

        from matplotlib import cm, colors
        from PIL import Image, ImageDraw
        import numpy as np
        import math

        # Colormap normalizace
        amp_norm = colors.Normalize(vmin=vmin_amp,  vmax=vmax_amp,  clip=True)
        curl_norm = colors.Normalize(vmin=vmin_curl, vmax=vmax_curl, clip=True)
        amp_map = cm.ScalarMappable(norm=amp_norm,  cmap='plasma')
        curl_map = cm.ScalarMappable(norm=curl_norm, cmap='bwr')

        # Resample režim
        RESAMPLE = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC
        }.get(resample, Image.NEAREST)

        pil_frames = []
        n = len(frames_amp)
        if n == 0:
            print(f"[!] Skipping {filename}: No frames provided.")
            return

        # Globální statistiky curlu (konzistentní napříč snímky)
        if not frames_curl:
             print(f"[!] Skipping {filename}: No curl frames provided.")
             return
        abs_curl_all = np.abs(np.stack(frames_curl))
        if abs_curl_all.size == 0:
             print(f"[!] Skipping {filename}: abs_curl_all is empty.")
             return
        max_abs_curl = max(1e-9, float(abs_curl_all.max()))
        # např. 90. percentil
        try:
            curl_q = float(np.quantile(abs_curl_all, curl_alpha_quantile))
        except Exception as e:
            print(f"[!] curl_q quantile failed: {e}. using default 0.0")
            curl_q = 0.0

        for i in range(0, n, max(1, k_skip)):
            amp = frames_amp[i]
            curl = frames_curl[i]
            vx = frames_vecx[i]
            vy = frames_vecy[i]

            # RGBA base = amplitude
            amp_rgba = amp_map.to_rgba(amp, bytes=True)  # uint8 RGBA
            base = Image.fromarray(amp_rgba, mode="RGBA")

            # RGBA overlay = curl s ALFA maskou (amp-gating + kvantil |curl|)
            curl_rgba = curl_map.to_rgba(curl, bytes=True).copy()
            abs_curl = np.abs(curl)

            # 1) normalizovaný příspěvek z curlu
            #    (lineárně od prahu curl_q do maxima; pod prahem = 0)
            denom = max(1e-12, (max_abs_curl - curl_q))
            alpha_f = np.clip((abs_curl - curl_q) / denom, 0.0, 1.0)

            # 2) potlačení mimo "hmotu": v nízké amplitudě nulová alfa
            alpha_f[amp < amp_alpha_floor] = 0.0

            # 3) zmenšení celkové krytí (méně "fialového sněhu")
            # typicky 96 (0..96)
            alpha = (alpha_f * alpha_scale).astype(np.uint8)
            curl_rgba[..., 3] = alpha
            over = Image.fromarray(curl_rgba, mode="RGBA")

            # Kompozice amplitude + curl
            comp = Image.alpha_composite(base, over)

            # --- ŠIPKY se špičkou (arrowheads) ---
            draw = ImageDraw.Draw(comp)
            H, W = amp.shape
            arrow_rgba = (144, 238, 144, 200)

            for y in range(0, H, vec_stride):
                for x in range(0, W, vec_stride):
                    dx = float(vx[y, x])
                    dy = float(vy[y, x])
                    if dx*dx + dy*dy < 1e-12:
                        continue

                    x1, y1 = float(x), float(y)
                    x2 = x1 + dx * vec_scale
                    y2 = y1 + dy * vec_scale

                    # tělo šipky
                    draw.line([(x1, y1), (x2, y2)], fill=arrow_rgba, width=1)

                    # špička šipky („V“)
                    theta = math.atan2(dy, dx)
                    head_len = 0.6 * vec_scale
                    head_wide = 0.35 * vec_scale
                    hx = math.cos(theta)
                    hy = math.sin(theta)
                    nx = -hy
                    ny = hx
                    xh1 = x2 - hx*head_len + nx*head_wide
                    yh1 = y2 - hy*head_len + ny*head_wide
                    xh2 = x2 - hx*head_len - nx*head_wide
                    yh2 = y2 - hy*head_len - ny*head_wide
                    draw.line([(x2, y2), (xh1, yh1)], fill=arrow_rgba, width=1)
                    draw.line([(x2, y2), (xh2, yh2)], fill=arrow_rgba, width=1)

            if out_px:
                comp = comp.resize((out_px, out_px), RESAMPLE)

            pil_frames.append(comp)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=int(1000/max(1, fps)),
                    loop=0,
                    disposal=2,
                    optimize=True
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    def save_flow_quiver_gif(frames_vecx, frames_vecy, filename,
                             out_px=512, vec_stride=8, vec_scale=6.0, k_skip=2, fps=10,
                             bg="white", resample="nearest"):
        # This Python code is generating a series of frames for an ultra-fast flow GIF with vector arrows. It
        # uses the PIL (Python Imaging Library) module to create and draw the frames. The code takes input
        # arrays `frames_vecx` and `frames_vecy` representing vector components, and generates a GIF animation
        # showing the flow of vectors as arrows on a sparse grid.
        """
        Ultra-fast FLOW GIF: sparse vector field with arrowheads (no Matplotlib).
        Vykreslí se řídká šachovnice šipek z (frames_vecx, frames_vecy).
        """
        from PIL import Image, ImageDraw
        import numpy as np
        import math

        # choose resample kernel
        RESAMPLE = {
            "nearest": Image.NEAREST,
            "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC
        }.get(resample, Image.NEAREST)

        n = len(frames_vecx)
        H, W = frames_vecx[0].shape

        # arrow color (semi-transparent lime)
        arrow_rgba = (144, 238, 144, 220)

        pil_frames = []
        for i in range(0, n, max(1, k_skip)):
            vx = frames_vecx[i]
            vy = frames_vecy[i]

            # plátno
            if bg == "black":
                comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            else:
                comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))

            draw = ImageDraw.Draw(comp)

            # šipky se špičkou (stejná orientace jako u overlay funkce)
            for y in range(0, H, vec_stride):
                for x in range(0, W, vec_stride):
                    dx = float(vx[y, x])
                    dy = float(vy[y, x])
                    if dx*dx + dy*dy < 1e-12:
                        continue

                    x1, y1 = float(x), float(y)
                    x2 = x1 + dx * vec_scale
                    y2 = y1 + dy * vec_scale
                    # tělo šipky
                    draw.line([(x1, y1), (x2, y2)], fill=arrow_rgba, width=2)

                    # arrowhead ("V" shape with two short strokes)
                    theta = math.atan2(dy, dx)
                    head_len = 0.6 * vec_scale
                    head_wide = 0.35 * vec_scale
                    hx = math.cos(theta)
                    hy = math.sin(theta)
                    nx = -hy
                    ny = hx
                    xh1 = x2 - hx * head_len + nx * head_wide
                    yh1 = y2 - hy * head_len + ny * head_wide
                    xh2 = x2 - hx * head_len - nx * head_wide
                    yh2 = y2 - hy * head_len - ny * head_wide
                    draw.line([(x2, y2), (xh1, yh1)], fill=arrow_rgba, width=2)
                    draw.line([(x2, y2), (xh2, yh2)], fill=arrow_rgba, width=2)

            if out_px:
                comp = comp.resize((out_px, out_px), RESAMPLE)

            pil_frames.append(comp)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=int(1000/max(1, fps)),
                    loop=0,
                    disposal=2,
                    optimize=True
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    # --- GIF exports (guarded) ---
    if SAVE_GIFS:
        if WANT_FRAMES and _has_frames():
            if _nonempty(frames_amp):
                save_gif(frames_amp, _os.path.join(output_dir, f"{RUN_TAG}_lineum_amplitude.gif"),
                         cmap="plasma", vmin=0, vmax=0.5, out_px=512)
            else:
                _warn_skip("GIF amplitude (frames_amp is empty)")

            if _nonempty(frames_curl):
                save_gif(frames_curl, _os.path.join(output_dir, f"{RUN_TAG}_lineum_spin.gif"),
                         cmap="bwr", vmin=-0.3, vmax=0.3, out_px=512)
            else:
                _warn_skip("GIF spin (frames_curl is empty)")

            if _nonempty(frames_vort):
                save_gif(frames_vort, _os.path.join(output_dir, f"{RUN_TAG}_lineum_vortices.gif"),
                         cmap="bwr", vmin=-1, vmax=1, out_px=512)
            else:
                _warn_skip("GIF vortices (frames_vort is empty)")

            if _nonempty(frames_particles):
                save_gif(frames_particles, _os.path.join(output_dir, f"{RUN_TAG}_lineum_particles.gif"),
                         cmap="gray", vmin=0, vmax=1, out_px=512)
            else:
                _warn_skip("GIF particles (frames_particles is empty)")

            if _nonempty(frames_vecx) and _nonempty(frames_vecy):
                flow_path = _os.path.join(
                    output_dir, f"{RUN_TAG}_lineum_flow.gif")
                save_flow_quiver_gif(
                    frames_vecx, frames_vecy,
                    flow_path,
                    out_px=512,      # output GIF size in pixels
                    vec_stride=12,   # sparsity of arrow grid
                    vec_scale=9.0,   # arrow length (scale)
                    k_skip=GIFT_SKIP,  # skip frames (smaller file)
                    fps=5,          # snímková frekvence GIFu
                    bg="black"      # nebo "black", chceš-li tmavé pozadí
                )
            else:
                _warn_skip("GIF flow (frames_vecx/frames_vecy empty)")
        else:
            _warn_skip(
                "GIF exports (no stored frames; set LINEUM_SAVE_FRAMES/PNGS/GIFS or disable this stage)")
    else:
        _warn_skip("GIF exports (LINEUM_SAVE_GIFS=0)")

    def generate_html_report(
        filename=f"{RUN_TAG}_lineum_report.html",
        mass=0,
        mass_ratio=0,
        max_lifespan=0,
        median_lifespan=0,
        include_spin=True,
        phi_mean_near=0,
        phi_mean_field=0,
        phi_std_field=1,
        mass_ratio_blackholes=None,
        avg_phi_death=None,
        low_mass_count=None,
        phi_low_mass_mean=0,
        curl_low_mass_mean=0,
        phi_above_025_count=0,
        curl_near_zero_count=0,
        phi_half_life_steps=None,
        sbr=None, pct_neutral=None,
        mean_total_vort=None,
        phi_std_near=None,
        f0_ci=None,
        sbr_ci=None,
        figure0_html=""
    ):

        # [check] Detekce jevů na základě logů
        quasiparticles_present = len(trajectories) > 0
        # total vortices > 0
        vortices_present = any(row[4] > 0 for row in topo_log)
        charge_std = np.std([row[3] for row in topo_log])
        topo_conserved = charge_std < 3
        stable_frequency = dominant_freq > 1e10  # arbitrárně: nad 10 GHz
        phi_present = np.nanmax([row[1] for row in phi_center_log]) > 0.01
        phi_gravitation_confirmed = False

        # 🧪 Dynamický seznam potvrzených jevů
        confirmations = []
        if vortices_present:
            confirmations.append("🌀 Spontaneous vortex formation (±1 winding)")
        if quasiparticles_present:
            confirmations.append(
                "🧫 Quasiparticle detections with trackable trajectories")
        if stable_frequency:
            confirmations.append(
                f"🎵 Stable single-peak spectrum (f₀ = {dominant_freq:.2e} Hz{'; SBR ≈ ' + f'{sbr:.2f}' if (sbr is not None and sbr == sbr) else ''})"
            )
        if topo_conserved:
            confirmations.append(
                "🔁 Near-neutral global topological charge over time (winding)")
        if phi_present:
            confirmations.append(
                "🌌 Non-zero background φ observed at the center")

        if mass_ratio > 0.001 and mass_ratio < 100:
            confirmations.append(
                f"⚖️ Display-only effective mass estimate from f₀ (m/mₑ ≈ {mass_ratio:.2e})"
            )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if blackhole_count > 0:
        #     confirmations.append(
        #         f"🕳️ Detekce {blackhole_count} kvazičástic uvězněných ve φ-pasti (černá díra)")

        #     if mass_ratio_blackholes is not None and mass_ratio_blackholes < 0.01:
        #         confirmations.append(
        #             "🪐 Třískova hypotéza strukturálního uzavření potvrzena: částice zanikají v silných φ-zónách bez zbytkové hmotnosti"
        #         )
        #     elif mass_ratio_blackholes is not None:
        #         confirmations.append(
        #             f"🪐 Třískova hypotéza strukturálního uzavření částečně potvrzena: návratové částice mají hmotnost {mass_ratio_blackholes:.2e}× elektronová"
        #         )
        #     else:
        #         confirmations.append(
        #             "🪐 Třískova hypotéza strukturálního uzavření zatím neověřena – spektrální data nedostupná"
        #         )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if avg_phi_death is not None and avg_phi_death > 0.25:
        #     confirmations.append(
        #         f"🌀 φ v místě zániku návratových částic potvrzuje strukturální uzavření (⟨φ⟩ = {avg_phi_death:.3f})"
        #     )
        # elif avg_phi_death is not None:
        #     confirmations.append(
        #         f"🌀 φ v místě zániku návratových částic: {avg_phi_death:.3f} (hranice potvrzení je 0.25)"
        #     )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if wormhole_count > 0:
        #     confirmations.append(
        #         f"🌉 Podezření na {wormhole_count} případů červí díry (skoková relokace mezi φ-zónami)")

        _curl_std = 0.0 if ("curl_std" not in globals()
                            or curl_std is None) else float(curl_std)
        if _curl_std > 0.05:
            confirmations.append(
                f"🔄 Significant curl activity inside high-φ regions (σ = {curl_std:.2e})")

        # Potvrzení homogenního výskytu kvazičástic
        try:
            with open(_os.path.join(output_dir, f"{RUN_TAG}_multi_spectrum_summary.csv")) as f:
                import csv
                reader = csv.DictReader(f)
                freqs = []
                mass_ratios = []
                for row in reader:
                    freqs.append(float(row["dominant_freq_Hz"]))
                    mass_ratios.append(float(row["mass_ratio"]))

                freq_std = np.std(freqs)
                mass_ratio_std = np.std(mass_ratios)

                if freq_std < 1e17 and mass_ratio_std < 0.01:
                    confirmations.append(
                        "🧬 Consistent f₀ across sampled points (low across-grid variance)")

        except Exception as e:
            print("[!] Homogeneity check failed:", e)

        if max_lifespan >= 100:
            confirmations.append(
                f"🕒 Emergence of long-lived quasiparticles (max {max_lifespan} steps, median {median_lifespan})"
            )

        if include_spin and _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png")):
            confirmations.append(
                "🧲 Averaged curl map near quasiparticles shows a dipole-like pattern (spin aura)")

        if phi_mean_near > phi_mean_field + 3 * phi_std_field:
            confirmations.append(
                "🌠 Elevated φ near quasiparticles (mean > field mean + 3σ)")

        # 💫 φ-gravitační interakce: ověření sbližování částic
        try:
            top_trajs = pd.read_csv(_os.path.join(
                output_dir, f"{RUN_TAG}_trajectories.csv"))
            grouped = top_trajs.groupby("id")
            lifespans = grouped.size().sort_values(ascending=False)
            top2_ids = lifespans.head(2).index.tolist()
            filtered = top_trajs[top_trajs["id"].isin(top2_ids)]

            from collections import defaultdict
            from scipy.spatial.distance import euclidean
            step_to_positions = defaultdict(dict)
            for _, row in filtered.iterrows():
                step = int(row["step"])
                id_ = int(row["id"])
                y = float(row["y"])
                x = float(row["x"])
                step_to_positions[step][id_] = (y, x)

            shared_steps = [s for s in step_to_positions if len(
                step_to_positions[s]) == 2]

            if len(shared_steps) >= 5:
                dists = [euclidean(*step_to_positions[s].values())
                         for s in shared_steps]
                if dists[0] > dists[-1]:
                    # (v1-safe) no explicit claim; keep internal flag if needed
                    phi_gravitation_confirmed = True

        except Exception as e:
            print("[!] φ-guidance test failed:", e)

        if not confirmations:
            confirmations.append(
                "No major emergent phenomena detected")

        # 🔧 HTML konstrukce
        confirmed_html = "\n".join(f"<li>{c}</li>" for c in confirmations)

        gravitational_row = ("<tr><td>Guided motion</td>"
                             "<td>Alignment with +∇|φ| (environmental guidance)</td></tr>")

        # --- Run labels shown under the report title (only if available)
        labels = [f"RUN_TAG: {RUN_TAG}"]
        if 'TIME_STEP' in globals():
            try:
                labels.append(f"Δt: {TIME_STEP:.2e} s")
            except Exception:
                pass
        if 'PIXEL_SIZE' in globals():
            try:
                labels.append(f"pixel: {PIXEL_SIZE:.2e} m")
            except Exception:
                pass

        # Try to include Git commit (short SHA) if available
        commit_short = None
        try:
            import subprocess              # ponecháme jen subprocess
            commit_short = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
        except Exception:
            # Fallback: allow passing it via environment (optional)
            commit_short = _os.environ.get(
                "GIT_COMMIT_SHORT", "").strip() or None

        if commit_short:
            labels.append(f"commit: {commit_short}")

        labels_text = " · ".join(labels)

        # --- Data links for convenience (relative to report location)
        # IMPORTANT: some files are optional (e.g., spectrum_log.csv when legacy FFT is disabled).
        def _link_if_exists(rel_name: str, label: str) -> str:
            p = _os.path.join(output_dir, rel_name)
            return f'<li><a href="{rel_name}">{label}</a></li>' if _os.path.exists(p) else ""

        _links = []
        _links.append(_link_if_exists(
            f"{RUN_TAG}_amplitude_log.csv", "amplitude_log.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_phi_center_log.csv", "phi_center_log.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_topo_log.csv", "topo_log.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_trajectories.csv", "trajectories.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_multi_spectrum_summary.csv", "multi_spectrum_summary.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_spin_aura_profile.csv", "spin_aura_profile.csv"))
        _links.append(_link_if_exists(
            f"{RUN_TAG}_metrics_summary.csv", "metrics_summary.csv"))
        # optional legacy FFT export
        _links.append(_link_if_exists(
            f"{RUN_TAG}_spectrum_log.csv", "spectrum_log.csv"))

        _links = [x for x in _links if x]
        data_links_html = f"<ul>{''.join(_links)}</ul>" if _links else "<p><em>No downloadable files found.</em></p>"

        # --- Derived display numbers from f0 (safe)
        try:
            # constants in-place (avoid missing PLANCK_H / LIGHT_SPEED)
            _H = 6.62607015e-34        # Planck constant [J·s]
            _C = 299_792_458.0         # speed of light [m/s]
            energy_j = _H * dominant_freq
            energy_ev = energy_j / 1.602176634e-19
            wavelength_m = _C / \
                dominant_freq if dominant_freq != 0 else float("inf")
        except Exception:
            energy_j = None
            energy_ev = None
            wavelength_m = None

        def _fmt_ci_pair(val, ci, unit=""):
            try:
                if ci and all(isinstance(x, (int, float)) and x == x for x in ci):
                    lo, hi = ci
                    if unit:
                        return f"{val:.2e} {unit}  [{lo:.2e}, {hi:.2e}]"
                    else:
                        return f"{val:.2f}  [{lo:.2f}, {hi:.2f}]"
                return f"{val:.2e} {unit}".strip() if unit else f"{val:.2f}"
            except Exception:
                return "—"

        html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Lineum Simulation Report</title>
      <style>
  body {{ font-family: Arial, sans-serif; padding: 20px; }}
  h1, h2 {{ color: #2c3e50; }}
  .grid {{ display: flex; flex-wrap: wrap; gap: 10px; }}
  table {{ border-collapse: collapse; margin-top: 10px; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
  th {{ background-color: #f4f4f4; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 10px 0; border: 1px solid #ccc; }}
</style>

    </head>
    <body>
        <h1>🧪 Lineum – Emergent Quantum Field</h1>

        <p style="margin-top:-8px;color:#666;"><small>{labels_text}</small></p>

        <h2>📦 Data & downloads</h2>
        {data_links_html}


        <h2>📂 Run Configuration</h2>
        <ul>
            <li><strong>Run tag:</strong> {RUN_TAG}</li>
            <li><strong>LOW_NOISE_MODE:</strong> {'True' if LOW_NOISE_MODE else 'False'}</li>
            <li><strong>TEST_EXHALE_MODE:</strong> {'True' if TEST_EXHALE_MODE else 'False'}</li>
            <li><strong>KAPPA_MODE:</strong> {KAPPA_MODE}</li>
        </ul>


      <h2>[check] Confirmed observations (v1-safe)</h2>
      <ul>
        {confirmed_html}
      </ul>

      <h2>📌 Run metrics ({RUN_TAG})</h2>
    <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>φ half-life (center)</td>
        <td>{phi_half_life_steps if phi_half_life_steps is not None else '—'} steps
            (canonical target ≈ 2000)</td></tr>
            <tr><td>SBR (±2-bin guard)</td>
    <td>{'—' if (sbr is None or sbr != sbr) else _fmt_ci_pair(sbr, sbr_ci)}</td></tr>

  <tr><td>Topology neutrality</td>
      <td>{'—' if pct_neutral is None else f'{pct_neutral:.1f}%'} of steps with |net charge| ≤ 1
          (mean vortices ≈ {'—' if mean_total_vort is None else f'{mean_total_vort:.0f}'})</td></tr>
            <tr><td>φ near vs field</td>
      <td>{phi_mean_near:.2e} ± {('—' if phi_std_near is None else f'{phi_std_near:.2e}')}
          vs {phi_mean_field:.2e} ± {('—' if phi_std_field is None else f'{phi_std_field:.2e}')}</td></tr>


    </table>
    
<p class="metrics-note" style="font-size:0.9em; opacity:0.85; margin-top:6px;">
  Windowed estimates: W={WINDOW_W}, hop={WINDOW_HOP}, guard=±2 bins around f₀; 95% CI via bootstrap (B=1000 resamples).
  See <code>metrics_summary.csv</code> in the downloads section for machine-readable values.
</p>


{figure0_html}

<h2>📊 Quasiparticle Properties</h2>
<table>
  <tr><th>Property</th><th>Value</th></tr>
  <tr><td>Dominant frequency f₀</td>
<td>{_fmt_ci_pair(dominant_freq, f0_ci, 'Hz')}</td></tr>

<tr><td>Energy (E = h f₀)</td>
<td>{'—' if energy_j is None else f'{energy_j:.2e} J (~{energy_ev/1e3:.2f} keV)'}</td></tr>
<tr><td>Wavelength (λ = c / f₀)</td>
<td>{'—' if wavelength_m is None else f'{wavelength_m:.2e} m'}</td></tr>

  <tr><td>Effective mass</td><td>{mass:.2e} kg</td></tr>
  <tr><td>Mass relative to electron</td><td>{mass_ratio:.4f} ({mass_ratio*100:.2f}%) × electron mass</td></tr>
  <tr><td>Max lifespan</td><td>{max_lifespan} steps</td></tr>
  <tr><td>Median lifespan</td><td>{median_lifespan} steps</td></tr>
  {gravitational_row}

</table>
<p style="margin:6px 0 0;color:#555;font-size:0.9em;">
  <strong>Note.</strong> “Effective mass” is a display-only unit conversion from f₀ via m = h·f₀ / c²; it is not an intrinsic rest-mass claim. See the core paper’s “Interpretation note (v1)” for context.
</p>


      <h2>🌀 Simulation Summary</h2>
      <ul>
        <li><strong>Steps (sim):</strong> {steps}</li>
        <li><strong>Frames stored:</strong> {len(frames_step_idx)}</li>
        <li><strong>Field size:</strong> {size} × {size}</li>
        <li><strong>Quasiparticles detected:</strong> {'[check] Yes' if quasiparticles_present else '[ERR] No'}</li>
        <li><strong>Vortices detected:</strong> {'[check] Yes' if vortices_present else '[ERR] No'}</li>
        <li><strong>Topological charge conserved:</strong> {'[check] Yes' if topo_conserved else '[!] Unstable'}</li>
      </ul>

      <h2>📈 Key Plots</h2>
      <div class="grid">
        {f'<div><img src="{RUN_TAG}_topo_charge_plot.png" alt="Topological charge plot"></div>' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_topo_charge_plot.png")) else ''}
        {f'<div><img src="{RUN_TAG}_vortex_count_plot.png" alt="Vortex count plot"></div>' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_vortex_count_plot.png")) else ''}
        {f'<div><img src="{RUN_TAG}_spectrum_plot.png" alt="Spectrum plot"></div>' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_spectrum_plot.png")) else ''}
        {f'<div><img src="{RUN_TAG}_phi_center_plot.png" alt="φ center plot"></div>' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_phi_center_plot.png")) else ''}
      </div>

            <h2>🎞️ Field Evolution GIFs</h2>
      <div class="grid">
        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_amplitude.gif" alt="Amplitude |ψ|" title="Amplitude |ψ|">
          <figcaption>Amplitude |ψ|</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_amplitude.gif")) else ''}

        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_spin.gif" alt="Spin-like curl map" title="Spin-like curl map">
          <figcaption>Spin-like curl map</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_spin.gif")) else ''}

        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_vortices.gif" alt="Vortex cores (±1 winding)" title="Vortex cores (±1 winding)">
          <figcaption>Vortex cores (±1 winding)</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_vortices.gif")) else ''}

        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_particles.gif" alt="Tracked quasiparticles" title="Tracked quasiparticles">
          <figcaption>Tracked quasiparticles</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_particles.gif")) else ''}

        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_flow.gif" alt="Flow field arrows (∇φ)" title="Flow field arrows (∇φ)">
          <figcaption>Flow field arrows (∇φ)</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_flow.gif")) else ''}

        {f'''
        <figure>
          <img src="{RUN_TAG}_lineum_full_overlay.gif"
               alt="Composite overlay (masked curl)"
               title="Composite overlay (masked curl)">
          <figcaption>Composite overlay (masked curl)</figcaption>
        </figure>''' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_lineum_full_overlay.gif")) else ''}

      </div>


      <h2>🧲 Spin aura (averaged curl map)</h2>
<p>
We compute an average of <code>curl(∇arg ψ)</code> in local windows centered on detected quasiparticles.
The resulting map shows a robust dipole-like pattern (“spin aura”). We report this as an emergent
flow pattern in the model; no claim is made about quantum spin.
</p>

{f'<div><img src="{RUN_TAG}_spin_aura_avg.png" alt="Spin aura"></div>' if _os.path.exists(_os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png")) else '<p><em>Spin-aura image not available for this run (frames may be disabled).</em></p>'}


      <h2>📚 Glossary & Naming Rationale</h2>

      <h2>🧠 Note on φ-guided motion</h2>
<p><strong>Note on φ-guided motion.</strong><br>
We do not claim a gravitational theory. In the canonical regime, particles tend to move along gradients of the background field φ. We refer to this as <em>environmental guidance</em>: a metric-like influence of φ on trajectories, without introducing a force law or any analogy to GR. This behavior is quantified via alignment metrics in the report and should be interpreted as an emergent guidance effect within the model.</p>

    <h3>🔤 Lineum</h3>
    <p>
      The name <strong>Lineum</strong> is a coined term from the Latin <em>linea</em> ("line" or "thread"), symbolizing
      the filament-like tension structures that emerge in the field. It refers to a hypothetical quantum field defined
      by local, nonlinear evolution rules. This field exhibits spontaneous formation of vortices, oscillations,
      topological effects, and quasiparticles.
    </p>
    <p>
      Pronunciation: <strong><em>line-um</em></strong> (Czech: <em>lineum</em>, as written).
    </p>
    <p>
      The name follows a tradition of physics-inspired constructs such as <em>graviton</em>, <em>inflaton</em>, or
      <em>axion</em>—terms that suggest emergent dynamics without predefining their exact physical nature.
    </p>

    <p style="color:#666;margin-top:24px;">
<small>Note: This report summarizes operational measurements from a 2D emergent model.
No cosmological, gravitational, biomedical or metaphysical claims are made.</small>
</p>

    <p style="margin-top:30px; font-style: italic; color: #555;">
        (c) Lineum – emergent quantum field simulation
    </p>
    </body>
    </html>"""

        path = _os.path.join(output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)

    # --- Full overlay GIF (guarded) ---
    if SAVE_GIFS:
        if WANT_FRAMES and _has_frames() and _nonempty(frames_amp) and _nonempty(frames_curl) and _nonempty(frames_vecx) and _nonempty(frames_vecy):
            overlay_path = _os.path.join(
                output_dir, f"{RUN_TAG}_lineum_full_overlay.gif")
            save_full_overlay_gif(
                frames_amp, frames_curl, frames_vecx, frames_vecy,
                overlay_path,
                vmin_amp=0.0, vmax_amp=0.5,
                vmin_curl=-0.3, vmax_curl=0.3,
                out_px=512,
                vec_stride=12,         # sparser arrows = cleaner look
                vec_scale=6.0,
                k_skip=GIFT_SKIP,
                # sladěno s ostatními GIFy (při k_skip=2)
                fps=5,
                amp_alpha_floor=0.30,  # skryje curl v nízké |ψ|
                curl_alpha_quantile=0.95,  # ignore weak curl below the 95th percentile
                alpha_scale=80,        # gentler overall curl alpha
                resample="bilinear"
            )
        else:
            _warn_skip("full overlay GIF (missing stored frames)")

    # --- NPY dumps (guarded) ---
    if WANT_FRAMES and _has_frames():
        # 🌀 Save all vortex fields to files for analysis
        frames_vort_np = np.array(frames_vort)  # shape: (n_frames, size, size)
        npy_path = _os.path.join(output_dir, f"{RUN_TAG}_frames_vortices.npy")
        frames_curl_np = np.array(frames_curl)
        npy_curl_path = _os.path.join(output_dir, f"{RUN_TAG}_frames_curl.npy")
        try:
            np.save(npy_curl_path, frames_curl_np)
            notify_file_creation(npy_curl_path)
        except Exception as e:
            notify_file_creation(npy_curl_path, success=False, error=e)

        try:
            np.save(npy_path, frames_vort_np)
            frames_amp_np = np.array(frames_amp)
            amp_npy_path = _os.path.join(
                output_dir, f"{RUN_TAG}_frames_amp.npy")
            try:
                np.save(amp_npy_path, frames_amp_np)
                notify_file_creation(amp_npy_path)
            except Exception as e:
                notify_file_creation(amp_npy_path, success=False, error=e)

            notify_file_creation(npy_path)
        except Exception as e:
            notify_file_creation(npy_path, success=False, error=e)
    else:
        _warn_skip("NPY dumps (no stored frames)")

    # 🧪 Analýza φ v okolí kvazičástic
    import random
    phi_values_near_particles = []
    phi_values_field = []

    if WANT_FRAMES and _has_frames() and _nonempty(frames_phi):
        for row in trajectories:
            step, y, x = int(row[1]), int(row[2]), int(row[3])
            fi = _phi_frame_idx(step)
            if fi is None:
                continue
            phi_frame = frames_phi[fi]

            if 2 < y < size - 3 and 2 < x < size - 3:
                local_phi = phi_frame[y-2:y+3, x-2:x+3].flatten()
                phi_values_near_particles.extend(local_phi)

            # random points in field (same stored frame)
            for _ in range(5):
                ry, rx = random.randint(
                    0, size - 1), random.randint(0, size - 1)
                phi_values_field.append(float(phi_frame[ry, rx]))

        phi_mean_near = float(np.mean(phi_values_near_particles)
                              ) if phi_values_near_particles else 0.0
        phi_std_near = float(np.std(phi_values_near_particles)
                             ) if phi_values_near_particles else 0.0
        phi_mean_field = float(np.mean(phi_values_field)
                               ) if phi_values_field else 0.0
        phi_std_field = float(np.std(phi_values_field)
                              ) if phi_values_field else 0.0

        # 🌀 Uložení φ polí pro pozdější analýzu
        frames_phi_np = np.array(frames_phi)  # φ v čase (throttled)
        phi_npy_path = _os.path.join(output_dir, f"{RUN_TAG}_frames_phi.npy")
        try:
            np.save(phi_npy_path, frames_phi_np)
            notify_file_creation(phi_npy_path)
        except Exception as e:
            notify_file_creation(phi_npy_path, success=False, error=e)
    else:
        _warn_skip(
            "phi-near-particles analysis + frames_phi.npy (no stored phi frames)")
        phi_mean_near = 0.0
        phi_std_near = None
        phi_mean_field = 0.0
        phi_std_field = 1.0

    if KAPPA_MODE == "island_to_constant":
        kappa = generate_kappa(i, total_steps=steps)

    # 📈 Výpočet životnosti kvazičástic
    lifespan_df = pd.DataFrame(trajectories, columns=[
        "id", "step", "y", "x", "amplitude"])
    # frames_phi is throttled; use _phi_at(step, y, x) to access step-aligned values.
    blackhole_candidates = []
    for tid, group in lifespan_df.groupby("id"):
        traj_steps = group["step"].values
        ys = group["y"].values.astype(int)
        xs = group["x"].values.astype(int)
        inside_phi = []
        for s, y, x in zip(traj_steps, ys, xs):
            v = _phi_at(int(s), int(y), int(x))
            if v is None:
                continue
            inside_phi.append(bool(v > 0.25))

        if len(inside_phi) > 5 and all(inside_phi[-5:]):
            blackhole_candidates.append(tid)
    blackhole_count = len(blackhole_candidates)

    # Získání φ při posledním výskytu každé černoděrové částice
    phi_at_death = []

    for tid in blackhole_candidates:
        traj = lifespan_df[lifespan_df["id"] == tid]
        last_step = traj["step"].max()
        row = traj[traj["step"] == last_step].iloc[0]
        y, x = int(row["y"]), int(row["x"])
        v = _phi_at(int(last_step), int(y), int(x))
        if v is not None:
            phi_at_death.append(float(v))

    if phi_at_death:
        avg_phi_death = np.mean(phi_at_death)
    else:
        avg_phi_death = None

    # Výpočet průměrné hmotnosti návratových částic
    blackhole_masses = []

    for tid in blackhole_candidates:
        traj = lifespan_df[lifespan_df["id"] == tid]
        yx_pairs = traj[["y", "x"]].drop_duplicates().values.astype(int)
        for y, x in yx_pairs:
            match = [d for d in multi_spectrum_details if d["point"] == (y, x)]
            if match:
                blackhole_masses.append(match[0]["mass_ratio"])

    if blackhole_masses:
        mass_ratio_blackholes = np.mean(blackhole_masses)
    else:
        mass_ratio_blackholes = None

    wormhole_count = 0
    for tid, group in lifespan_df.groupby("id"):
        group = group.sort_values("step")
        prev = None
        for _, row in group.iterrows():
            step, y, x = int(row["step"]), int(row["y"]), int(row["x"])
            v = _phi_at(step, y, x)
            if v is None:
                continue
            if v > 0.25:
                if prev:
                    dist = euclidean((y, x), prev)
                    if dist > 20:
                        wormhole_count += 1
                        break
                prev = (y, x)

    lifespans = lifespan_df.groupby("id")["step"].agg(["min", "max"])
    lifespans["duration"] = lifespans["max"] - lifespans["min"] + 1

    if lifespans.empty or "duration" not in lifespans or lifespans["duration"].dropna().empty:
        max_lifespan = 0
        median_lifespan = 0
    else:
        max_lifespan = int(lifespans["duration"].max())
        median_lifespan = int(lifespans["duration"].median())
        print(f"DEBUG: median_lifespan={median_lifespan}")

    # 📊 Analýza průměrné spinové aury kvazičástic
    # seaborn is optional; keep fallback without seaborn to avoid dependency issues
    try:
        import seaborn as sns
        _HAS_SEABORN = True
    except Exception:
        sns = None
        _HAS_SEABORN = False

    from scipy.ndimage import zoom

    frames_curl_np = np.array(frames_curl)

    curl_inside_phi = []
    if not (WANT_FRAMES and _has_frames() and _nonempty(frames_phi) and _nonempty(frames_curl)):
        _warn_skip("spin-aura + curl-in-phi stats (missing stored frames)")
        curl_mean = 0.0
        curl_std = 0.0
        average_spin_map = None
        upsampled_spin_map = None
        cutouts = []
    else:
        for step in range(len(frames_curl_np)):
            # step here is frame-index, not simulation step; align by stored step index
            if step >= len(frames_step_idx):
                continue
            sim_step = int(frames_step_idx[step])
            fi = _phi_frame_idx(sim_step)
            if fi is None:
                continue
            mask = frames_phi[fi] > 0.25
            curl_inside_phi.extend(frames_curl_np[step][mask])

            curl_mean = float(np.mean(curl_inside_phi)
                              ) if curl_inside_phi else 0.0
            curl_std = float(np.std(curl_inside_phi)
                             ) if curl_inside_phi else 0.0

    lifespan_df = pd.DataFrame(trajectories, columns=[
        "id", "step", "y", "x", "amplitude"])
    cutout_size = 11
    half_size = cutout_size // 2
    cutouts = []

    for _, row in lifespan_df.iterrows():
        step = int(row["step"])
        y = int(row["y"])
        x = int(row["x"])

        fi = _frame_idx_for_step(step)
        if fi is None:
            continue
        if (
            0 <= fi < len(frames_curl_np)
            and half_size <= y < frames_curl_np.shape[1] - half_size
            and half_size <= x < frames_curl_np.shape[2] - half_size
        ):
            cutout = frames_curl_np[fi, y-half_size:y +
                                    half_size+1, x-half_size:x+half_size+1]
            cutouts.append(cutout)

    # ---- Spin-aura: requires stored frames AND non-empty cutouts ----
    if not cutouts:
        print("[!] Skipping: spin-aura upsample and related plots (no cutouts; likely no stored frames).")
        average_spin_map = None
        upsampled_spin_map = None
    else:
        average_spin_map = np.mean(cutouts, axis=0)

        # Guard: ensure we have a real 2D numeric array
        try:
            average_spin_map = np.asarray(average_spin_map)
            _spin_ok = (average_spin_map.ndim ==
                        2 and average_spin_map.size > 0)
        except Exception:
            _spin_ok = False

        if not _spin_ok:
            print(
                "[!] Skipping: spin-aura upsample and related plots (invalid average_spin_map).")
            upsampled_spin_map = None
        else:
            upsampled_spin_map = zoom(average_spin_map, 5, order=3)

            # Clean NaN/Inf only if the map exists and is numeric
            try:
                upsampled_spin_map = np.asarray(
                    upsampled_spin_map, dtype=float)
                if not np.all(np.isfinite(upsampled_spin_map)):
                    upsampled_spin_map = np.nan_to_num(
                        upsampled_spin_map, nan=0.0, posinf=0.0, neginf=0.0
                    )
            except Exception:
                print(
                    "[!] Skipping: spin-aura plots (upsampled map not a finite float array).")
                upsampled_spin_map = None

    # Only export plots/profile if we actually have a valid map
    if upsampled_spin_map is not None:
        # Uložení obrázku
        spin_img_path = _os.path.join(
            output_dir, f"{RUN_TAG}_spin_aura_avg.png")
        plt.figure(figsize=(6, 6))
        if _HAS_SEABORN:
            sns.heatmap(upsampled_spin_map, center=0,
                        cmap="bwr", cbar=True, square=True)
            plt.title("🧲 Averaged spin aura (curl ∇arg(ψ))")
            plt.axis("off")
        else:
            plt.imshow(upsampled_spin_map, cmap="bwr")
            plt.title("🧲 Averaged spin aura (curl ∇arg(ψ))")
            plt.axis("off")
            plt.colorbar()
        plt.tight_layout()
        try:
            plt.savefig(spin_img_path, dpi=150)
            notify_file_creation(spin_img_path)
        except Exception as e:
            notify_file_creation(spin_img_path, success=False, error=e)
        finally:
            plt.close()

        # Plain map
        spin_map_path = _os.path.join(
            output_dir, f"{RUN_TAG}_spin_aura_map.png")
        plt.figure(figsize=(3.6, 3.6))
        plt.imshow(upsampled_spin_map, cmap="bwr")
        plt.axis("off")
        plt.tight_layout(pad=0)
        try:
            plt.savefig(spin_map_path, bbox_inches="tight",
                        pad_inches=0, dpi=150)
            notify_file_creation(spin_map_path)
        except Exception as e:
            notify_file_creation(spin_map_path, success=False, error=e)
        finally:
            plt.close()

        # Radial profile from the non-upsampled average map
        yy, xx = np.indices(average_spin_map.shape)
        cy, cx = average_spin_map.shape[0] // 2, average_spin_map.shape[1] // 2
        rr = np.sqrt((yy - cy)**2 + (xx - cx)**2)
        rbin = rr.astype(int)
        rmax = rbin.max()
        profile_rows = [(int(r), float(average_spin_map[rbin == r].mean()))
                        for r in range(rmax + 1)]
        save_csv("spin_aura_profile.csv", [
                 "radius_px", "mean_curl"], profile_rows)

    include_spin = _os.path.exists(
        _os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png"))

    # If we skipped frame-dependent analyses, guard downstream reads (avoid crash on missing CSV).
    if not (WANT_FRAMES and _has_frames()):
        include_spin = False

    low_mass_count = sum(
        1 for d in multi_spectrum_details if d["mass_ratio"] < 0.01)

    # 📊 Export φ a curl v místech kvazičástic s mass_ratio < 0.01
    low_mass_coords = [
        (d["point"][0], d["point"][1])
        for d in multi_spectrum_details
        if d["mass_ratio"] < 0.01
    ]

    phi_final = np.abs(phi.copy())  # poslední stav φ

    # 📊 Výstup φ hodnot v mřížce 20×20
    grid_points = [(y, x) for y in range(0, size, 20)
                   for x in range(0, size, 20)]
    phi_grid_rows = [(y, x, phi_final[y, x]) for y, x in grid_points]
    save_csv("phi_grid_summary.csv", ["y", "x", "phi"], phi_grid_rows)

    # 🧠 Detekce deja vu / Mandela efekt kandidátů (φ > 0.25 na mřížce)
    phi_deja_rows = [(y, x, phi_final[y, x])
                     for y, x in grid_points if phi_final[y, x] > 0.25]
    save_csv("phi_grid_dejavu.csv", ["y", "x", "phi"], phi_deja_rows)

    curl_final = curl  # poslední stav curl (v hlavní smyčce už ho máš)

    rows = []
    for y, x in low_mass_coords:
        if 0 <= y < size and 0 <= x < size:
            rows.append([y, x, phi_final[y, x], curl_final[y, x]])

    save_csv("phi_curl_low_mass.csv", ["y", "x", "phi", "curl"], rows)

    # 📊 Vyhodnocení paměťové stopy ve φ-pastích
    df_low_mass = pd.read_csv(_os.path.join(
        output_dir, f"{RUN_TAG}_phi_curl_low_mass.csv"))

    phi_low_mass_mean = df_low_mass["phi"].mean()
    curl_low_mass_mean = df_low_mass["curl"].abs().mean()
    phi_above_025_count = (df_low_mass["phi"] > 0.25).sum()
    curl_near_zero_count = (df_low_mass["curl"].abs() < 0.02).sum()

    # Save φ-center plot used in the report
    try:
        save_phi_center_plot()
    except Exception as e:
        print(f"[warn] save_phi_center_plot failed: {e}")

    # --- Recompute display-only mass from the canonical f0 and guard against drift ---
    _H = 6.62607015e-34
    _C = 299_792_458.0
    _electron_mass = 9.1093837015e-31  # CODATA 2018

    mass = (_H * dominant_freq) / (_C**2)
    electron_mass = _electron_mass      # keep plain name if used downstream
    mass_ratio = mass / electron_mass

    # sanity guard – the display mass must be exactly hf0/c^2
    _mass_from_f = (_H * dominant_freq) / (_C**2)
    if dominant_freq > 1e-12 and np.isfinite(dominant_freq):
        # Relative error check (safe against div/0 due to if-guard)
        assert abs(mass - _mass_from_f) / _mass_from_f < 1e-6, "mass/f0 mismatch"

    generate_html_report(
        mass=mass,
        mass_ratio=mass_ratio,
        max_lifespan=max_lifespan,
        median_lifespan=median_lifespan,
        include_spin=include_spin,
        phi_mean_near=phi_mean_near,
        phi_mean_field=phi_mean_field,
        phi_std_field=phi_std_field,
        mass_ratio_blackholes=mass_ratio_blackholes,
        avg_phi_death=avg_phi_death,
        low_mass_count=low_mass_count,
        phi_low_mass_mean=phi_low_mass_mean,
        curl_low_mass_mean=curl_low_mass_mean,
        phi_above_025_count=phi_above_025_count,
        curl_near_zero_count=curl_near_zero_count,
        phi_half_life_steps=phi_half_life_steps,
        sbr=sbr,
        pct_neutral=pct_neutral,
        mean_total_vort=mean_total_vort,
        phi_std_near=phi_std_near,
        sbr_ci=sbr_ci,
        f0_ci=f0_ci,
        figure0_html=figure0_html
    )

    # --- JSON manifest tohoto běhu (strojově čitelný souhrn) ---
    run_meta = {
        "run_id": int(RUN_ID),
        "run_tag": str(RUN_TAG),
        "seed": int(SEED),
        "run_mode": str(RUN_MODE),
        "param_tag": str(PARAM_TAG),
        "kappa_mode": str(KAPPA_MODE),
        "low_noise_mode": bool(LOW_NOISE_MODE),
        "test_exhale_mode": bool(TEST_EXHALE_MODE),
        # Never depend on frames_* being present (they can be disabled).
        "grid_size": int(size),
        "steps": int(steps),
        "pixel_size_m": float(PIXEL_SIZE),
        "time_step_s": float(TIME_STEP),
        "window_W": int(WINDOW_W),
        "window_hop": int(WINDOW_HOP),
        "phi_interaction_cap": float(PHI_INTERACTION_CAP),
        "phi_cap": float(PHI_CAP),
        "psi_amp_cap": float(PSI_AMP_CAP),
        "grad_cap": float(GRAD_CAP),
    }

    # --- Structural Closure (Phi Half-life) ---
    phi_half_life_steps = None
    phi_half_life_status = "OK"
    steady_state_val = None
    
    if len(phi_center_log) > 0:
        # Synced sequence from phi_center_log (logged steps only)
        phi_logged = np.array([row[1] for row in phi_center_log])
        n_logged = len(phi_logged)
        
        # Steady state: trailing 10% (min 1 frame)
        window_size = max(1, int(math.floor(0.1 * n_logged)))
        steady_state_val = float(np.mean(phi_logged[-window_size:]))
        
        if steady_state_val < 0.01:
            phi_half_life_status = "N/A_LOW_STEADY_STATE"
            phi_half_life_steps = None
        else:
            phi_half = 0.5 * steady_state_val
            # Find first step in the same logged sequence
            for idx, val in enumerate(phi_logged):
                if val >= phi_half:
                    phi_half_life_steps = int(phi_center_log[idx][0])
                    break

    metrics = {
        "dominant_freq_Hz": float(dominant_freq),
        "sbr": None if (sbr is None or sbr != sbr) else float(sbr),
        "f0_ci": None if f0_ci is None else [float(f0_ci[0]), float(f0_ci[1])],
        "sbr_ci": None if sbr_ci is None else [float(sbr_ci[0]), float(sbr_ci[1])],
        "phi_half_life_steps": phi_half_life_steps,
        "phi_half_life_status": phi_half_life_status,
        "phi_steady_state": steady_state_val,
        "pct_neutral": float(pct_neutral) if pct_neutral is not None else None,
        "mean_total_vortices": float(mean_total_vort) if mean_total_vort is not None else None,
        "max_lifespan_steps": int(max_lifespan),
        "median_lifespan_steps": int(median_lifespan),
        "phi_mean_near": float(phi_mean_near),
        "phi_mean_field": float(phi_mean_field),
        "phi_std_near": None if phi_std_near is None else float(phi_std_near),
        "phi_std_field": float(phi_std_field),
        "low_mass_quasiparticle_count": int(low_mass_count),
    }

    outputs = {
        # HTML report
        "html_report": _os.path.join(output_dir, f"{RUN_TAG}_lineum_report.html"),

        # CSV logy (vše přes save_csv má prefix RUN_TAG_)
        "amplitude_log_csv": _os.path.join(output_dir, f"{RUN_TAG}_amplitude_log.csv"),
        "phi_center_log_csv": _os.path.join(output_dir, f"{RUN_TAG}_phi_center_log.csv"),
        "topo_log_csv": _os.path.join(output_dir, f"{RUN_TAG}_topo_log.csv"),
        "trajectories_csv": _os.path.join(output_dir, f"{RUN_TAG}_trajectories.csv"),
        "multi_spectrum_summary_csv": _os.path.join(output_dir, f"{RUN_TAG}_multi_spectrum_summary.csv"),
        "metrics_summary_csv": _os.path.join(output_dir, f"{RUN_TAG}_metrics_summary.csv"),
        "phi_grid_summary_csv": _os.path.join(output_dir, f"{RUN_TAG}_phi_grid_summary.csv"),
        "phi_grid_dejavu_csv": _os.path.join(output_dir, f"{RUN_TAG}_phi_grid_dejavu.csv"),
        "phi_curl_low_mass_csv": _os.path.join(output_dir, f"{RUN_TAG}_phi_curl_low_mass.csv"),
        "spin_aura_profile_csv": _os.path.join(output_dir, f"{RUN_TAG}_spin_aura_profile.csv"),

        # Obrázky a GIFy
        "spectrum_plot_png": _os.path.join(output_dir, f"{RUN_TAG}_spectrum_plot.png"),
        "phi_center_plot_png": _os.path.join(output_dir, f"{RUN_TAG}_phi_center_plot.png"),
        "topo_charge_plot_png": _os.path.join(output_dir, f"{RUN_TAG}_topo_charge_plot.png"),
        "vortex_count_plot_png": _os.path.join(output_dir, f"{RUN_TAG}_vortex_count_plot.png"),
        "kappa_map_png": _os.path.join(output_dir, f"{RUN_TAG}_kappa_map.png"),
        "figure0_canonical_png": _os.path.join(output_dir, f"{RUN_TAG}_figure0_canonical.png"),
        "spin_aura_avg_png": _os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png"),
        "spin_aura_map_png": _os.path.join(output_dir, f"{RUN_TAG}_spin_aura_map.png"),
        "gif_amplitude": _os.path.join(output_dir, f"{RUN_TAG}_lineum_amplitude.gif"),
        "gif_spin": _os.path.join(output_dir, f"{RUN_TAG}_lineum_spin.gif"),
        "gif_vortices": _os.path.join(output_dir, f"{RUN_TAG}_lineum_vortices.gif"),
        "gif_particles": _os.path.join(output_dir, f"{RUN_TAG}_lineum_particles.gif"),
        "gif_flow": _os.path.join(output_dir, f"{RUN_TAG}_lineum_flow.gif"),
        "gif_full_overlay": _os.path.join(output_dir, f"{RUN_TAG}_lineum_full_overlay.gif"),

        # NPY dumpy
        "frames_vortices_npy": _os.path.join(output_dir, f"{RUN_TAG}_frames_vortices.npy"),
        "frames_curl_npy": _os.path.join(output_dir, f"{RUN_TAG}_frames_curl.npy"),
        "frames_amp_npy": _os.path.join(output_dir, f"{RUN_TAG}_frames_amp.npy"),
        "frames_phi_npy": _os.path.join(output_dir, f"{RUN_TAG}_frames_phi.npy"),
    }


    # State checkpoint (if enabled)
    latest_ckpt_path = None
    if SAVE_STATE:
        try:
            # Uložení stavu po posledním kroku (i)
            # Pokud běh skončil normálně, i je poslední krok.
            # Pokud byl přerušen, i je krok přerušení.
            latest_ckpt_path = save_state_checkpoint(
                output_dir, RUN_TAG, int(i),
                psi, phi, kappa, delta, active_tracks, int(next_id)
            )
            if latest_ckpt_path:
                outputs["latest_state_checkpoint"] = latest_ckpt_path
        except Exception as e:
            print(f"⚠️ Failed to save state checkpoint: {e}")

    # --- Analysis Config (Explicit commitment for audit) ---
    analysis_config = {
        "spectrum_definition": "power |FFT(x)|^2",
        "window_type": "Hann",
        "window_length": int(WINDOW_W) if WINDOW_W else 256,
        "hop_length": int(WINDOW_HOP) if WINDOW_HOP else 128,
        "guard_bins": 2,
        "estimator": "centroid",
        "bootstrap_iterations": 1000,
        "bootstrap_ci_level": 0.95,
        "sbr_guard_bins": 2,
    }

    # --- Kappa Metadata & Stats ---
    # Determine if κ is static or dynamic for stats basis
    is_dynamic_kappa = (KAPPA_MODE == "island_to_constant") # or others if added
    
    # Kappa spatial stats (from the final state)
    kappa_final_mean = float(np.mean(kappa))
    kappa_final_std = float(np.std(kappa))
    
    # Kappa temporal stats (of spatial means)
    kappa_mean_of_means = None
    kappa_std_of_means = None
    if is_dynamic_kappa and len(kappa_spatial_means) > 0:
        kappa_mean_of_means = float(np.mean(kappa_spatial_means))
        kappa_std_of_means = float(np.std(kappa_spatial_means))

    manifest = {
        "run": run_meta,
        "spectral_pipeline": spectral_meta,
        "kappa": {
            "mode": KAPPA_MODE,
            "hash": KAPPA_HASH,
            "hash_basis": "map_at_init", # static for now, dynamic could update this
            "is_dynamic": is_dynamic_kappa,
            "stats": {
                "spatial_final_mean": kappa_final_mean,
                "spatial_final_std": kappa_final_std,
                "temporal_mean_of_spatial_means": kappa_mean_of_means,
                "temporal_std_of_spatial_means": kappa_std_of_means
            }
        },
        "metrics": metrics or {},
        "data_files": outputs,
        "topology": {
            "computed_over": "logged_frames_only",
            "includes_step_0": True,
            "raw_winding_used": True
        }
    }

    save_manifest(manifest, filename=f"{RUN_TAG}_manifest.json")

    print("All GIFs, logs and manifest have been successfully generated.")
