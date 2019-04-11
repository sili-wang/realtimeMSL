from ina219 import INA219, DeviceRangeError
import time
import subprocess
import sys
from thread import start_new_thread
 
SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 2.0
ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
ina.configure(ina.RANGE_16V)


def collect_data(buf,ina,buf_index):
    power = ina.power()
    buf[buf_index] = [time.time(),power]
    buf_index += 1
    return [buf,buf_index]

def send_data(buf):
    try:
        http_post = "curl -i -XPOST \'http://172.22.114.74:8086/write?db=em_collectd\' -u aditya:123 --data-binary \'"
        for b in buf:
            http_post += "\nPSVirPower,type=PSVirPower value="
            http_post += str(b[1]) + " " + str(int(b[0]*1e9))
            #http_post += "\n"
        http_post += "\'"
        # print http_post
        subprocess.call(http_post, shell=True)
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print(e)



buf1 = [[0,0]]*1000
buf0 = [[0,0]]*1000
buf0_index = 0
buf1_index = 0
flag = 0
starttime = time.time()

while True:
    if flag == 1:
        [buf1,buf1_index] = collect_data(buf1,ina,buf1_index)
        if buf1_index == 1000:
            try:
                start_new_thread( send_data, (buf1,) )
                buf1_index = 0
            except:
                print "Error: unable to start thread"
            flag = 0
    else:
        [buf0,buf0_index] = collect_data(buf0,ina,buf0_index)
        if buf0_index == 1000:
            try:
                start_new_thread( send_data, (buf0,) )
                buf0_index = 0
            except:
                print "Error: unable to start thread"
            flag = 1
    time.sleep(0.01 - ((time.time() - starttime) % 0.01))

