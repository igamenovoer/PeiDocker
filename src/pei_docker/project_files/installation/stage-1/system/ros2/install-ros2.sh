#!/bin/bash

# Usage: ./install-ros2.sh [--distro <ros_distro>] [--with-gui] [--with-nav2-full]
#
# This script installs ROS2 with selected packages.
#
# Options:
#   --distro <ros_distro>    Specify the ROS2 distribution to install (default: rolling)
#   --with-gui               Install GUI packages like rqt and rviz2
#   --with-nav2-full         Install full Nav2 packages instead of minimal
#
# Examples:
#   ./install-ros2.sh
#   ./install-ros2.sh --distro humble
#   ./install-ros2.sh --distro humble --with-gui --with-nav2-full
#
# Note: This script must be run with root privileges.

# Function to print usage
print_usage() {
    echo "Usage: ./install-ros2.sh [--distro <ros_distro>] [--with-gui] [--with-nav2-full]"
    echo "This script installs ROS2 with selected packages."
    echo "Options:"
    echo "  --distro <ros_distro>    Specify the ROS2 distribution to install (default: rolling)"
    echo "  --with-gui               Install GUI packages like rqt and rviz2"
    echo "  --with-nav2-full         Install full Nav2 packages instead of minimal"
    echo "Examples:"
    echo "  ./install-ros2.sh"
    echo "  ./install-ros2.sh --distro humble"
    echo "  ./install-ros2.sh --distro humble --with-gui --with-nav2-full"
    echo "Note: This script must be run with root privileges."
}

# Default ROS2 distro
default_ros2_distro="rolling"

# Display help if --help is used
if [ "$1" == "--help" ]; then
    print_usage
    exit 0
fi

# require sudo permission
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Parse command line arguments
ROS_DISTRO=""
WITH_GUI=false
WITH_NAV2_FULL=false

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --distro)
        ROS_DISTRO="$2"
        shift # past argument
        shift # past value
        ;;
        --with-gui)
        WITH_GUI=true
        shift # past argument
        ;;
        --with-nav2-full)
        WITH_NAV2_FULL=true
        shift # past argument
        ;;
        *)    # unknown option
        echo "Unknown option: $1"
        print_usage
        exit 1
        ;;
    esac
done

# Set default distro if not specified and warn user
if [ -z "$ROS_DISTRO" ]; then
    ROS_DISTRO="$default_ros2_distro"
    echo "WARNING: No --distro specified, defaulting to '$ROS_DISTRO'"
fi

echo "Installing ROS2 $ROS_DISTRO with selected packages"

export DEBIAN_FRONTEND=noninteractive
export TZ=Asia/Shanghai

apt update

# Base packages (always installed)
BASE_PACKAGES="ros-dev-tools ros-$ROS_DISTRO-ros-base ros-$ROS_DISTRO-rmw-cyclonedds-cpp ros-$ROS_DISTRO-cyclonedds"

# GUI packages (optional)
GUI_PACKAGES=""
if [ "$WITH_GUI" = true ]; then
    GUI_PACKAGES="ros-$ROS_DISTRO-rviz2 ros-$ROS_DISTRO-rqt"
    echo "Installing GUI packages: rviz2, rqt"
fi

# Nav2 packages
NAV2_PACKAGES="ros-$ROS_DISTRO-nav2-lifecycle-manager ros-$ROS_DISTRO-nav2-util"
if [ "$WITH_NAV2_FULL" = true ]; then
    NAV2_PACKAGES="$NAV2_PACKAGES ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-bringup ros-$ROS_DISTRO-nav2-minimal-tb*"
    echo "Installing full Nav2 packages"
else
    echo "Installing minimal Nav2 packages"
fi

# Install all packages
apt install -y --no-install-recommends $BASE_PACKAGES $GUI_PACKAGES $NAV2_PACKAGES
