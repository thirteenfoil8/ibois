# Need to setup a static ip address on raspberry pi:
# ifconfig to look at the ip of raspberry
# sudo route -n to get gateway
# sudo nano /etc/dhcpcd.conf
# add these lines :
# interface wlan0
# static ip_address= ip of raspberry or another
# static routers = gateway
# static domain_name_server=8.8.8.8 8.8.4.4
# save and reboot
# pip install paramiko


import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('Mdca632a33460.dyn.epfl.ch', username='pi', password='ibois')
file = open("../output/camera_data.txt","a")
def execute_vision(client):
    stdin, stdout, stderr = client.exec_command('cd ibois/LaserVision/vision/ && python3 vision.py')
    Dx = stdout[0]
    Dy = stdout[1]
    rot = stdout[2].strip('\n')[1:-2]
    file.write('translation_vector: {Dx:.2f} {Dy:.2f}\n'.format(Dx=Dx,Dy=Dy))
    file.write('rotation_angle: {rot:.2f} \n'.format(rot=rot))
    file.write('marker_id: 7')
file.truncate(0)

execute_vision(client)
file.close()
client.close()
