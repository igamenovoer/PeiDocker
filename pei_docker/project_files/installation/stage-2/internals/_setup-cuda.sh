#!/bin/bash

# configure cuda environment
echo "Setting up CUDA environment ..."
echo "Some packages requires CUDA_VISIBLE_DEVICES set properly"

# if CUDA_VISIBLE_DEVICES is not set, and nvidia-smi exists, find number of gpus and set CUDA_VISIBLE_DEVICES accordingly
if [ -z "$CUDA_VISIBLE_DEVICES" ] && command -v nvidia-smi &> /dev/null; then
    # get the number of gpus
    NUM_GPUS=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
    echo "Found $NUM_GPUS GPUs"

    # if no gpus, skip
    if [ "$NUM_GPUS" -eq 0 ]; then
        echo "No GPUs found, skipping cuda setup"
    else
        # set CUDA_VISIBLE_DEVICES to all gpus
        export CUDA_VISIBLE_DEVICES=$(seq -s, 0 $((NUM_GPUS-1)))
        echo "CUDA_VISIBLE_DEVICES set to $CUDA_VISIBLE_DEVICES"
    fi
fi

# # do we have CUDA_VISIBLE_DEVICES set? If so, skip
# if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
#     echo "CUDA_VISIBLE_DEVICES is already set to $CUDA_VISIBLE_DEVICES, skipping cuda setup"
#     exit
# fi

# # do we have nvidia-smi? If not, skip
# if ! command -v nvidia-smi &> /dev/null
# then
#     echo "nvidia-smi not found, skipping cuda setup"
#     exit
# fi

# # get the number of gpus
# NUM_GPUS=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
# echo "Found $NUM_GPUS GPUs"

# # if no gpus, skip
# if [ "$NUM_GPUS" -eq 0 ]; then
#     echo "No GPUs found, skipping cuda setup"
#     exit
# fi

# # set CUDA_VISIBLE_DEVICES to all gpus
# export CUDA_VISIBLE_DEVICES=$(seq -s, 0 $((NUM_GPUS-1)))
# echo "CUDA_VISIBLE_DEVICES set to $CUDA_VISIBLE_DEVICES"
