import os.path
import shutil
import uuid
from typing import Union

from cavass._io import ensure_output_file_dir_existence
from cavass.constants import CAVASS_START_INDEX
from cavass.ops import ndvoi, matched_reslice, bin_ops
from cavass.slice_range import get_slice_range


def integrate_trimmed_images(trimmed_files: Union[list[str], tuple[str]],
                             reference_file: str,
                             output_file_1: str,
                             output_file_2: str, ):
    """
    Suture trimmed CAVASS files.
    For the situation that the whole file is trimmed into multiple files of body regions, this script integrates
    multiple trimmed files into one file.
    The ROI of the new file is determined by the provided trimmed files, which is the region exactly contains all
    trimmed files and may not be the same as the ROI of original untrimmed file.

    Args:
        trimmed_files (tuple or list): Trimmed files. trimmed files must be arranged correctly in the order of form inferior to superior.
        reference_file (str): File to match.
        output_file_1 (str): `output_file_1` is the output file trimmed from the reference file according to the ROI obtained from the trimmed files.`
        output_file_2 (str): `output_file_2` is the output file of integrated files of the untrimmed files.

    Returns:

    """

    assert os.path.exists(reference_file), f'{reference_file} does not exist!.'
    for each in trimmed_files:
        assert os.path.exists(each), f'{each} does not exist!.'

    # Get ROI from the first and last untrimmed files.
    # The inferior location is the inferior location of the first trimmed image in the untrimmed image.
    # The superior location is the superior location of the last trimmed image in the untrimmed image.
    all_unmatched_files = []
    inferior_slice_idx, _, unmatched_files = get_slice_range(trimmed_files[0], reference_file)
    all_unmatched_files.extend(unmatched_files)
    _, superior_slice_idx, unmatched_files = get_slice_range(trimmed_files[-1], reference_file)
    all_unmatched_files.extend(unmatched_files)

    # CAVASS uses index started from 1.
    inferior_slice_idx -= CAVASS_START_INDEX
    superior_slice_idx -= CAVASS_START_INDEX

    # The new ROI is [inferior_slice_idx, superior_slice_idx]
    # Trim from original untrimmed file.

    made_output_dir_1, output_dir_1 = ensure_output_file_dir_existence(output_file_1)

    try:
        ndvoi(reference_file, output_file_1, min_slice_dim_3=inferior_slice_idx, max_slice_dim_3=superior_slice_idx)
    except Exception as e:
        if made_output_dir_1 and os.path.isdir(output_dir_1):
            shutil.rmtree(output_dir_1)
        if os.path.exists(output_file_1):
            os.remove(output_file_1)
        raise e

    made_output_dir_2, output_dir_2 = ensure_output_file_dir_existence(output_file_2)

    # create reslice files of trimmed files w.r.t untrimmed file.
    tmp_files = []
    reslice_files = []
    file_type = os.path.splitext(trimmed_files[0])[1][1:]
    interpolation_method = 'nearest' if file_type == 'BIM' else 'linear'
    for trimmed_file in trimmed_files:
        reslice_file = os.path.join(output_dir_2, f'{uuid.uuid1()}.{file_type}')
        tmp_files.append(reslice_file)
        reslice_files.append(reslice_file)
        try:
            matched_reslice(trimmed_file, reference_file, reslice_file, interpolation_method=interpolation_method)
        except Exception as e:
            if made_output_dir_1 and os.path.isdir(output_dir_1):
                shutil.rmtree(output_dir_1)
            if os.path.exists(output_file_1):
                os.remove(output_file_1)

            if made_output_dir_2 and os.path.isdir(output_dir_2):
                shutil.rmtree(output_dir_2)
            for each in tmp_files:
                if os.path.exists(each):
                    os.remove(each)
            raise e

    # integrate reslice files by OR operation.
    if len(reslice_files) > 1:
        or_op_file_1 = reslice_files[0]
        or_op_file_2 = reslice_files[1]
        or_op_output_file = os.path.join(output_dir_2, f'{uuid.uuid1()}.{file_type}')
        or_op_output_files = [or_op_output_file]
        tmp_files.append(or_op_output_file)
        bin_ops(or_op_file_1, or_op_file_2, or_op_output_file, op='or')
        if len(reslice_files) > 2:
            for reslice_file in reslice_files[2:]:
                or_op_file_1 = or_op_output_files[-1]
                or_op_file_2 = reslice_file
                or_op_output_file = os.path.join(output_dir_2, f'{uuid.uuid1()}.{file_type}')
                or_op_output_files.append(or_op_output_file)
                tmp_files.append(or_op_output_file)
                try:
                    bin_ops(or_op_file_1, or_op_file_2, or_op_output_file, op='or')
                except Exception as e:
                    if made_output_dir_1 and os.path.isdir(output_dir_1):
                        shutil.rmtree(output_dir_1)
                    if os.path.exists(output_file_1):
                        os.remove(output_file_1)

                    if made_output_dir_2 and os.path.isdir(output_dir_2):
                        shutil.rmtree(output_dir_2)
                    for each in tmp_files:
                        if os.path.exists(each):
                            os.remove(each)
                    raise e

        output_file = or_op_output_files[-1]
    else:
        output_file = reslice_files[0]

    # reslice to otuput file 1
    try:
        matched_reslice(output_file, output_file_1, output_file_2, interpolation_method=interpolation_method)
    except Exception as e:
        if made_output_dir_1 and os.path.isdir(output_dir_1):
            shutil.rmtree(output_dir_1)
        if os.path.exists(output_file_1):
            os.remove(output_file_1)

        if made_output_dir_2 and os.path.isdir(output_dir_2):
            shutil.rmtree(output_dir_2)
        for each in tmp_files:
            if os.path.exists(each):
                os.remove(each)
        raise e

    for each in tmp_files:
        if os.path.exists(each):
            os.remove(each)
    return all_unmatched_files
