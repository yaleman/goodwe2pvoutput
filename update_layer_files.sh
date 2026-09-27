#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="layer_requirements"
MYTEMP=$(mktemp -d)
trap 'rm -rf "$MYTEMP"' EXIT


if [ ! -f ".python-version" ]; then
    echo "Error: .python-version file not found. Please create it with the desired Python version."
    exit 1
fi
PYTHON_VERSION="$(tr -d '\n' < .python-version)"

uv export --frozen --no-dev --no-emit-project -o "$MYTEMP/requirements.txt" >/dev/null
for ARCH in x86_64 aarch64; do
    uv pip install \
       --no-installer-metadata \
       --only-binary :all: \
       --python-platform "${ARCH}-manylinux2014" \
       --python "${PYTHON_VERSION}" \
       --target "$MYTEMP/$ARCH/python" \
       -r "$MYTEMP/requirements.txt"
    rm -rf "$MYTEMP/$ARCH/bin"
done

python3 scripts/merge_layer_architectures.py "$MYTEMP/x86_64/python" "$MYTEMP/aarch64/python"

rm -rf "$TARGET_DIR"
mv "$MYTEMP/x86_64" "$TARGET_DIR"
