import numpy as np
import hashlib
from copy import deepcopy
from dataclasses import replace

class TextToWaveEncoder:
    """
    Hybrid Architecture Text-to-Wave Encoder
    Handles both 'identity_burn' (Layer 1 - HDD/mu) and 'runtime' (Layer 2 - RAM/phi) plasticity.
    """
    def __init__(self, grid_size=64, plasticity_tau=200):
        self.grid_size = grid_size
        self.plasticity_tau = plasticity_tau
        self.history_frequencies = {}
        self.mu_baseline = None
        
    def _hash_text(self, text: str) -> str:
        # Simple semantic proxy: hash the normalized text
        return hashlib.sha256(text.lower().strip().encode('utf-8')).hexdigest()
        
    def set_baseline(self, state: dict):
        if "mu" in state:
            self.mu_baseline = np.copy(state["mu"])
            
    def compute_metrics(self, state_before: dict, state_after: dict):
        metrics = {}
        # RTB Stability Score: inverse of amplitude of chaotic noise (Psi diff)
        diff_psi = float(np.linalg.norm(state_after["psi"] - state_before["psi"]))
        metrics["rtb_stability_score"] = 1.0 / (1.0 + diff_psi)
        
        # Identity Drift Index: L1 norm of mu vs baseline
        if self.mu_baseline is not None and "mu" in state_after:
            drift = float(np.sum(np.abs(state_after["mu"] - self.mu_baseline)))
            metrics["identity_drift_index"] = drift
        else:
            metrics["identity_drift_index"] = 0.0
            
        # Plasticity Retention Curve Estimate: how much phi changed
        diff_phi = float(np.sum(np.abs(state_after["phi"] - state_before["phi"])))
        metrics["plasticity_retention"] = diff_phi

        return metrics

    def encode(self, text: str, state: dict, cfg, step_fn, mode="runtime", personalization_depth=1.0):
        """
        Injects a semantic text block into the Lineum physics grid.
        - mode='identity_burn': Engraves heavily into Mu. Uses frequency reinforcement.
        - mode='runtime': Engraves strictly into Phi/Psi. Highly reversible.
        """
        assert mode in ["identity_burn", "runtime"], f"Unknown mode: {mode}"
        
        state_before = deepcopy(state)
        if self.mu_baseline is None and "mu" in state:
            self.set_baseline(state)
            
        txt_hash = self._hash_text(text)
        freq = self.history_frequencies.get(txt_hash, 0) + 1
        self.history_frequencies[txt_hash] = freq
        
        rng = np.random.RandomState(int(txt_hash[:8], 16))
        cx, cy = rng.randint(10, self.grid_size - 10, size=2)
        
        delta = np.zeros((self.grid_size, self.grid_size), dtype=np.float64)
        base_pulse = 10.0 * personalization_depth
        delta[cx-3:cx+4, cy-3:cy+4] = base_pulse
        state["delta"] = delta
        
        original_use_mu = getattr(cfg, "use_mu", False)
        
        if mode == "identity_burn":
            cfg = replace(cfg, use_mu=True)
            # Frequency Weighting: Single input = low mu engraving. Repeated = exponential.
            ticks = int(20 * (1.5 ** (freq - 1)))
            ticks = min(ticks, self.plasticity_tau * 3)
        else:
            # Runtime Mode: strictly Layer 2 (RAM)
            cfg = replace(cfg, use_mu=False)
            ticks = int(self.plasticity_tau * 0.25)
            
        # Active injection ticks
        for _ in range(ticks):
            state = step_fn(state, cfg)
            
        # Clear external pulse and let plasticity settle
        state["delta"] = np.zeros_like(state["phi"])
        
        for _ in range(self.plasticity_tau):
            state = step_fn(state, cfg)
            
        if "mu" not in state and "mu" in state_before:
            state["mu"] = state_before["mu"]
            
        metrics = self.compute_metrics(state_before, state)
        # Also compute naive cost for legacy logs
        metrics["hdd_cost_kj"] = float(np.sum(np.abs(state["psi"])**2) - np.sum(np.abs(state_before["psi"])**2))
        
        return state, metrics
