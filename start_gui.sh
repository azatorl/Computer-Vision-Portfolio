#!/bin/bash

cd ~/teknofest_yolo/GUI
source ../venv/bin/activate

unset QT_QPA_PLATFORM_PLUGIN_PATH
unset QT_PLUGIN_PATH

python main.py

