#!/bin/bash
# Render surface for segmentation.
# Note that the rendering script may be failed when saving surface file in extension disks.
# This may be caused by permission limitations and may be solved by outputting the surface file in a different disk.
# Argument1: segmentation file
# Argument2: output surface file
# Author: Dai Jian

if [ "$#" -lt 2 ]; then
  echo "The number of input arguments at least should be two, input_bim_file and output_surface_file. Received $#."
  exit 1
fi

input_bim_file="$1"
output_surface_file="$2"

if [[ $output_surface_file == */* ]]; then
    output_dir="${output_surface_file%/*}"
else
    output_dir="."
fi

output_dir=$(realpath "$output_dir")
if [ ! -e "$output_dir" ]; then
  mkdir -p "${output_dir}"
fi

tmp_interpretation_file="${output_dir}/$(uuidgen).BIM"
tmp_gaussian_file="${output_dir}/$(uuidgen).IM0"

ndinterpolate ${input_bim_file} ${tmp_interpretation_file} 0 `get_slicenumber ${input_bim_file} -s | head -c 9` `get_slicenumber ${input_bim_file} -s | head -c 9` `get_slicenumber ${input_bim_file} -s | head -c 9` 1 1 1 1 `get_slicenumber ${input_bim_file}`
gaussian3d ${tmp_interpretation_file} ${tmp_gaussian_file} 0 1.500000
track_all ${tmp_gaussian_file} ${output_surface_file} 1.000000 115.000000 254.000000 26 0 0
rm ${tmp_interpretation_file}
rm ${tmp_gaussian_file}
