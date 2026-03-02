import numpy as np

class TranslatorV01:
    """
    Implements TranslatorSpec v0.1 and ReadoutSpec v0.1.
    A pure mathematical bridge mapping 1536D Semantic embeddings to/from a 100x100 physical 2D tensor.
    """
    def __init__(self, size=100, embedding_dim=1536, seed=42):
        self.size = size
        self.dim = embedding_dim
        
        # 1. TranslatorSpec v0.1: Deterministic Gaussian Anchors
        np.random.seed(seed)
        self.anchor_x = np.random.randint(0, size, size=self.dim)
        self.anchor_y = np.random.randint(0, size, size=self.dim)
        
        # Precompute the fixed 2D Gaussian patches for all 1536 anchors (Sigma = 1.5)
        self.anchors_base = np.zeros((self.dim, size, size), dtype=np.float64)
        y_grid, x_grid = np.ogrid[:size, :size]
        sigma = 1.5
        for i in range(self.dim):
            dist_sq = (x_grid - self.anchor_x[i])**2 + (y_grid - self.anchor_y[i])**2
            self.anchors_base[i] = np.exp(-dist_sq / (2 * sigma**2))
            
        print(f"[Translator] Initialized TranslatorSpec v0.1 ({self.dim} Anchors, Size {size}x{size})")

    def text_embedding_to_delta(self, embedding_vector: np.ndarray) -> np.ndarray:
        """
        Translates a 1536D embedding vector into a 100x100 physical delta injection mask.
        TranslatorSpec v0.2: Absolute Scaling based on vector norm (depth preserved).
        """
        assert len(embedding_vector) == self.dim, f"Embedding must be {self.dim}D"
        
        # We do NOT force L2 normalization here anymore, relying on the input vector's
        # geometric magnitude to inherently represent semantic mass/weight.
        vec = embedding_vector.reshape(-1, 1, 1)
        mask = np.sum(vec * self.anchors_base, axis=0)
        
        # Extract the absolute topographic deformation magnitude
        mask = np.abs(mask)
        
        # Absolute scale factor (Calibrated such that a 1.0 norm vector yields ~0.7 delta peak)
        delta = np.clip(mask * 5.0, 0.0, 1.0)
        return delta
        
    def read_grid_to_vector(self, psi: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """
        Implements ReadoutSpec v0.1.
        Scans a 10x10 sparse physical grid (100 probes) over the 100x100 space.
        Extracts absolute Psi and Phi, normalizes them, and returns a flat 200D vector.
        """
        assert psi.shape == (self.size, self.size)
        assert phi.shape == (self.size, self.size)
        
        # 10x10 probe grid: step every 10 cells
        step = self.size // 10
        probe_indices = np.arange(step // 2, self.size, step) # Center the probes
        
        psi_mag = np.abs(psi)
        phi_abs = np.abs(phi)
        
        readout = []
        for y in probe_indices:
            for x in probe_indices:
                # TranslatorSpec v0.2 scale adjustments based on expected running Homeostasis norms
                # P-Norm scaled for realistic Max Psi peaks (~2500 - 3500)
                p_norm = np.clip(psi_mag[y, x] / 3000.0, 0.0, 1.0)
                # F-Norm scaled for saturated running topological pressure (~10000)
                f_norm = np.clip(phi_abs[y, x] / 12000.0, 0.0, 1.0)
                
                readout.append(p_norm)
                readout.append(f_norm)
                
        # Returns exactly 200 elements (10 * 10 * 2)
        return np.array(readout, dtype=np.float64)

# Example Usage:
if __name__ == "__main__":
    t = TranslatorV01()
    dummy_embed = np.random.randn(1536)
    delta_out = t.text_embedding_to_delta(dummy_embed)
    print("Delta Mask Shape:", delta_out.shape, "Max:", delta_out.max(), "Min:", delta_out.min())
    
    dummy_psi = np.random.randn(100, 100) + 1j * np.random.randn(100, 100)
    dummy_phi = np.random.randn(100, 100) * 5.0
    vec_r = t.read_grid_to_vector(dummy_psi, dummy_phi)
    print("Readout Vector R Shape:", vec_r.shape, "Max:", vec_r.max(), "Min:", vec_r.min())
