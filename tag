#!/bin/bash

WORKING_DIR=/home/$USER/aokp/

find $WORKING_DIR -name .git -execdir git tag -a build-2 -m "Build-2" \;
