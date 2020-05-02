#!/bin/bash

sleep 1

# poll wifi state after every dhcp event
export FW_DIR=${FW_DIR:="/home/music/fw_dir"}
python3 $FW_DIR/scripts/wifi_monitor.py
