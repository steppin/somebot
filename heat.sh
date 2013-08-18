#!/bin/bash

# usage: heat.sh lold.splats temp.png
# temp.png is a preview image that the heatmap gets overlayed on

splats=$1
preview=$2
# you get the idea, but script should cd into `basename $0'...
./heat.py "$splats" "$preview"

# imagemagick composite
# should not hardcode classic.png in heat.py...
# should provide option as to where to output to...
composite classic.png "$preview" heatmap.png
