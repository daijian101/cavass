import os.path
import shutil

import numpy as np
from jbag.io import ensure_output_file_dir_existence

from cavass.ops import get_image_resolution, read_cavass_file, save_cavass_file


def match_im0_bim(im0_file, bim_file, output_bim_file):
    assert os.path.isfile(im0_file), f'{im0_file} does not exist or is not a file!'
    assert os.path.isfile(bim_file), f'{bim_file} does not exist or is not a file!'

    shape_1 = get_image_resolution(im0_file)
    shape_2 = get_image_resolution(bim_file)

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_bim_file)

    if shape_1[2] == shape_2[2]:
        shutil.copy(bim_file, output_bim_file)
    else:
        original_data = read_cavass_file(bim_file)
        data = np.zeros(shape_1, dtype=bool)
        data[..., :original_data.shape[2]] = original_data
        try:
            save_cavass_file(output_bim_file, data, True, copy_pose_file=im0_file)
        except Exception as e:
            if made_output_dir and os.path.isdir(output_dir):
                shutil.rmtree(output_dir)
            if os.path.exists(output_bim_file):
                os.remove(output_bim_file)
            raise e
