from cavass._log import logger
from cavass.ops import get_slice_number


def get_slice_range(partial_region_file: str, entire_region_file: str):
    """
    Get the slice location range where the `portion file` is located in the `entire region file`.

    Args:
        partial_region_file (str):
        entire_region_file (str):

    Returns:

    """
    slice_number_1 = get_slice_number(partial_region_file)
    slice_number_2 = get_slice_number(entire_region_file)
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
        logger.warning(
            f"Input files do not match.\nInput file 1 is {partial_region_file}.\nInput file 2 is {entire_region_file}.")
        unmatched = [partial_region_file, entire_region_file]
    else:
        unmatched = []
    return inferior_slice_idx, superior_slice_idx, unmatched
