#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please supply the settings_file as an argument"
    exit 0
fi

settings_file="$1"

python code/shapifyattributes.py $settings_file
python code/dotfile.py $settings_file
python code/dotmap.py $settings_file
python code/generatetileindex.py $settings_file
python code/makeclient.py $settings_file

echo "Done!"
