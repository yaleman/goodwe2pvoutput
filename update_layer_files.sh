#!/bin/bash
#update_layer_files.sh

TARGET_DIR="layer_requirements"
if [ -d "${TARGET_DIR}" ]; then
	echo "Removing existing layer_requirements directory..."
	rm -rf "${TARGET_DIR}"
fi

mkdir -p "${TARGET_DIR}"

MYTEMP=$(mktemp -d)


if [ ! -f ".python-version" ]; then
    echo "Error: .python-version file not found. Please create it with the desired Python version."
    exit 1
fi
PYTHON_VERSION="$(cat .python-version)"

uv export --frozen --no-dev --no-editable -o "$MYTEMP/requirements.txt"
uv pip install \
   --no-installer-metadata \
   --compile-bytecode \
   --python-platform x86_64-manylinux2014 \
   --python "${PYTHON_VERSION}" \
   --target "${TARGET_DIR}/python" \
   -r "$MYTEMP/requirements.txt"

uv pip install \
   --no-installer-metadata \
   --compile-bytecode \
   --python-platform aarch64-manylinux2014 \
   --python "${PYTHON_VERSION}" \
   --target "${TARGET_DIR}/python" \
   -r "$MYTEMP/requirements.txt"

rm -rf "${TARGET_DIR:?}/bin"

rm -rf "$MYTEMP"