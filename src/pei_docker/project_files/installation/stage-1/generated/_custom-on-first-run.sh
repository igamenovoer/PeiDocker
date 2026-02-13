DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
  echo "Executing $DIR/_custom-on-first-run.sh"
fi
bash $DIR/../custom/stage-1/custom/my-on-first-run-1.sh
bash $DIR/../custom/stage-1/custom/my-on-first-run-2.sh
