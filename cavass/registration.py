import os.path
import shutil

import numpy as np

from cavass.ops import get_image_resolution, read_cavass_file, save_cavass_file


def register_im0_bim(im0_file, bim_file, output_bim_file):
    shape_1 = get_image_resolution(im0_file)
    shape_2 = get_image_resolution(bim_file)
    output_dir = os.path.split(output_bim_file)[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    if shape_1[2] == shape_2[2]:
        shutil.copy(bim_file, output_bim_file)
    else:
        original_data = read_cavass_file(bim_file)
        data = np.zeros(shape_1, dtype=bool)
        data[..., :original_data.shape[2]] = original_data
        save_cavass_file(output_bim_file, data, True, reference_file=im0_file)
