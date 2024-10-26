import network
import time

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    if not wlan.isconnected():
        print("正在连接")
        wlan.connect("ssid","password") # 填入你自己的Wi-Fi和密码
        while not wlan.isconnected():
            print("正在尝试连接")
            time.sleep(1)
    print("network config:",wlan.ifconfig())
