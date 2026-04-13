#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${BALAS_CONFIG_FILE:-$SCRIPT_DIR/.balas.env}"
if [[ -f "$CONFIG_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
    set +a
fi

REPO_ROOT="${REPO_ROOT:-$SCRIPT_DIR}"
PROJECT_NAME="${PROJECT_NAME:-tflite-test}"
BUILD_CONFIG="${BUILD_CONFIG:-Debug}"
MCUX_WORKSPACE_DIR="${MCUX_WORKSPACE_DIR:-${MCUX_WORKSPACE_LOC:-$REPO_ROOT/cpp-project}}"
MCUXPRESSO_IDE_BIN="${MCUXPRESSO_IDE_BIN:-${MCUXPRESSO:-/usr/local/mcuxpressoide/ide/mcuxpressoide}}"
MCUX_IMPORT_PROJECT="${MCUX_IMPORT_PROJECT:-1}"

if [[ ! -x "$MCUXPRESSO_IDE_BIN" ]]; then
    echo "MCUXpresso IDE not found or not executable: $MCUXPRESSO_IDE_BIN" >&2
    echo "Set MCUXPRESSO_IDE_BIN in the environment or in .balas.env." >&2
    exit 1
fi

if [[ ! -d "$MCUX_WORKSPACE_DIR/$PROJECT_NAME" ]]; then
    echo "Project directory not found: $MCUX_WORKSPACE_DIR/$PROJECT_NAME" >&2
    echo "Set MCUX_WORKSPACE_DIR to the directory that contains $PROJECT_NAME." >&2
    exit 1
fi

if [[ "$MCUX_IMPORT_PROJECT" == "1" || "$MCUX_IMPORT_PROJECT" == "true" ]]; then
    "$MCUXPRESSO_IDE_BIN" -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild \
      -data "$MCUX_WORKSPACE_DIR" -import "$MCUX_WORKSPACE_DIR/$PROJECT_NAME"
fi

"$MCUXPRESSO_IDE_BIN" -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild \
  -data "$MCUX_WORKSPACE_DIR" -build "$PROJECT_NAME/$BUILD_CONFIG"
