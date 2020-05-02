import os
from importlib.machinery import SourceFileLoader

fw_dir = os.getenv("FW_DIR")
wifi = SourceFileLoader('wifi_control', fw_dir + '/scripts/wifi_control.py').load_module()

wifi.initialize_state()
if wifi.wifi_connected() :
    os.system('oscsend localhost 4001 /wifiStatus i 1')
else :
    os.system('oscsend localhost 4001 /wifiStatus i 0')
