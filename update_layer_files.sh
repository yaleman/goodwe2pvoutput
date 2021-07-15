#!/bin/bash
#update_layer_files.sh

mkdir -p layer_requirements/python
/opt/homebrew/opt/python@3.8/bin/python3 -m pip install --target ./layer_requirements/python pvoutput pygoodwe