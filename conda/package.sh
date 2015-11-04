#!/bin/bash
CHANNEL=nckz
OUTPUT=`CONDA_PY=35 conda build ./ --output`
CONDA_PY=35 conda build ./
anaconda upload -u $CHANNEL $OUTPUT --force
