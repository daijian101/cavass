import os
import re
import shutil
import subprocess
import time
import uuid
from typing import Union, LiteralString

from jbag.io import read_mat, save_mat, ensure_output_file_dir_existence

# CAVASS build path, default in installation is ~/cavass-build.
# If CAVASS build path is not in PATH or is not as same as default, set `CAVASS_PROFILE_PATH` to your CAVASS build path.
if os.path.exists(os.path.expanduser('~/cavass-build')):
    CAVASS_PROFILE_PATH = os.path.expanduser('~/cavass-build')
else:
    CAVASS_PROFILE_PATH = None


def env():
    if CAVASS_PROFILE_PATH is not None:
        PATH = f'{os.environ["PATH"]}:{os.path.expanduser(CAVASS_PROFILE_PATH)}'
        VIEWNIX_ENV = os.path.expanduser(CAVASS_PROFILE_PATH)
        return {'PATH': PATH, 'VIEWNIX_ENV': VIEWNIX_ENV}
    return None


def execute_cmd(cavass_cmd):
    p = subprocess.Popen(cavass_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env())
    r, e = p.communicate()
    try:
        r = r.decode()
    except UnicodeDecodeError:
        r = r.decode('gbk')
    e = e.decode().strip()
    if e:
        e_lines = e.splitlines()
        line_0_correct_pattern = r'^VIEWNIX_ENV=(/[^/\0]+)+/?$'
        line_0 = e_lines[0]
        matched_env = re.match(line_0_correct_pattern, line_0)
        if len(e_lines) > 1 or not matched_env:
            raise OSError(f'Error occurred when executing command:\n{cavass_cmd}\nError message is\n{e}')
    r = r.strip()
    return r


def get_image_resolution(input_file):
    """
    Get (H,W,D) resolution of input_file.

    Args:
        input_file (str or LiteralString):

    Returns:
    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    cmd = f'get_slicenumber {input_file} -s'
    r = execute_cmd(cmd)
    r = r.split('\n')[2]
    r = r.split(' ')
    r = tuple(map(lambda x: int(x), r))
    return r


def get_voxel_spacing(input_file):
    """
    Get spacing between voxels.

    Args:
        input_file (str or LiteralString):

    Returns:

    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    cmd = f'get_slicenumber {input_file} -s'
    r = execute_cmd(cmd)
    r = r.split('\n')[0]
    r = r.split(' ')
    r = tuple(map(lambda x: float(x), r))
    return r


def get_slice_number(input_file):
    """
    CAVASS `get_slicenumber {input_file} -s`.

    Args:
        input_file (str or LiteralString):

    Returns:

    """
    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    cmd = f'get_slicenumber {input_file} -s'
    r = execute_cmd(cmd)
    results = []
    for each_line in r.splitlines():
        results.extend(each_line.split(' '))
    return tuple(map(lambda x: float(x), results))


def read_cavass_file(input_file, first_slice=None, last_slice=None, sleep_time=0):
    """
    Load data of input_file.
    Use the assigned slice indices if both the first slice and the last slice are given.

    Args:
        input_file (str or LiteralString):
        first_slice (int or None, optional, default=None): Loading from the first slice (included). Load from the
            inferior slice if first_slice is None.
        last_slice (int or None, optional, default=None): Loading end at the last_slice (included). Loading ends up at
            the superior slice if last_slice is None.
        sleep_time (int, optional, default=0): Set a sleep_time between saving and loading temp mat to avoid system IO
            error if necessary. Default is 0.

    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    tmp_path = os.path.expanduser('~/tmp/cavass')
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path, exist_ok=True)

    output_file = os.path.join(tmp_path, f'{uuid.uuid1()}.mat')
    if first_slice is None or last_slice is None:
        cvt2mat = f'exportMath {input_file} matlab {output_file} `get_slicenumber {input_file}`'
    else:
        cvt2mat = f'exportMath {input_file} matlab {output_file} {first_slice} {last_slice}'
    try:
        execute_cmd(cvt2mat)
    except Exception as e:
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e
    if sleep_time > 0:
        time.sleep(sleep_time)
    ct = read_mat(output_file)
    os.remove(output_file)
    return ct


def copy_pose(input_file_1, input_file_2, output_file):
    """
    Copy pose of `input_file_2` to `input_file_1`, output to `output_file`.
    Args:
        input_file_1:
        input_file_2:
        output_file:

    Returns:

    """
    assert os.path.isfile(input_file_1), f'{input_file_1} does not exist or is not a file!'
    assert os.path.isfile(input_file_2), f'{input_file_2} does not exist or is not a file!'

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    try:
        execute_cmd(f'copy_pose {input_file_1} {input_file_2} {output_file}')
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e


def save_cavass_file(output_file,
                     data,
                     binary=False,
                     size: Union[None, list[int], tuple[int, ...]] = None,
                     spacing: Union[None, list[float], tuple[float, ...]] = None,
                     copy_pose_file=None):
    """
    Save data as CAVASS format. Do not provide spacing and reference_file at the same time. Recommend to use binary for
    mask files and reference_file to copy all properties.

    Args:
        output_file (str or LiteralString):
        data (numpy.ndarray):
        binary (bool, optional, default=False): Save as binary data if True.
        size (sequence or None, optional, default=None): Array size for converting CAVASS format. Default is None,
            setting the shape of input data array to `size`.
        spacing (sequence or None, optional, default=None): Voxel spacing. Default is None, set (1, 1, 1) to `spacing`.
        copy_pose_file (str or LiteralString or None, optional, default=None): If `copy_pose_file` is given, copy pose
            from the given file to the `output_file`.
    """

    assert spacing is None or copy_pose_file is None
    if copy_pose_file is not None:
        assert os.path.exists(copy_pose_file), f'{copy_pose_file} does not exist!'

    if size is None:
        size = data.shape
    assert len(size) == 3
    size = ' '.join(list(map(lambda x: str(x), size)))

    spacing = ' '.join(list(map(lambda x: str(x), spacing))) if spacing is not None else ''

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    tmp_files = []
    tmp_mat = os.path.join(output_dir, f'tmp_{uuid.uuid1()}.mat')
    tmp_files.append(tmp_mat)
    save_mat(tmp_mat, data)

    if not binary:
        if copy_pose_file is None:
            try:
                execute_cmd(f'importMath {tmp_mat} matlab {output_file} {size} {spacing}')
            except Exception as e:
                if made_output_dir and os.path.isdir(output_dir):
                    shutil.rmtree(output_dir)
                for tmp_file in tmp_files:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                raise e
        else:
            tmp_file = os.path.join(output_dir, f'tmp_{uuid.uuid1()}.IM0')
            tmp_files.append(tmp_file)
            try:
                execute_cmd(f'importMath {tmp_mat} matlab {tmp_file} {size}')
                copy_pose(tmp_file, copy_pose_file, output_file)
            except Exception as e:
                if made_output_dir and os.path.isdir(output_dir):
                    shutil.rmtree(output_dir)
                for tmp_file in tmp_files:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                raise e

    if binary:
        if copy_pose_file is None:
            tmp_file = os.path.join(output_dir, f'tmp_{uuid.uuid1()}.IM0')
            tmp_files.append(tmp_file)
            try:
                execute_cmd(f'importMath {tmp_mat} matlab {tmp_file} {size} {spacing}')
                execute_cmd(f'ndthreshold {tmp_file} {output_file} 0 1 1')
            except Exception as e:
                if made_output_dir and os.path.isdir(output_dir):
                    shutil.rmtree(output_dir)
                for tmp_file in tmp_files:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                raise e
        else:
            tmp_file = os.path.join(output_dir, f'tmp_{uuid.uuid1()}.IM0')
            tmp_files.append(tmp_file)
            try:
                execute_cmd(f'importMath {tmp_mat} matlab {tmp_file} {size}')
            except Exception as e:
                if made_output_dir and os.path.isdir(output_dir):
                    shutil.rmtree(output_dir)
                for tmp_file in tmp_files:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                raise e

            tmp_file1 = os.path.join(output_dir, f'tmp_{uuid.uuid1()}.BIM')
            tmp_files.append(tmp_file1)
            try:
                execute_cmd(f'ndthreshold {tmp_file} {tmp_file1} 0 1 1')
                copy_pose(tmp_file1, copy_pose_file, output_file)
            except Exception as e:
                if made_output_dir and os.path.isdir(output_dir):
                    shutil.rmtree(output_dir)
                for tmp_file in tmp_files:
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                raise e

    for each in tmp_files:
        os.remove(each)


def bin_ops(input_file_1, input_file_2, output_file, op):
    """
    Execute binary operations.

    Args:
        input_file_1 (str or LiteralString):
        input_file_2 (str or LiteralString):
        output_file (str or LiteralString):
        op (str): `or` | `nor` | `xor` | `xnor` | `and` | `nand` | `a-b`.
    """

    assert os.path.isfile(input_file_1), f'{input_file_1} does not exist or is not a file!'
    assert os.path.isfile(input_file_2), f'{input_file_2} does not exist or is not a file!'

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    cmd_str = f'bin_ops {input_file_1} {input_file_2} {output_file} {op}'
    try:
        execute_cmd(cmd_str)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e


def median2d(input_file, output_file, mode=0):
    """
    Perform median filter.

    Args:
        input_file (str or LiteralString):
        output_file (str or LiteralString):
        mode (int, optional, default=0): 0 for foreground, 1 for background, default is 0.
    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    try:
        execute_cmd(f'median2d {input_file} {output_file} {mode}')
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e


def export_math(input_file, output_file, output_file_type='matlab', first_slice=-1, last_slice=-1):
    """
    Export CAVASS format file to other formats.

    Args:
        input_file (str or LiteralString):
        output_file (str or LiteralString):
        output_file_type (str, optional, default="matlab"): Support format: `mathematica` | `mathlab` | `r` | `vtk`.
        first_slice (int, optional, default=-1): Perform from `first_slice`. If -1, `first slice` is set to 0.
        last_slice (int, optional, default=-1): Perform ends up on `last_slice`. If -1, `last_slice` is set to the max
            slice index of input image.
    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    first_slice = 0 if first_slice == -1 else first_slice
    if last_slice == -1:
        resolution = get_image_resolution(input_file)
        last_slice = resolution[2] - 1

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    try:
        execute_cmd(f'exportMath {input_file} {output_file_type} {output_file} {first_slice} {last_slice}')
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e


def render_surface(input_bim_file, output_file):
    """
    Render surface of segmentation. The output file should with postfix of `BS0`.
    Note that the rendering script may fail when saving output file in extension disks/partitions.
    I don't know the exact reason for this problem.  But it seems related to the **track_all** script.
    Script "track_all {input_IM0_file} {output_file} 1.000000 115.000000 254.000000 26 0 0" can't save
    output file to disks/partitions except the system disk/partition.

    Args:
        input_bim_file (str or LiteralString):
        output_file (str or LiteralString):
    """

    assert os.path.isfile(input_bim_file), f'{input_bim_file} does not exist or is not a file!'

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    interpl_tmp_bim_file = os.path.join(output_dir, f'{uuid.uuid1()}.BIM')
    ndinterpolate_cmd = f'ndinterpolate {input_bim_file} {interpl_tmp_bim_file} 0 `get_slicenumber {input_bim_file} -s | head -c 9` `get_slicenumber {input_bim_file} -s | head -c 9` `get_slicenumber {input_bim_file} -s | head -c 9` 1 1 1 1 `get_slicenumber {input_bim_file}`'
    try:
        execute_cmd(ndinterpolate_cmd)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(interpl_tmp_bim_file):
            os.remove(interpl_tmp_bim_file)
        raise e

    gaussian_tmp_im0_file = os.path.join(output_dir, f'{uuid.uuid1()}.IM0')
    gaussian_cmd = f'gaussian3d {interpl_tmp_bim_file} {gaussian_tmp_im0_file} 0 1.500000'
    try:
        execute_cmd(gaussian_cmd)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(interpl_tmp_bim_file):
            os.remove(interpl_tmp_bim_file)
        if os.path.exists(gaussian_tmp_im0_file):
            os.remove(gaussian_tmp_im0_file)
        raise e

    render_cmd = f'track_all {gaussian_tmp_im0_file} {output_file} 1.000000 115.000000 254.000000 26 0 0'
    try:
        execute_cmd(render_cmd)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(interpl_tmp_bim_file):
            os.remove(interpl_tmp_bim_file)
        if os.path.exists(gaussian_tmp_im0_file):
            os.remove(gaussian_tmp_im0_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e

    os.remove(interpl_tmp_bim_file)
    os.remove(gaussian_tmp_im0_file)

    if not os.path.exists(output_file):
        raise FileNotFoundError(
            f'Output file {output_file} fails to created. Try saving output file to system disk to solve this problem.')


def ndvoi(input_file: Union[str, LiteralString], output_file: Union[str, LiteralString], mode: int = 0,
          offset_x=0, offset_y=0, new_width=0, new_height=0, min_intensity: int = 0, max_intensity: int = 0,
          min_slice_dim_3=None, max_slice_dim_3=None, min_slice_dim_4=None, max_slice_dim_4=None):
    """
    CAVASS `ndvoi input output mode [offx offy new_width new_height min max [min3 max3] [min4 max4] | [z]margin]`
    Args:
        input_file (str or LiteralString):
        output_file (str or LiteralString):
        mode (int, optional, default=0): Mode of operation (0=foreground, 1=background).
        offset_x (int or float, optional, default=0): Offset of the origin of the new scene in respect to input scene.
        offset_y (int or float, optional, default=0): Offset of the origin of the new scene in respect to input scene.
        new_width (int, optional, default=0): Dimensions (in pixels) of new scene(0=original dimensions).
        new_height (int, optional, default=0): Dimensions (in pixels) of new scene(0=original dimensions).
        min_intensity (int, optional, default=0): Grey window for the pixels values (0 = entire range).
        max_intensity (int, optional, default=0): Grey window for the pixels values (0 = entire range).
        min_slice_dim_3 (int or None, optional, default=None): Min slice along the third axis.
        max_slice_dim_3 (int or None, optional, default=None): Max slice along the third axis.
        min_slice_dim_4 (int or None, optional, default=None): Min slice along the fourth axis.
        max_slice_dim_4 (int or None, optional, default=None): Max slice along the fourth axis.

    Returns:

    """

    assert os.path.isfile(input_file), f'{input_file} does not exist or is not a file!'

    assert mode in [0, 1], f'{mode} is not a valid mode. (0=foreground, 1=background)'

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    cmd = f'ndvoi {input_file} {output_file} {mode} {offset_x} {offset_y} {new_width} {new_height} {min_intensity} {max_intensity}'
    if min_slice_dim_3 is not None:
        cmd += f' {min_slice_dim_3}'
    if max_slice_dim_3 is not None:
        cmd += f' {max_slice_dim_3}'
    if min_slice_dim_4 is not None:
        cmd += f' {min_slice_dim_4}'
    if max_slice_dim_4 is not None:
        cmd += f' {max_slice_dim_4}'
    try:
        execute_cmd(cmd)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e


def matched_reslice(file_to_reslice: Union[str, LiteralString], file_to_match: Union[str, LiteralString],
                    output_file: Union[str, LiteralString], matrix=None, interpolation_method: str = 'linear',
                    landmark=None, new_loc=None):
    """
    Position the content of file_to_reslice in the correct location in file_to_match.

    Args:
        file_to_reslice (str or LiteralString):
        file_to_match (str or LiteralString):
        output_file (str or LiteralString):
        matrix (optional, default=None): 4x3 rigid transformation from scanner coordinate system of `file_to_reslice` to `file_to_match`.
        interpolation_method (str, optional, default="linear"): Interpolation method, supported options are `linear` and `nearest`.
        landmark (optional, default=None): Scanner coordinates of landmark in input scene to reslice
        new_loc (optional, default=None): New location of landmark in scanner coordinate system.

    Returns:

    """
    assert os.path.isfile(file_to_reslice), f'{file_to_reslice} does not exist or is not a file!'
    assert os.path.isfile(file_to_match), f'{file_to_match} does not exist or is not a file!'

    assert interpolation_method in ['linear', 'nearest'], (
        f'{interpolation_method} is not a valid interpolation method.'
        f' Support interpolation methods are `linear` and `nearest`.')
    interpolation_method = interpolation_method[0]

    made_output_dir, output_dir = ensure_output_file_dir_existence(output_file)

    cmd = f'matched_reslice {file_to_reslice} {file_to_match} {output_file}'
    # TODO: don't konw the format of matrix for now.
    if matrix is not None:
        cmd += f' {matrix}'

    cmd += f' -{interpolation_method}'

    # TODO: don't know how landmark and new_loc look like.
    if landmark is not None:
        cmd += f' {landmark}'
    if new_loc is not None:
        cmd += f' {new_loc}'
    try:
        execute_cmd(cmd)
    except Exception as e:
        if made_output_dir and os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(output_file):
            os.remove(output_file)
        raise e
