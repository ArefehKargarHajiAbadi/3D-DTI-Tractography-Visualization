from dipy.reconst.dti import TensorModel, fractional_anisotropy
import numpy as np

class TensorFitter:
    """Fit diffusion tensor and compute FA."""
    def __init__(self, data, gtab):
        self.data = data
        self.gtab = gtab
        self.model = TensorModel(gtab)

    def compute_fa(self):
        try:
            fit = self.model.fit(self.data)
            fa = fractional_anisotropy(fit.evals)
            # Clip to valid range and mask NaN
            fa = np.nan_to_num(fa, nan=0.0)
            fa = np.clip(fa, 0.0, 1.0)
            return fa, fit
        except Exception as e:
            raise RuntimeError(f"Tensor fitting failed: {e}")