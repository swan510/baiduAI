import network
import time
class WifiConnect():
    def __init__(self,ssid,password):
        self.ssid = ssid
        self.password = password
    def connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        wlan.active(True)
        if not wlan.isconnected():
            print("正在连接")
            wlan.connect(self.ssid,self.password)
            while not wlan.isconnected():
                print("正在尝试连接")
                time.sleep(1)
        print("network config:",wlan.ifconfig())
