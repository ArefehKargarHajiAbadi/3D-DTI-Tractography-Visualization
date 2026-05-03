import nibabel as nib
import numpy as np
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs

class DataLoader:
    def __init__(self, config):
        self.dti_path = config['data']['dti_file']
        self.bval_path = config['data']['bval_file']
        self.bvec_path = config['data']['bvec_file']

    def load(self):
        img = nib.load(self.dti_path)
        data = img.get_fdata(dtype=np.float32)
        bvals, bvecs = read_bvals_bvecs(self.bval_path, self.bvec_path)
        gtab = gradient_table(bvals=bvals, bvecs=bvecs)
        return data, gtab