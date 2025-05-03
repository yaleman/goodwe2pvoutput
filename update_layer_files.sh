#!/bin/bash
#update_layer_files.sh

if [ -d "layer_requirements" ]; then
	echo "Removing existing layer_requirements directory..."
	rm -rf layer_requirements
fi

TARGET_DIR="layer_requirements"

mkdir -p "${TARGET_DIR}"

PYTHON_VERSION="3.12"

uv export --frozen --no-dev --no-editable -o "$TMPDIR/requirements.txt"
uv pip install \
   --no-installer-metadata \
   --no-compile-bytecode \
   --python-platform x86_64-manylinux2014 \
   --python "${PYTHON_VERSION}" \
   --target "${TARGET_DIR}/python" \
   -r "$TMPDIR/requirements.txt"

uv pip install \
   --no-installer-metadata \
   --no-compile-bytecode \
   --python-platform aarch64-manylinux2014 \
   --python "${PYTHON_VERSION}" \
   --target "${TARGET_DIR}/python" \
   -r "$TMPDIR/requirements.txt"

rm -rf "${TARGET_DIR:?}/bin"
