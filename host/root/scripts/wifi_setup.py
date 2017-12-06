import os
import imp
import sys
import time
import threading

# usb or sd card
user_dir = sys.argv[1] 

# imports
current_dir = os.path.dirname(os.path.abspath(__file__))
og = imp.load_source('og', current_dir + '/og.py')
wifi = imp.load_source('wifi_control', current_dir + '/wifi_control.py')

wifi.log_file = user_dir + "/wifi_log.txt"

# UI elements
menu = og.Menu()
banner = og.Alert()

# lock for updating menu
menu_lock = threading.Lock()

def quit():
    og.end_app()

# stores possible networks
# used to build wifi menu
# contains connect callback
class WifiNet :
    ssid = ''
    pw = ''
    def connect (self):
        wifi.connect(self.ssid, self.pw)
        update_menu()
        og.redraw_flag = True

def disconnect():
    wifi.disconnect_all()
    update_menu()
    og.redraw_flag = True

def start_web():
    wifi.start_web_server()
    update_menu()
    og.redraw_flag = True

def stop_web():
    wifi.stop_web_server()
    update_menu()
    og.redraw_flag = True

# update menu based on connection status
def update_menu():
    dots = ['.','..','...','....']
    menu_lock.acquire()
    try :
        # update wifi network labels
        if (wifi.state == wifi.CONNECTING) : 
            menu.header = 'Connecting'+dots[wifi.connecting_timer % 4]
            update_net_status_label('.')
        elif (wifi.state == wifi.CONNECTED) : 
            menu.header = 'Connected ' + wifi.current_net
            update_net_status_label('*')
        elif (wifi.state == wifi.DISCONNECTING) : 
            menu.header = 'Disconnecting..'
            update_net_status_label('-')
        elif (wifi.state == wifi.CONNECTION_ERROR) : 
            menu.header = 'Problem Connecting'
            update_net_status_label('-')
        else : 
            menu.header = 'Not Connected'
            update_net_status_label('-')
        
        # update webserver menu entry
        if (wifi.web_server_state == wifi.WEB_SERVER_RUNNING) :
            update_web_server_menu_entry(True)
        else :
            update_web_server_menu_entry(False)
    
    finally :
        menu_lock.release()

# show connected status for each network
def update_net_status_label(stat):
    # check entries that have stashed net info (I know)
    for i in range(len(menu.items)) :
        try :
            if (menu.items[i][2]['type'] == 'net') :
                if (menu.items[i][2]['ssid'] == wifi.current_net) :
                    menu.items[i][0] = ' '+stat+' ' + menu.items[i][2]['ssid']
                else :
                    menu.items[i][0] = ' - ' + menu.items[i][2]['ssid']
        except :
            pass

def update_web_server_menu_entry(stat):
    if (stat) :
        label = 'Stop Web Server'
        action = stop_web
    else :
        label = 'Start Web server'
        action = start_web
    for i in range(len(menu.items)) :
        try :
            if (menu.items[i][2]['type'] == 'web_server_control') :
                menu.items[i][0] = label
                menu.items[i][1] = action
        except :
            pass

# bg connection checker
def check_status():
    while True:
        time.sleep(1)
        wifi.update_state()
        update_menu()
        og.redraw_flag = True

def non():
    pass

def error_wifi_file() :
    og.clear_screen()
    og.println(0, "Error with wifi.txt")
    og.println(1, "Please check file")
    og.println(2, "is on your USB drive")
    og.println(3, "and in the correct")
    og.println(4, "format.")
    og.flip()
    og.enc_input()
    quit()

# build main menu
menu.items = []
menu.header='Not Connected'

# start it up
og.start_app()

try :
    f = open(user_dir + "/wifi.txt")
    try :
        networks = f.readlines()
        networks = [x.strip() for x in networks] 
        ssids = networks[0::2]
        pws = networks[1::2]
        for i in range(len(ssids)) :
            ssid = ssids[i]
            pw = pws[i]
            net = WifiNet()
            net.ssid = ssid
            net.pw = pw
            menu.items.append([' - ' + ssid, net.connect, {'type':'net', 'ssid':ssid}]) # stash some extra info with these net entries
    except : 
        print "bad wifi file" 
        raise
except :
    error_wifi_file()
    print "no wifi file"

menu.items.append(['Start Web Server', non, {'type':'web_server_control'}])
menu.items.append(['Disconnect', disconnect])
menu.items.append(['< Home', quit])
menu.selection = 1

# bg thread
menu_updater = threading.Thread(target=check_status)
menu_updater.daemon = True # stop the thread when we exit

wifi.initialize_state()
update_menu()
og.redraw_flag = True

# start thread to update connection status
menu_updater.start()

# enter menu
menu.perform()



