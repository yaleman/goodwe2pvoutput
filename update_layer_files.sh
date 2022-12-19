#!/bin/bash
#update_layer_files.sh

if [ -f "/opt/homebrew/opt/asdf/libexec/asdf.sh" ]; then
	. /opt/homebrew/opt/asdf/libexec/asdf.sh
fi
if [ -f "$HOME/.asdf/asdf.sh" ]; then
 . $HOME/.asdf/asdf.sh
fi
mkdir -p layer_requirements/python
asdf shell python 3.9.16
python3 --version
python3 -m pip install --upgrade --target ./layer_requirements/python pvoutput pygoodwe
