#!/bin/bash
# Render surface for all segmentations in the given input directory.
# Note that the rendering script may be failed when saving surface file in extension disks.
# This may be caused by permission limitations and may be solved by outputting the surface file in a different disk.
# Argument1: directory of segmentations
# Argument2: output directory of surface
# Author: Dai Jian

if [ "$#" -ne 2 ]; then
  echo "Two arguments should be provided, data input_directory and output directory, received $#."
  exit 1
fi

input_dir="$1"
output_dir="$2"

if [[ $output_dir == *"/" ]]; then
  output_dir="${output_dir:0:(${#output_dir} - 1)}"
fi

output_dir=$(realpath "$output_dir")
if [ ! -e "$output_dir" ]; then
  mkdir -p "${output_dir}"
fi

for segmentation in "$input_dir"/*; do
  if [ -f "$segmentation" ]; then
    if [[ $segmentation == *".BIM" ]]; then
      segmentation_file_name="${segmentation##*/}"
      output_file="${output_dir}/${segmentation_file_name:0:(${#segmentation_file_name} - 4)}_surface.BS0"
      render_surface_script=$(realpath "./render_surface.sh")
      bash ${render_surface_script} ${segmentation} ${output_file}
    fi
  fi
done
