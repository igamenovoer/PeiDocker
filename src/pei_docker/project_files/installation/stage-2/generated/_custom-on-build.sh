DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
  echo "Executing $DIR/_custom-on-build.sh"
fi
bash $DIR/../custom/stage-2/custom/my-build-1.sh
bash $DIR/../custom/stage-2/custom/my-build-2.sh
