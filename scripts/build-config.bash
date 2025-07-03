#!/bin/bash

# PeiDocker Configuration Builder CLI Tool
# Build any PeiDocker configuration with flexible options
set -e

# Default values
NO_CACHE=false
STAGE="all"
RECREATE_PROJECT=true
CONFIG_FILE=""
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}===== $1 =====${NC}"
    echo ""
}

# Function to show usage
show_usage() {
    echo "PeiDocker Configuration Builder"
    echo ""
    echo "Usage: $0 [OPTIONS] <config_file>"
    echo ""
    echo "Arguments:"
    echo "  config_file              Path to the YAML configuration file"
    echo ""
    echo "Options:"
    echo "  --no-cache               Use --no-cache for docker compose build (default: false)"
    echo "  --stage=1|2|all          Build specific stage or all stages (default: all)"
    echo "  --recreate-project=true|false   Recreate project directory (default: true)"
    echo "  --verbose                Enable verbose output (default: false)"
    echo "  --help, -h               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 myconfig.yml                           # Build all stages with cache, recreate project"
    echo "  $0 --no-cache --stage=1 myconfig.yml     # Build only stage-1 without cache"
    echo "  $0 --stage=2 --recreate-project=false myconfig.yml  # Build stage-2 without recreating project"
    echo "  $0 --verbose tests/configs/ssh-test.yml  # Build with verbose output"
    echo ""
    echo "Build Directory:"
    echo "  Auto-generated from config filename: myconfig.yml → build-myconfig"
    echo ""
    echo "Stage Options:"
    echo "  --stage=1     Build only stage-1"
    echo "  --stage=2     Build only stage-2"
    echo "  --stage=all   Build stage-1 then stage-2 (default)"
}

# Function to validate stage option
validate_stage() {
    case "$1" in
        "1"|"2"|"all")
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to validate boolean option
validate_boolean() {
    case "$1" in
        "true"|"false")
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --stage=*)
                STAGE="${1#*=}"
                if ! validate_stage "$STAGE"; then
                    print_error "Invalid stage option: $STAGE. Must be 1, 2, or all"
                    exit 1
                fi
                shift
                ;;
            --recreate-project=*)
                RECREATE_PROJECT="${1#*=}"
                if ! validate_boolean "$RECREATE_PROJECT"; then
                    print_error "Invalid recreate-project option: $RECREATE_PROJECT. Must be true or false"
                    exit 1
                fi
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                print_error "Unknown option: $1"
                echo ""
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$CONFIG_FILE" ]; then
                    CONFIG_FILE="$1"
                else
                    print_error "Multiple config files specified: '$CONFIG_FILE' and '$1'"
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Function to validate inputs
validate_inputs() {
    # Check if config file is provided
    if [ -z "$CONFIG_FILE" ]; then
        print_error "No configuration file specified"
        echo ""
        show_usage
        exit 1
    fi
    
    # Check if config file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Check if config file is readable
    if [ ! -r "$CONFIG_FILE" ]; then
        print_error "Configuration file is not readable: $CONFIG_FILE"
        exit 1
    fi
    
    # Check if docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not available in PATH"
        exit 1
    fi
    
    # Check if docker compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
}

# Function to extract build directory name from config file
get_build_directory() {
    local config_path="$1"
    local config_basename=$(basename "$config_path")
    local config_name="${config_basename%.*}"  # Remove extension
    echo "build-${config_name}"
}

# Function to create and configure project
setup_project() {
    local build_dir="$1"
    local config_file="$2"
    
    # Change to project root
    cd /workspace/code/PeiDocker
    
    # Handle project recreation
    if [ "$RECREATE_PROJECT" = "true" ]; then
        if [ -d "$build_dir" ]; then
            print_info "Removing existing build directory: $build_dir"
            rm -rf "$build_dir"
        fi
        
        print_info "Creating new PeiDocker project: $build_dir"
        if [ "$VERBOSE" = "true" ]; then
            PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei create -p "$build_dir"
        else
            PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei create -p "$build_dir" > /dev/null
        fi
        
        print_info "Copying configuration file: $config_file"
        cp "$config_file" "$build_dir/user_config.yml"
        
        print_info "Configuring PeiDocker project"
        if [ "$VERBOSE" = "true" ]; then
            PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei configure -p "$build_dir"
        else
            PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei configure -p "$build_dir" > /dev/null
        fi
    else
        if [ ! -d "$build_dir" ]; then
            print_warning "Build directory does not exist, creating new project: $build_dir"
            RECREATE_PROJECT=true
            setup_project "$build_dir" "$config_file"
            return
        fi
        
        if [ ! -f "$build_dir/docker-compose.yml" ]; then
            print_warning "Docker compose file missing, reconfiguring project"
            cp "$config_file" "$build_dir/user_config.yml"
            if [ "$VERBOSE" = "true" ]; then
                PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei configure -p "$build_dir"
            else
                PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei configure -p "$build_dir" > /dev/null
            fi
        else
            print_info "Using existing project directory: $build_dir"
        fi
    fi
}

# Function to build Docker images
build_docker_images() {
    local build_dir="$1"
    local stage="$2"
    local no_cache="$3"
    
    # Change to build directory
    cd "$build_dir"
    
    # Prepare build arguments
    local build_args=""
    if [ "$no_cache" = "true" ]; then
        build_args="$build_args --no-cache"
    fi
    build_args="$build_args --progress=plain"
    
    # Build based on stage selection
    case "$stage" in
        "1")
            print_info "Building stage-1 Docker image"
            docker compose build $build_args stage-1
            ;;
        "2")
            print_info "Building stage-2 Docker image"
            docker compose build $build_args stage-2
            ;;
        "all")
            print_info "Building stage-1 Docker image"
            docker compose build $build_args stage-1
            print_info "Building stage-2 Docker image"
            docker compose build $build_args stage-2
            ;;
    esac
}

# Main function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    
    # Validate inputs
    validate_inputs
    
    # Get absolute path to config file
    CONFIG_FILE=$(realpath "$CONFIG_FILE")
    
    # Extract build directory name
    BUILD_DIR=$(get_build_directory "$CONFIG_FILE")
    
    # Show configuration
    print_header "PeiDocker Configuration Builder"
    print_info "Configuration file: $CONFIG_FILE"
    print_info "Build directory: $BUILD_DIR"
    print_info "Stage to build: $STAGE"
    print_info "Use cache: $([ "$NO_CACHE" = "true" ] && echo "No" || echo "Yes")"
    print_info "Recreate project: $RECREATE_PROJECT"
    print_info "Verbose output: $VERBOSE"
    
    # Setup project
    setup_project "$BUILD_DIR" "$CONFIG_FILE"
    
    # Build Docker images
    build_docker_images "$BUILD_DIR" "$STAGE" "$NO_CACHE"
    
    # Success message
    print_header "Build Completed Successfully"
    print_success "Docker images built successfully!"
    print_info "Build directory: $(realpath "$BUILD_DIR")"
    
    # Show next steps
    echo ""
    echo "Next steps:"
    echo "  cd $BUILD_DIR"
    case "$STAGE" in
        "1")
            echo "  docker compose up -d stage-1"
            ;;
        "2")
            echo "  docker compose up -d stage-2"
            ;;
        "all")
            echo "  docker compose up -d stage-2  # Run the final stage"
            ;;
    esac
    echo ""
}

# Run main function with all arguments
main "$@"