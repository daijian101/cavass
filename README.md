# CAVASS Python Library

[toc]

This library implements medical image processing methods involving using CAVASS software in Python environment.

## Installation

`pip install cavass`

## Structure

**ops.py** contains codes that implement CAVASS shell commands, like reading CAVASS format files, saving CAVASS format
files, etc.

**contrast_enhancement.py** contains windowing functions predefined in CAVASS GUI (soft tissue, bone, and PET).

**converters.py** includes codes for converting medical image file formats, like converting images from NifTI format to
CAVASS format.

**registration.py** includes methods of matching images and segmentations for now.

## Usage

### Set CAVASS build path

To use this package, Linux version of CAVASS is necessary to be
installed, https://www.mipg.upenn.edu/Vnews/mipg_software.html. And the CAVASS package path is needed to add in the
environment variables. If the CAVASS software is installed on the *"~/cavass-build"* path, you don't need to set the
environment variable. Otherwise, you need to assign your CAVASS installation path before invoking any other methods in "
cavass.ops".

```
import cavass.ops

cavass.ops.CAVASS_PROFILE_PATH = 'your CAVASS path'
```

### IO

#### Read CAVASS file

```
from cavass.ops import read_cavass_file

input_file = 'N019PETCT.IM0'
image = read_cavass_file(input_file, first_slice=None, last_slice=None)
Output: np.ndarray[512, 512, 284]
```

Typically, you only need to pass the "*input file*" to the function for reading the IM0 image or BIM segmentation. If
you assign the first_slice/last_slice value(s), then only slices in this range would be returned.

#### Save CAVASS file

```
from cavass.ops import save_cavass_file

data: np.ndarray uint16 for image, bool for segmentation

save_cavass_file(output_file, data, binary=False, size=None, spacing=None, copy_pose_file=None)
```

Save data to *output_file*. If data is an image, set *binary* to False. If data is a segmentation, set *binary* to True.
Parameter *size* is the size of input data. The default is None, which means using the size of input data. You can
directly ignore this parameter in most situations. Parameter *spacing* is used to set the voxel spacing of the input
data. And if *copy_pose_file* exist, copy pose from reference file to the new output file. The most common scenario of
using this function is to save a segmentation of a given medical image.

```
from cavass.ops import save_cavass_file

image_file = 'CT.IM0'
output_file = 'CT_segmentation.BIM'
segmentation: np.ndarray bool
save_cavass_file(output_file, segmentation, binary=True, reference_file=image_file)
```

Above code saves segmentation to output file CT_segmentation.BIM. And copy properties of image CT.IM0 to the new BIM
file.

#### Copy pose

```
from cavass.ops import copy_pose

copy_pose(input_file1, input_file2, output_file)
```

Copy properties (voxel spacing, orientation, etc.) of *<u>input_file2</u>* to *input_file1*, and output the new file
*output_file*.

#### Export

```
from cavass.ops import export_math

export_math(input_file, output_file, output_file_type='matlab', first_slice=-1, last_slice=-1)
```

Export *input_file* to *output_file* with the format of *output_file_type*. The supported output formats include *
*mathematica**, **mathlab**, **r**, and **vtk**. The parameters of  *first_slice* and the *last_slice* indicate the
first and last slice index for export. If set to -1, the *first_slice* is set to 0, and the *last_slice* is set to the
max slice index of the input image.

### Convert image format

#### Dicom to CAVASS

```
from cavass.converters import dicom2cavass

dicom2cavass(input_dir, output_file, offset_value=0)
```

Convert dicom image to CAVASS format. *input_dir* is the directory that contains dicom files. CAVASS IM0 format uses
uint16 as the data type. However, Hounsfield units have negative values. So *offset_value* is used to transfer HU to
non-negative range, 1024 is commonly used for HU.

#### NIfTI to CAVASS

```
from cavass.converters import nifti2cavass

nifti2cavass(input_file, output_file, modality, offset_value=0, copy_pose_file)
```

Convert input NIfTI image to CAVASS format. CAVASS IM0 format uses uint16 as the data type. However, Hounsfield units
have negative values. So *offset_value* is used to transfer HU to the non-negative range, 1024 is commonly used for HU.
Copy pose from the copy pose file to the output file if the copy pose file exists.

#### NIfTI segmentation file to CAVASS BIM file

```
from cavass.converters import nifti_label2cavass

nifti_label2cavass(input_file, output_file, objects, modality, discard_background=True, copy_pose_file)
```

Convert NIfTI format segmentation file to CAVASS BIM files. Since a NIfTI format segmentation file could contain
arbitrary kinds of categories, and a CAVASS BIM file only contains one type of object, one NIfTI segmentation file may
convert to multiple CAVASS BIM files. The final output file is {output_file}_{objects[i]}.BIM. *objects* can be an
array, which contains the oject labels in the input NIfTI segmentation file that are desired to be converted, or a
string split by commas. Copy pose from the copy pose file to the output file if the copy pose file exists.

#### CAVASS to NIFTI

```
from cavass.converters import cavass2nifti

cavass2nifti(input_file, output_file, orientation='ARI')
```

Convert CAVASS format file to NIfTI format file. Parameter of *orientation* assigns the image orientation for the output
NIfTI file. Supported options include ARI and LPI for now.

### Get Image resolution

```
from cavass.ops import get_image_resolution

input_file = 'N019PETCT.IM0'
r = get_image_resolution(input_file)
Output: (512, 512, 284)
```

### Get voxel spacing

```
from cavass.ops import get_voxel_spacing

input_file = 'N019PETCT.IM0'
r = get_voxel_spacing(input_file)
Output: (0.976562, 0.976562, 3.0)
```

### Binary operations

```
from cavass.ops import bin_ops

# op: `or` | `nor` | `xor` | `xnor` | `and` | `nand` | `a-b`
bin_ops(input_file_1, input_file_2, output_file, op)
```

Perform binary operations between two input files *input_file_1* and *input_file_2*. The supported operations include *
*or**, **nor**, **xor**, **xnor**, **and**, **nand**, and **a-b**.

### Median filter

```
from cavass.ops import median2d

median2d(input_file, output_file, mode=0)
```

Perform 2D median filter to *input_file* and output *output_file*. Set *mode=0* for foreground filtering, *mode=1* for
background.

### Render surface

```
from cavass.ops import render_surface

render_surface(input_bim_file, output_file)
```

Render the surface of the input BIM file.

Note that the rendering script may fail when saving output file in extension disks/partitions. I don't know the exact
reason for this problem. But it seems related to the **track_all** script. Script "track_all {input_IM0_file}
{output_file} 1.000000 115.000000 254.000000 26 0 0" can't save output file to disks/partitions except the system
disk/partition.

### ndvoi

CAVASS `ndvoi input output mode [offx offy new_width new_height min max [min3 max3] [min4 max4] | [z]margin]`

```
from cavass.ops import ndvoi

ndvoi(untrimmed_file, output_file, min_slice_dim_3=inferior_slice_idx, max_slice_dim_3=superior_slice_idx)
```

### matched reslice

```
from cavass.ops import matched_reslice

matched_reslice(file_to_reslice, file_to_match, output_file, interpolation_method=interpolation_method):
```

### Windowing

```
from cavass.contrast_enhancement import cavass_soft_tissue_windowing,cavass_bone_windowing, cavass_pet_windowing

input_image: np.ndarray

output = cavass_soft_tissue_windowing(input_image)
output: np.ndarray uint8

output = cavass_bone_windowing(input_image)
output: np.ndarray uint8

output = cavass_pet_windowing(input_image)
output: np.ndarray uint8
```

The windowing methods are used to enhance the image contrast.

cavass_soft_tissue_windowing uses a center of 1000, and a window width of 500.

cavass_bone_windowing uses a center of 2000, and a window width of 4000.

cavass_pet_windowing uses a center of 1200, a window width of 3500, and the invert transform.

### Match file

```
from cavass.match import match

match(unmatched_file, file_to_match, output_file)
```

### Combine trimmed files

```
from cavass.integration import integrate_trimmed_images

# output_file_1 is the image trimmed from the reference file according to the ROI obtained from the trimmed files.
# output_file_2 is the integrated image of trimmed images.
integrate_trimmed_images(trimmed_files, reference_file, output_file_1, output_file_2)

```

