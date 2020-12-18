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
    e = 0 #stiffness of the support
    cal1 = 52.5
    cal2 = 35.2
    cal3 = 55.4
    cal4 = 49.5
    
    return [distances[0]-cal1,distances[1]-cal2,distances[2]-cal3,distances[3]-cal4]
    

def getTFminiData(rx,num=1):

    pi.set_mode(rx, pigpio.INPUT)

    pi.bb_serial_read_open(rx, 115200)
    loop = 0
    dists = []
    while loop<50:
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
    median =np.median(dists)
    for i in dists:
        if np.abs(i-median)>1:
            dists.remove(i)      
    median = np.median(dists)
    return np.mean(dists)

if __name__ == '__main__':
    try:
        i = 1
        for rx in rxs:
            pi = pigpio.pi()
            distances[i-1]=getTFminiData(rx,i)
            i+=1
        distances = calibration(distances)
            
        print(distances)

    except:
        pi.bb_serial_read_close(rx)
        pi.stop()
