#!/bin/bash
# this script sets up all environment variables, as well as configuration files
# based on the environment variables

# Normalize boolean-like variables to lowercase true/false; allow 1/0; keep empty as-is
normalize_bool() {
  # $1: variable name
  local __var_name="$1"
  # Indirect expansion to get value
  local __val="${!__var_name}"
  # Empty means: leave empty (use Dockerfile/system default)
  if [ -z "${__val+x}" ] || [ -z "${__val}" ]; then
    return 0
  fi
  case "${__val}" in
    1|true|TRUE|True) __val="true" ;;
    0|false|FALSE|False) __val="false" ;;
    *) __val="$(printf '%s' "$__val" | tr '[:upper:]' '[:lower:]')" ;;
  esac
  # export back
  eval "export ${__var_name}='${__val}'"
}

# Known boolean vars in stage-2
for __b in WITH_ESSENTIAL_APPS WITH_CUSTOM_APPS \
          ENABLE_GLOBAL_PROXY REMOVE_GLOBAL_PROXY_AFTER_BUILD \
          PEI_BAKE_ENV_STAGE_2; do
  normalize_bool "$__b"
done

# if ENABLE_GLOBAL_PROXY is true, set up proxy for all users
if [ "$ENABLE_GLOBAL_PROXY" = "true" ]; then
  # if PEI_HTTP_PROXY_2 is not set, or PEI_HTTPS_PROXY_2 is not set
  # skip
  if [ -z "$PEI_HTTP_PROXY_2" ] || [ -z "$PEI_HTTPS_PROXY_2" ]; then
    echo "PEI_HTTP_PROXY_2 and PEI_HTTPS_PROXY_2 must be set if ENABLE_PROXY_IN_BUILD is true"
    echo "Skipping proxy setup for build"
  else
    echo "Setting up proxy for build, write to /etc/environment"
    echo "http_proxy=$PEI_HTTP_PROXY_2" >> /etc/environment
    echo "https_proxy=$PEI_HTTPS_PROXY_2" >> /etc/environment
    echo "HTTP_PROXY=$PEI_HTTP_PROXY_2" >> /etc/environment
    echo "HTTPS_PROXY=$PEI_HTTPS_PROXY_2" >> /etc/environment
  fi
fi


# if PEI_BAKE_ENV_STAGE_2 is true, bake the environment variables to /etc/environment
if [ "$PEI_BAKE_ENV_STAGE_2" = "true" ]; then
  echo "Baking environment variables to /etc/environment"

  # get directory of this script
  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

  # if DIR/../generated/_etc_environment.sh exists, append it to /etc/environment
  echo "Checking $DIR/../generated/_etc_environment.sh"
  if [ -f "$DIR/../generated/_etc_environment.sh" ]; then
    echo "Appending $DIR/../generated/_etc_environment.sh to /etc/environment"

    # add a new line first
    echo "" >> /etc/environment

    # append the file
    cat $DIR/../generated/_etc_environment.sh >> /etc/environment
  else
    echo "$DIR/../generated/_etc_environment.sh not found"
  fi
fi
