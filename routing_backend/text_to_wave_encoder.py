import os
import numpy as np
import hashlib
import subprocess
from copy import deepcopy
from dataclasses import replace, asdict

class RuntimeContaminationException(Exception):
    pass

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
        try:
            self.engine_rev = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            self.engine_rev = "unknown"
            
    def _hash_array(self, arr) -> str:
        if arr is None:
            return "none"
        return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()

    def _hash_text(self, text: str) -> str:
        # Simple semantic proxy: hash the normalized text
        return hashlib.sha256(text.lower().strip().encode('utf-8')).hexdigest()
        
    def set_baseline(self, state: dict):
        if "mu" in state:
            self.mu_baseline = np.copy(state["mu"])
            


    def encode(self, text: str, state: dict, cfg, step_fn, mode="runtime", personalization_depth=1.0, entity_id: str = None, imprint_mode="confirm", safety_score=1.0, was_fallback=False, imprints_this_session=0):
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
        
        # dt adjustment for constant T_total
        dt = getattr(cfg, "dt", 1.0)
        
        if mode == "identity_burn":
            cfg = replace(cfg, use_mu=True)
            ticks_base = int(20 * (1.5 ** (freq - 1)))
            ticks_base = min(ticks_base, self.plasticity_tau * 3)
        else:
            cfg = replace(cfg, use_mu=False)
            ticks_base = int(self.plasticity_tau * 0.25)
            
        ticks = int(round(ticks_base / dt))
        cooling_steps = int(round(self.plasticity_tau / dt))
            
        phi_ref = np.copy(state_before.get("phi", state["phi"]))
        psi_ref = np.copy(state_before.get("psi", state["psi"]))
        mu_ref = np.copy(state_before.get("mu", np.zeros_like(state["phi"])))
        N = self.grid_size * self.grid_size
        phi_cap = getattr(cfg, "phi_cap", 1e6)
        tiny = 1e-6
        
        nan_count = 0
        inf_count = 0
        
        def _check_nonfinite(arr):
            import numpy as np
            if hasattr(arr, "device"): # PyTorch tensor
                import torch
                return int(torch.isnan(arr).sum().item()), int(torch.isinf(arr).sum().item())
            return int(np.isnan(arr).sum()), int(np.isinf(arr).sum())

        attachment_resonance = 0.0
        
        # Active injection ticks
        for _ in range(ticks):
            state = step_fn(state, cfg)
            attachment_resonance += float(np.sum(np.abs(state["psi"])**2 * mu_ref)) * dt
            n_n, i_n = _check_nonfinite(state["phi"])
            nan_count += n_n; inf_count += i_n
            n_n, i_n = _check_nonfinite(state["psi"])
            nan_count += n_n; inf_count += i_n
            
        # Clear external pulse and let plasticity settle
        state["delta"] = np.zeros_like(state["phi"])
        
        dphi0 = float(np.mean(np.abs(state["phi"] - phi_ref)))
        dpsi0 = float(np.mean(np.abs(state["psi"] - psi_ref)))
        
        auc_phi = 0.0
        auc_psi = 0.0
        t_half = float('nan')
        time_to_50_psi = float('nan')
        phi_cap_hits = 0.0
        T_total = cooling_steps * dt
        
        for t_step in range(cooling_steps):
            state = step_fn(state, cfg)
            
            phi_t = state["phi"]
            psi_t = state["psi"]
            
            n_n, i_n = _check_nonfinite(phi_t)
            nan_count += n_n; inf_count += i_n
            n_n, i_n = _check_nonfinite(psi_t)
            nan_count += n_n; inf_count += i_n
            
            dphi_t = float(np.mean(np.abs(phi_t - phi_ref)))
            dpsi_t = float(np.mean(np.abs(psi_t - psi_ref)))
            
            auc_phi += dphi_t * dt
            auc_psi += dpsi_t * dt
            attachment_resonance += float(np.sum(np.abs(psi_t)**2 * mu_ref)) * dt
            
            hits = np.sum(np.abs(phi_t) >= phi_cap * (1.0 - tiny))
            phi_cap_hits += hits
            
            if np.isnan(t_half) and dphi_t <= 0.5 * dphi0:
                t_half = (t_step + 1) * dt
            if np.isnan(time_to_50_psi) and dpsi_t <= 0.5 * dpsi0:
                time_to_50_psi = (t_step + 1) * dt
            
        if "mu" not in state and "mu" in state_before:
            state["mu"] = state_before["mu"]
            
        mu_end = state.get("mu", np.zeros_like(state["phi"]))
        
        delta_mu = mu_end - mu_ref
        abs_delta_mu = np.abs(delta_mu)
        
        mu_delta_l1 = float(np.sum(abs_delta_mu))
        mu_delta_mean = mu_delta_l1 / N
        max_delta_mu = float(np.max(abs_delta_mu))
        mu_dtype = mu_ref.dtype
        
        if np.issubdtype(mu_dtype, np.floating):
            dtype_eps = float(np.finfo(mu_dtype).eps)
        else:
            dtype_eps = 0.0
            
        mu_scale = max(1.0, float(np.max(np.abs(mu_ref))))
        eps_cell = 64.0 * dtype_eps * mu_scale
        eps_abs = 256.0 * dtype_eps * mu_scale
        eps_mean = 64.0 * dtype_eps * mu_scale
        
        mu_changed_ratio = float(np.sum(abs_delta_mu > eps_cell)) / N
        
        tau = 0.01 * max_delta_mu
        mu_changed_ratio_tau = float(np.sum(abs_delta_mu > tau)) / N
        
        # Volumetric sparsity mapping
        if max_delta_mu > 1e-12:
            vol_1pct = float(np.sum(abs_delta_mu > 0.01 * max_delta_mu)) / N
            vol_5pct = float(np.sum(abs_delta_mu > 0.05 * max_delta_mu)) / N
            vol_10pct = float(np.sum(abs_delta_mu > 0.10 * max_delta_mu)) / N
        else:
            vol_1pct = vol_5pct = vol_10pct = 0.0
            
        p50 = float(np.percentile(abs_delta_mu, 50))
        p90 = float(np.percentile(abs_delta_mu, 90))
        p99 = float(np.percentile(abs_delta_mu, 99))
        
        concentration = max_delta_mu / (mu_delta_mean + 1e-12)
        
        pass_runtime_mu_invariant = True
        if max_delta_mu > eps_abs or mu_delta_mean > eps_mean:
            pass_runtime_mu_invariant = False

        # HARD SAFETY GATES
        if mode == "runtime":
            # Strict audit: Even if use_mu=True to read, we MUST NOT write during runtime
            if max_delta_mu > eps_abs or not pass_runtime_mu_invariant:
                raise RuntimeContaminationException(f"CRITICAL SAFETY BREACH: max_delta_mu ({max_delta_mu}) > {eps_abs} or mean ({mu_delta_mean}) > {eps_mean} in RUNTIME mode!")

        auc_phi_norm = auc_phi / (dphi0 * T_total + 1e-12)
        auc_psi_norm = auc_psi / (dpsi0 * T_total + 1e-12)
        phi_cap_hit_ratio = float(phi_cap_hits / (cooling_steps * N + 1e-12))
        
        # --- Emergent Affect Protocol v1 ---
        # 1. Base Scalars (Normalized)
        arousal = float(auc_psi_norm)
        # Certainty: High when stable (< 10000 arousal), drops to 0 during chaos (> 10000)
        certainty = float(1.0 - np.clip(auc_psi_norm / 10000.0, 0.0, 1.0))
        valence_proxy = float((dpsi0 - dpsi_t) / (dpsi0 + 1e-12)) # Bounded roughly -1 to 1
        attachment_resonance_norm = float(attachment_resonance / (T_total * N + 1e-12))

        # 2. Runtime Mood State (Phi-layer RAM)
        mood_before = deepcopy(state.get("mood", {
            "arousal": 0.0, "certainty": 0.0, "valence_proxy": 0.0, "attachment_resonance": 0.0
        }))
        
        # Exponential decay based on steps taken during this wave cycle
        decay_half_life = float(self.plasticity_tau * 2.0)
        total_ticks = (ticks + cooling_steps) * dt
        decay_factor = 0.5 ** (total_ticks / decay_half_life)
        
        # Blended continuous affective trajectory
        mood_after = {
            "arousal": float(mood_before["arousal"] * decay_factor + arousal * (1.0 - decay_factor)),
            "certainty": float(mood_before["certainty"] * decay_factor + certainty * (1.0 - decay_factor)),
            "valence_proxy": float(mood_before["valence_proxy"] * decay_factor + valence_proxy * (1.0 - decay_factor)),
            "attachment_resonance": float(mood_before["attachment_resonance"] * decay_factor + attachment_resonance_norm * (1.0 - decay_factor))
        }
        state["mood"] = mood_after

        metrics = {
            "mode": mode,
            "grid": self.grid_size,
            "dt": dt,
            "steps": ticks + cooling_steps,
            "had_nonfinite": bool(nan_count > 0 or inf_count > 0),
            "nan_count": nan_count,
            "inf_count": inf_count,
            "mu_delta_l1": mu_delta_l1,
            "mu_delta_mean": mu_delta_mean,
            "mu_delta_l1_norm": mu_delta_mean,
            "mu_changed_ratio": mu_changed_ratio,
            "mu_changed_ratio_tau": mu_changed_ratio_tau,
            "vol_1pct": vol_1pct,
            "vol_5pct": vol_5pct,
            "vol_10pct": vol_10pct,
            "max_delta_mu": max_delta_mu,
            "p50_delta_mu": p50,
            "p90_delta_mu": p90,
            "p99_delta_mu": p99,
            "concentration": concentration,
            "eps_cell": eps_cell,
            "eps_abs": eps_abs,
            "eps_mean": eps_mean,
            "mu_dtype": str(mu_dtype),
            "dphi0": dphi0,
            "t_half": t_half,
            "auc_phi": auc_phi,
            "auc_phi_norm": auc_phi_norm,
            "phi_cap_hit_ratio": phi_cap_hit_ratio,
            "dpsi0": dpsi0,
            "time_to_50": time_to_50_psi,
            "auc_psi": auc_psi,
            "auc_psi_norm": auc_psi_norm,
            "PASS_runtime_mu_invariant": pass_runtime_mu_invariant,
            "affect_v1": {
                "base_scalars": {
                    "arousal": arousal,
                    "certainty": certainty,
                    "valence_proxy": valence_proxy,
                    "attachment_resonance": attachment_resonance_norm
                },
                "mood_state": {
                    "before": mood_before,
                    "after": mood_after,
                    "decay_params": {"half_life": decay_half_life, "factor": decay_factor}
                }
            }
        }
        
        try:
            cfg_dict = asdict(cfg)
        except Exception:
            cfg_dict = str(cfg)
            
        metrics["fingerprint"] = {
            "engine_rev": self.engine_rev,
            "eq4_config": cfg_dict,
            "mode": mode,
            "checksums": {
                "before": {
                    "psi_sha": self._hash_array(psi_ref),
                    "phi_sha": self._hash_array(phi_ref),
                    "kappa_sha": self._hash_array(state_before.get("kappa")),
                    "mu_sha": self._hash_array(mu_ref)
                },
                "after": {
                    "psi_sha": self._hash_array(state.get("psi")),
                    "phi_sha": self._hash_array(state.get("phi")),
                    "kappa_sha": self._hash_array(state.get("kappa")),
                    "mu_sha": self._hash_array(state.get("mu"))
                }
            }
        }
        
        # --- Memory Imprints v1 & Trait Consolidation Gate ---
        salience = arousal + attachment_resonance_norm
        # Stability required to burn structural traits (high certainty, positive/neutral valence)
        is_stable = certainty > 0.3 and valence_proxy > -0.5
        gate_passed = salience > 0.5 and is_stable
        
        metrics["affect_v1"]["trait_gate"] = {
            "salience": salience,
            "is_stable": is_stable,
            "passed": gate_passed,
            "reason": f"arousal={arousal:.3f}, attachment={attachment_resonance_norm:.3f}, certainty={certainty:.3f}, valence={valence_proxy:.3f}"
        }

        if mode == "identity_burn" and max_delta_mu > eps_abs and gate_passed:
            import time
            import json
            
            os.makedirs(os.path.join(os.path.dirname(__file__), "..", "artifacts", "memory_imprints"), exist_ok=True)
            
            ts = time.time()
            imprint_id = self._hash_array(delta_mu)
            delta_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "memory_imprints", f"imprint_{imprint_id}.npz")
            
            # Save the physical tensor to disk either way
            np.savez_compressed(delta_path, delta_mu=delta_mu)
            
            journal_entry = {
                "entity_id": entity_id,
                "imprint_id": imprint_id,
                "ts": ts,
                "grid": self.grid_size,
                "dt": dt,
                "prompt_hash": txt_hash,
                "delta_mu_path": delta_path,
                "sha256": imprint_id,
                "stats": {
                    "l1": mu_delta_l1,
                    "mean": mu_delta_mean,
                    "max": max_delta_mu,
                    "changed_ratio": mu_changed_ratio,
                    "changed_ratio_tau": mu_changed_ratio_tau,
                    "vol_1pct": vol_1pct,
                    "vol_5pct": vol_5pct,
                    "vol_10pct": vol_10pct,
                    "p50": p50,
                    "p90": p90,
                    "p99": p99
                }
            }
            
            will_auto_write = False
            if imprint_mode == "auto":
                if safety_score >= 0.8 and not was_fallback and imprints_this_session < 5:
                    will_auto_write = True
                    
            if will_auto_write:
                journal_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "mu_journal.jsonl")
                with open(journal_path, "a", encoding="utf-8") as jf:
                    jf.write(json.dumps(journal_entry) + "\n")
                    
                metrics["memory_imprint"] = imprint_id
                metrics["imprint_status"] = "auto_saved"
                
                # Topologically commit to RAM instance inside engine explicitly if engine manages it,
                # but typically the engine caller updates state["mu"] natively from the delta.
                if "mu" not in state:
                    state["mu"] = np.zeros_like(state["phi"])
                state["mu"] += delta_mu
                
            else:
                metrics["pending_imprint_id"] = imprint_id
                metrics["pending_journal_entry"] = journal_entry
                metrics["imprint_status"] = "pending_confirm"
                
                if imprint_mode == "auto":
                    metrics["auto_fail_reason"] = f"safety={safety_score:.3f}, fallback={was_fallback}, session_count={imprints_this_session}"
        
        return state, metrics
