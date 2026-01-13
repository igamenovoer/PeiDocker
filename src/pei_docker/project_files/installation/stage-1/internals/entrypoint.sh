#!/bin/bash

script_dir=$PEI_STAGE_DIR_1/internals

# run on-entry tasks
bash "$script_dir/on-entry.sh"

# first_run_signature_file=$PEI_DOCKER_DIR/stage-1-init-done

# # if first run signature file exists, skip the first run tasks
# # otherwise, run the first run tasks
# if [ -f $first_run_signature_file ]; then
#     echo "$first_run_signature_file found, skipping first run tasks"
# else
#     echo "$first_run_signature_file not found, running first run tasks ..."
#     bash $script_dir/on-first-run.sh
#     echo "Writing $first_run_signature_file"
#     echo "stage-1 is initialized" > $first_run_signature_file
# fi

# # execute on-every-run tasks
# bash $script_dir/on-every-run.sh

# check if ssh is installed, if yes, start the service
if [ -f /etc/ssh/sshd_config ]; then
    echo "Starting ssh service..."
    service ssh start
fi

# check if custom entry point is provided
custom_entry_file="$PEI_STAGE_DIR_1/internals/custom-entry-path"
custom_entry_args_file="$PEI_STAGE_DIR_1/internals/custom-entry-args"

if [ -f "$custom_entry_file" ] && [ -s "$custom_entry_file" ]; then

    raw_path=$(cat "$custom_entry_file")

    custom_entry_script="${raw_path/\$PEI_STAGE_DIR_1/$PEI_STAGE_DIR_1}"

    

    if [ -f "$custom_entry_script" ]; then

        echo "Executing custom entry point: $custom_entry_script"

        

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

        if [ $# -gt 0 ]; then

            echo "Executing command: $@"

            exec "$@"

        else

            echo "Starting default shell..."

            export SHELL=/bin/bash

            /bin/bash

        fi

    fi

else

    # start default shell or exec command

    if [ $# -gt 0 ]; then

        echo "Executing command: $@"

        exec "$@"

    else

        echo "Shell started."

        export SHELL=/bin/bash

        /bin/bash

    fi

fi
