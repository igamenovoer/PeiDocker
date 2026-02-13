DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
  echo "Executing $DIR/_custom-on-user-login.sh"
fi
