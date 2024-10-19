from typing import Union, LiteralString

from jbag.log import logger

from cavass.ops import get_slice_number


def get_slice_range(input_file_1: Union[str, LiteralString], input_file_2: Union[str, LiteralString]):
    """
    Get the slice location range where the input file 1 is located in the input file 2.

    Args:
        input_file_1 (str or LiteralString):
        input_file_2 (str or LiteralString):

    Returns:

    """
    slice_number_1 = get_slice_number(input_file_1)
    slice_number_2 = get_slice_number(input_file_2)
    # inferior slice refers to the index of slice in input_file_2 where
    # the inferior slice (the first slice) of input_file_1 located in input_file_2.
    # While the superior slice indicates the slice index in input_file_2
    # where the superior slice (the last slice) of input_file_1 located in input_file_2.
    inferior_slice_idx = round((slice_number_1[5] - slice_number_2[5]) / slice_number_2[2])
    superior_slice_idx = inferior_slice_idx + int(slice_number_1[8])
    inferior_slice_idx += 1
    if (slice_number_1[0] != slice_number_2[0]) or (slice_number_1[1] != slice_number_2[1]) or (
            slice_number_1[2] != slice_number_2[2]) or (slice_number_1[3] != slice_number_2[3]) or (
            slice_number_1[4] != slice_number_2[4]) or (slice_number_1[6] != slice_number_2[6]) or (
            slice_number_1[7] != slice_number_2[7]):
        logger.warning(f'Input files do not match.\nInput file 1 is {input_file_1}.\nInput file 2 is {input_file_2}.')
    return inferior_slice_idx, superior_slice_idx
