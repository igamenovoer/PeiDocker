#!/bin/bash

# stage 2 entrypoint, part of the content is from stage 1 entrypoint

script_dir_1=$PEI_STAGE_DIR_1/internals
script_dir_2=$PEI_STAGE_DIR_2/internals

# run on-entry tasks for stage 1
bash $script_dir_1/on-entry.sh

# run on-entry tasks for stage 2
bash $script_dir_2/on-entry.sh

# # do first run tasks
# bash $script_dir_1/on-first-run.sh

# # create links
# bash $script_dir_2/create-links.sh

# # do first run tasks in stage 2
# bash $script_dir_2/on-first-run.sh

# check if ssh is installed, if yes, start the service
if [ -f /etc/ssh/sshd_config ]; then
    echo "Starting ssh service..."
    service ssh start
fi

# check if custom entry point is provided (stage-2 overrides stage-1)
custom_entry_file_2="$PEI_STAGE_DIR_2/internals/custom-entry-path"
custom_entry_args_file_2="$PEI_STAGE_DIR_2/internals/custom-entry-args"
custom_entry_file_1="$PEI_STAGE_DIR_1/internals/custom-entry-path"
custom_entry_args_file_1="$PEI_STAGE_DIR_1/internals/custom-entry-args"

if [ -f "$custom_entry_file_2" ] && [ -s "$custom_entry_file_2" ]; then
    # Stage-2 custom entry point exists, use it and ignore stage-1
    custom_entry_script=$(cat "$custom_entry_file_2")
    custom_entry_args_file="$custom_entry_args_file_2"
    stage_name="stage-2"
elif [ -f "$custom_entry_file_1" ] && [ -s "$custom_entry_file_1" ]; then
    # No stage-2 custom entry point, check stage-1
    custom_entry_script=$(cat "$custom_entry_file_1")
    custom_entry_args_file="$custom_entry_args_file_1"
    stage_name="stage-1"
else
    # No custom entry point found, start default shell
    echo "Shell started."
    export SHELL=/bin/bash
    /bin/bash
    exit 0
fi

# Execute the custom entry point with argument precedence logic
if [ -f "$custom_entry_script" ]; then
    echo "Executing $stage_name custom entry point: $custom_entry_script"
    
    # Determine which arguments to use
    if [ $# -gt 0 ]; then
        # Runtime arguments provided, use them
        echo "Using runtime arguments: $@"
        bash "$custom_entry_script" "$@"
    elif [ -f "$custom_entry_args_file" ]; then
        # No runtime arguments, use default arguments from config
        default_args=$(cat "$custom_entry_args_file")
        if [ -n "$default_args" ]; then
            echo "Using default arguments: $default_args"
            eval "bash \"$custom_entry_script\" $default_args"
        else
            echo "No arguments (runtime or default)"
            bash "$custom_entry_script"
        fi
    else
        # No arguments file, run without arguments
        echo "No arguments (no default args file)"
        bash "$custom_entry_script"
    fi
else
    echo "Warning: Custom entry point file not found: $custom_entry_script"
    echo "Starting default shell..."
    export SHELL=/bin/bash
    /bin/bash
fi