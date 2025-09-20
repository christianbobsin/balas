#!/bin/bash
PROJECT_NAME=tflite-test
MCUX_WORKSPACE_LOC=/home/bruno/ufrgs/tcc/automator/cpp-project
MCUXPRESSO=/usr/local/mcuxpressoide/ide/mcuxpressoide

# This part is only needed to run once. TODO: find a way to automate detecting if this was run and dont run again otherwise
#$MCUXPRESSO -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild -data $MCUX_WORKSPACE_LOC \
#	-import $MCUX_WORKSPACE_LOC/$PROJECT_NAME -build $PROJECT_NAME/Debug

$MCUXPRESSO -nosplash -application org.eclipse.cdt.managedbuilder.core.headlessbuild \
  -data $MCUX_WORKSPACE_LOC -build $PROJECT_NAME/Debug