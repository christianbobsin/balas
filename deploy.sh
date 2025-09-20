#!/bin/bash
PROJECT_NAME=tflite-test
MCUX_WORKSPACE_LOC=/home/bruno/ufrgs/tcc/automator/cpp-project
MCUX_FLASH_DIR1=$MCUX_WORKSPACE_LOC/.mcuxpressoide_packages_support/MCXN947_support/Flash
LINKSERVER_BIN=/usr/local/LinkServer/binaries
MCUX_FLASH_DIR0=$LINKSERVER_BIN/Flash


$LINKSERVER_BIN/crt_emu_cm_redlink --flash-load-exec "$MCUX_WORKSPACE_LOC/$PROJECT_NAME/Debug/$PROJECT_NAME.axf" \
    -p MCXN947 --bootromstall 0x50000040 --probeserial IRFAZHJCVDLI1 -CoreIndex=0 \
        --flash-driver= -x $MCUX_WORKSPACE_LOC/$PROJECT_NAME/Debug --flash-dir $MCUX_FLASH_DIR0 \
            --flash-dir $MCUX_FLASH_DIR1 --flash-hashing --PreconnectScript LS_preconnect_MCXN9XX.scp