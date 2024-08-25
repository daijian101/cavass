import numpy as np
from jbag.image import windowing


def cavass_soft_tissue_windowing(input_data):
    return windowing(input_data, 1000, 500)


def cavass_bone_windowing(input_data):
    return windowing(input_data, 2000, 4000)


def cavass_pet_windowing(input_data):
    return windowing(input_data, 1200, 3500, invert=True)