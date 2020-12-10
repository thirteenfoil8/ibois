# -*- coding: utf-8 -*
import os
os.system('sudo pigpiod')
import pigpio
import time
import numpy as np
RX = 23
RX2 = 24
RX3 = 27
RX4 = 22
rxs = [RX,RX2,RX3,RX4]
distances = [0,0,0,0]

def calibration(distances):
    e = 3
    cal1 = 13.5 - e
    cal2 = 20 -e
    cal3 = 6.25 -e
    cal4 = 4 -e
    
    return [distances[0]-cal1,distances[1]-cal2,distances[2]-cal3,distances[3]-cal4]
    

def getTFminiData(rx,num=1):

    pi.set_mode(rx, pigpio.INPUT)

    pi.bb_serial_read_open(rx, 115200)
    loop = 0
    dists = []
    while loop<100:
    #print("#############")
        time.sleep(0.1)    #change the value if needed
        (count, recv) = pi.bb_serial_read(rx)
        if count > 8 :
            for i in range(0, count-9):
                if (recv[i] == 89 and recv[i+1] == 89):
                    checksum = 0                    
                    for j in range(0, 8):
                        checksum = checksum + recv[i+j]
                        
                    checksum = checksum % 256
                    
                    if checksum == recv[i+8]:
                        distance = recv[i+2] + recv[i+3] * 256  
            
                    if checksum == recv[i+8] :
                        dists.append(distance)
                        loop += 1
    pi.bb_serial_read_close(rx)
    pi.stop()
    return np.mean(dists)

if __name__ == '__main__':
    try:
        i = 1
        print('try1')
        for rx in rxs:
            pi = pigpio.pi()
            distances[i-1]=getTFminiData(rx,i)
            i+=1
        distances = calibration(distances)
        print(distances)

    except:
        print('fail')
        pi.bb_serial_read_close(rx)
        pi.stop()
