from dipy.tracking import utils
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.stopping_criterion import ThresholdStoppingCriterion
from dipy.tracking.streamline import Streamlines
import numpy as np

class TractographyGenerator:
    """Generate 3D white matter streamlines using deterministic tracking."""
    def __init__(self, fa_map, tensor_fit, config):
        self.fa = fa_map
        self.tensor_fit = tensor_fit
        self.fa_thresh = config['tracking']['fa_threshold']
        self.step_size = config['tracking']['step_size']
        self.seed_count = config['tracking']['seed_count']
        self.max_angle = config['tracking']['max_angle']

    def _create_seeds(self):
        """Generate seeds in regions with FA above threshold."""
        mask = self.fa > self.fa_thresh
        seed_indices = utils.seeds_from_mask(mask, density=self.seed_count, return_indices=True)
        return seed_indices

    def track(self):
        mask = self.fa > self.fa_thresh
        stopping_criterion = ThresholdStoppingCriterion(self.fa, self.fa_thresh)
        directions = self.tensor_fit.directions

        seeds = self._create_seeds()
        streamlines = LocalTracking(
            directions, stopping_criterion, seeds,
            affine=np.eye(4), step_size=self.step_size, max_angle=self.max_angle
        )
        # Convert generator to list and filter short streamlines
        tracts = [s for s in streamlines if len(s) > 10]
        return Streamlines(tracts)