import os
import shutil
from uuid import uuid4

from jbag.io import save_nii
from jbag.medical_image_converters import nifti2dicom

from cavass.ops import execute_cmd, get_voxel_spacing, read_cavass_file


def dicom2cavass(input_dir, output_file, offset_value=0):
    """
    Note that if the output file path is too long, this command may be failed.

    Args:
        input_dir (str or pathlib.Path):
        output_file (str or pathlib.Path):
        offset_value (int, optional, default=0):

    """

    file_dir, file = os.path.split(output_file)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    r = execute_cmd(f"from_dicom {input_dir}/* {output_file} +{offset_value}")
    return r


def nifti2cavass(input_file, output_file, offset_value=0, dicom_accession_number=1):
    """
    Convert nifti image to cavass image.

    Args:
        input_file (str or pathlib.Path):
        output_file (str or pathlib.Path):
        offset_value (int, optional, default=0):
        dicom_accession_number (int, optional, default=1):
    """

    save_path = os.path.split(output_file)[0]
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
    tmp_dicom_dir = os.path.join(save_path, f"{uuid4()}")
    r1 = nifti2dicom(input_file, tmp_dicom_dir, dicom_accession_number)
    r2 = dicom2cavass(tmp_dicom_dir, output_file, offset_value)
    shutil.rmtree(tmp_dicom_dir)
    return r1, r2


def cavass2nifti(input_file, output_file, orientation="ARI"):
    """
    Convert cavass IM0 and BIM formats to NIFTI.

    Args:
        input_file (str or pathlib.Path):
        output_file (str or pathlib.Path):
        orientation (str, optional, default="ARI"): Image orientation of nifti file, `ARI` or 'LPI'

    Returns:

    """

    spacing = get_voxel_spacing(input_file)
    data = read_cavass_file(input_file)
    save_nii(output_file, data, spacing, orientation=orientation)
