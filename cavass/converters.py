import os
import shutil
from uuid import uuid1

import numpy as np

from cavass._io import ensure_output_file_dir_existence, save_nifti
from cavass.dicom import Modality
from cavass.nifti2dicom import nifti2dicom
from cavass.ops import execute_cmd, get_voxel_spacing, read_cavass_file, copy_pose
from cavass.utils import one_hot


def dicom2cavass(input_dicom_dir, output_file, offset=0, copy_pose_file=None):
    """
    Note that if the output file path is too long, this command may be failed.

    Args:
        input_dicom_dir (str):
        output_file (str):
        offset (int, optional, default=0):
        copy_pose_file (str, optional, default=None): If `copy_pose_file` is given, copy pose of this
        file to the output file.

    """

    if not os.path.exists(input_dicom_dir):
        raise ValueError(f"Input DICOM series {input_dicom_dir} does not exist.")
    if copy_pose_file is not None:
        if not os.path.isfile(copy_pose_file):
            raise FileNotFoundError(f"Copy pose file {copy_pose_file} does not exist.")

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    input_dicom_dir = input_dicom_dir.replace(" ", "\ ")
    output_file = output_file.replace(" ", "\ ")
    try:
        if copy_pose_file is None:
            r = execute_cmd(f"from_dicom {input_dicom_dir}/* {output_file} +{offset}")
        else:
            split = os.path.splitext(output_file)
            root = split[0]
            extension = split[1]
            output_tmp_file = root + "_TMP" + extension
            r = execute_cmd(f"from_dicom {input_dicom_dir}/* {output_tmp_file} +{offset}")
            copy_pose(output_tmp_file, copy_pose_file, output_file)

    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

        if copy_pose_file is not None and os.path.exists(output_tmp_file):
            os.remove(output_tmp_file)

        if os.path.exists(output_file):
            os.remove(output_file)
        raise e
    return r


def nifti2cavass(input_nifti_file, output_file, modality, offset=0, copy_pose_file=None):
    """
    Convert NIfTI image to cavass image.

    Args:
        input_nifti_file (str):
        output_file (str):
        modality (Modality):
        offset (int, optional, default=0):
        copy_pose_file (str, optional, default=None):
    """

    if not os.path.isfile(input_nifti_file):
        raise FileNotFoundError(f"Input NIfTI file {input_nifti_file} does not exist.")

    if copy_pose_file is not None:
        if not os.path.isfile(copy_pose_file):
            raise FileNotFoundError(f"Copy pose file {input_nifti_file} does not exist.")

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    tmp_dicom_dir = os.path.join(output_dir, f"{uuid1()}")
    try:
        r1 = nifti2dicom(input_nifti_file, tmp_dicom_dir, modality=modality, force_overwrite=True)
        r2 = dicom2cavass(tmp_dicom_dir, output_file, offset, copy_pose_file)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.isdir(tmp_dicom_dir):
            shutil.rmtree(tmp_dicom_dir)
        if os.path.exists(output_file):
            os.remove(output_file)

        raise e
    shutil.rmtree(tmp_dicom_dir)
    return r1, r2


def cavass2nifti(input_file, output_file, orientation="ARI"):
    """
    Convert cavass IM0 and BIM formats to NIfTI.

    Args:
        input_file (str):
        output_file (str):
        orientation (str, optional, default="ARI"): Image orientation of NIfTI file, "ARI" or "LPI"

    Returns:

    """

    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")

    spacing = get_voxel_spacing(input_file)
    data = read_cavass_file(input_file)
    save_nifti(output_file, data, spacing, orientation=orientation)


def nifti_label2cavass(input_nifti_file, output_file, objects,
                       modality=Modality.CT, discard_background=True, copy_pose_file=None):
    """
    Convert NIfTI format segmentation file to cavass BIM format file. A NIfTI file in where contains arbitrary categories
    of objects will convert to multiple CAVASS BIM files, which matches to the number of object categories.

    Args:
        input_nifti_file (str):
        output_file (str): The final saved file for category i in input segmentation will be
        `output_file_prefix_{objects[i]}.BIM`
        objects (sequence or str): Objects is an array or a string with comma splitter of object categories,
        where the index of the category in the array is the number that indicates the category in the segmentation.
        modality (Modality, optional, default=Modality.CT):
        discard_background (bool, optional, default True): If True, the regions with label of 0 in the segmentation
        (typically refer to the background region) will not be saved.
        copy_pose_file (str, optional, default=None):

    Returns:

    """
    import nibabel as nib

    if not os.path.isfile(input_nifti_file):
        raise FileNotFoundError(f"Input NIfTI file {input_nifti_file} does not exist.")

    if copy_pose_file is not None:
        if not os.path.isfile(copy_pose_file):
            raise FileNotFoundError(f"Copy pose file {copy_pose_file} does not exist.")

    input_data = nib.load(input_nifti_file)
    image_data = input_data.get_fdata()

    if isinstance(objects, str):
        objects = objects.split(",")
    n_classes = len(objects) + 1 if discard_background else len(objects)
    one_hot_arr = one_hot(image_data, num_classes=n_classes)

    start = 1 if discard_background else 0
    for i in range(start, one_hot_arr.shape[3]):
        nifti_label_image = nib.Nifti1Image(one_hot_arr[..., i], input_data.affine, input_data.header, dtype=np.uint8)
        if discard_background:
            obj = objects[i - 1]
        else:
            obj = objects[i]
        tmp_nifti_file = f"{output_file}_{obj}.nii.gz"
        made_output_dir, output_dir = ensure_output_file_dir_existence(tmp_nifti_file)
        try:
            nib.save(nifti_label_image, tmp_nifti_file)
            nifti2cavass(tmp_nifti_file, f"{output_file}_{obj}.BIM", modality, copy_pose_file=copy_pose_file)
        except Exception as e:
            if made_output_dir and os.path.isdir(output_dir):
                shutil.rmtree(output_dir)
            if os.path.exists(tmp_nifti_file):
                os.remove(tmp_nifti_file)
            raise e
        os.remove(tmp_nifti_file)
