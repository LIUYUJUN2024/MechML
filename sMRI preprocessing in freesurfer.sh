#!/bin/bash

# 设置FreeSurfer环境变量
export FREESURFER_HOME=/mnt/other/username/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/mnt/other/username/ADNI/volume

top_dir="/mnt/other/username/ADNI/data"
recon_dir="/mnt/other/username/ADNI/recon"
volume_dir="/mnt/other/username/ADNI/volume"

# 获取文件夹列表
readarray -t folders < <(find "$top_dir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
total=${#folders[@]}

# 定义处理分段的函数
process_segment() {
  local start=$1
  local end=$2
  for (( i=start; i<end; i++ )); do
    if [ $i -lt $total ]; then
      current_folder_path="$top_dir/${folders[i]}"
      
      # 处理当前文件夹下的所有子文件夹
      for subfolder in "$current_folder_path"/*; do
        if [ -d "$subfolder" ]; then
          echo "$subfolder"
          
          mkdir -p "$recon_dir/${folders[i]}"
          export SUBJECTS_DIR="$recon_dir/${folders[i]}"

          subfolder_name=$(basename "$subfolder")
          recon-all -s $subfolder_name -i $subfolder/*.nii -all -qcache -parallel
          
          # 开始处理 recon 文件夹
          for subsubdir in "$recon_dir/${folders[i]}"/*; do
            if [ -d "$subsubdir" ]; then
              if echo "$subsubdir" | grep -q "fsaverage"; then  
                echo "Skipping $subsubdir because it contains 'fsaverage'."
                continue
              fi

              source_nii="$subsubdir/mri/aparc.a2009s+aseg.mgz"
              if [ ! -f "$source_nii" ]; then
                echo "Skipping $subsubdir because $source_nii does not exist."
                continue
              fi

              stl_dir="${subsubdir/recon/stl\/aparc.a2009s+aseg}"
              if [ ! -d "$stl_dir" ]; then
                mkdir -p "$stl_dir"
              fi

              target_nii="$stl_dir/aparc.a2009s+aseg.nii.gz"
              if [ ! -f "$target_nii" ]; then
                if mri_convert "$source_nii" "$target_nii"; then
                  echo "$target_nii created successfully."
                else
                  echo "Error converting $source_nii to $target_nii"
                fi
              else
                echo "$target_nii already exists."
              fi

              # 提取体积信息
              volume_stldir="${subsubdir/recon/volume}"
              target_volume_file="$volume_stldir/aseg_stats.txt"
              if [ ! -f "$target_volume_file" ]; then
                if [ ! -d "$volume_stldir" ]; then
                  mkdir -p "$volume_stldir"
                fi
                if asegstats2table --subjects "$subsubdir" --meas volume --tablefile "$target_volume_file"; then
                  echo "$target_volume_file extracted successfully."
                else
                  echo "failure extracting $subsubdir to $target_volume_file"
                fi
              else
                echo "$target_volume_file already exists."
              fi
            fi
          done
        fi
      done
    fi
  done
}

# 定义分段大小并启动处理
segment_size=$((total / 10))
(
  process_segment $((0*segment_size)) $((1*segment_size)) &
  process_segment $((2*segment_size)) $((3*segment_size)) &
  process_segment $((4*segment_size)) $((5*segment_size)) &
  process_segment $((6*segment_size)) $((7*segment_size)) &
  process_segment $((8*segment_size)) $((9*segment_size)) &
  process_segment $((1*segment_size)) $((2*segment_size)) &
  process_segment $((3*segment_size)) $((4*segment_size)) &
  process_segment $((5*segment_size)) $((6*segment_size)) &
  process_segment $((7*segment_size)) $((8*segment_size)) &
  process_segment $((9*segment_size)) $((10*segment_size)) &
)
wait
