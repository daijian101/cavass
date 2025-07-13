import os

import numpy as np


def read_mat(input_file, key="scene"):
    from scipy.io import loadmat
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file {input_file} does not exist.")
    data = loadmat(input_file)[key]
    return data


def save_mat(output_file, data, key="scene"):
    from scipy.io import savemat
    ensure_output_file_dir_existence(output_file)
    savemat(output_file, {key: data})


def save_nifti(output_file,
               data,
               voxel_spacing=None,
               orientation="LPI"):
    """
    Save image with nii format.

    Args:
        output_file (str):
        data (numpy.ndarray):
        voxel_spacing (sequence or None, optional, default=None): `tuple(x, y, z)`. Voxel spacing of each axis. If None,
            make `voxel_spacing` as `(1.0, 1.0, 1.0)`.
        orientation (str, optional, default="LPI"): "LPI" | "ARI". LPI: Left-Posterior-Inferior;
            ARI: Anterior-Right-Inferior.

    Returns:

    """
    if voxel_spacing is None:
        voxel_spacing = (1.0, 1.0, 1.0)  # replace this with your desired voxel spacing in millimeters

    match orientation:
        case "LPI":
            affine_matrix = np.diag(list(voxel_spacing) + [1.0])
        case "ARI":
            # calculate the affine matrix based on the desired voxel spacing and ARI orientation
            affine_matrix = np.array([
                [0, -voxel_spacing[0], 0, 0],
                [-voxel_spacing[1], 0, 0, 0],
                [0, 0, voxel_spacing[2], 0],
                [0, 0, 0, 1]
            ])
        case _:
            raise ValueError(f"Unsupported orientation {orientation}.")

    # create a NIfTI image object
    import nibabel as nib
    ensure_output_file_dir_existence(output_file)
    nii_img = nib.Nifti1Image(data, affine=affine_matrix)
    nib.save(nii_img, output_file)


def ensure_output_dir_existence(output_dir):
    mk_output_dir = not os.path.exists(output_dir)
    if mk_output_dir:
        os.makedirs(output_dir)
    return mk_output_dir, output_dir


def ensure_output_file_dir_existence(output_file):
    output_dir = os.path.split(output_file)[0]
    return ensure_output_dir_existence(output_dir)
