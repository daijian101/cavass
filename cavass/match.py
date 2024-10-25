import os
import shutil
from typing import Union, LiteralString

from cavass.ops import matched_reslice
from jbag.io import ensure_output_file_dir_existence

from cavass.constants import CAVASS_START_INDEX
from cavass.slice_range import get_slice_range


def match(unmatched_file: Union[str, LiteralString],
                       file_to_match: Union[str, LiteralString],
                       output_file: Union[str, LiteralString]):
    """
    Match body region.
    Args:
        unmatched_file (str or LiteralString):
        file_to_match (str or LiteralString):
        output_file (str or LiteralString):

    Returns:

    """
    inferior_slice_idx, superior_slice_idx, unmatched_files = get_slice_range(unmatched_file,
                                                                              file_to_match)
    inferior_slice_idx -= CAVASS_START_INDEX
    superior_slice_idx -= CAVASS_START_INDEX

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)
    file_type = os.path.splitext(unmatched_file[0])[1][1:]
    interpolation_method = 'nearest' if file_type == 'BIM' else 'linear'
    try:
        matched_reslice(unmatched_file, file_to_match, output_file,
                        interpolation_method=interpolation_method)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e
    return unmatched_files
