from influxdb import InfluxDBClient
import numpy as np
import matplotlib as ml
import matplotlib.pyplot as plt
import itertools 
import math
import datetime
import subprocess
import sys
import operator

IP = '172.22.114.74'
pi = 3.1416
dt = 0.0005
v0=3000
Nz=300
Nx=300
dz=4
dx=4
pml=50
m= int(Nz+2*pml)
n= int(Nx+2*pml)
d=2000*np.ones((n,m))
ddx=np.loadtxt("ddx")
ddz=np.loadtxt("ddz")
K=np.loadtxt("K")
ddx1=1-0.5*dt*ddx[3:m-4,3:n-4]
ddx2=1+0.5*dt*ddx[3:m-4,3:n-4]
ddz1=1-0.5*dt*ddz[3:m-4,3:n-4]
ddz2=1+0.5*dt*ddz[3:m-4,3:n-4]
stack=np.zeros((Nz,Nx))
client = InfluxDBClient(IP, 8086, 'sili', 'sensorweb', 'microseismic')
#plt.ion()
#myobj = plt.imshow(np.zeros((Nz,Nx)))
aa=1
while aa:
    currentDT = datetime.datetime.now()
    DT=currentDT.strftime("%Y-%m-%dT%H:%M:%S.000000000Z")
    print(DT)
    value=[]
    for b in range(pml,pml+Nx,1):
        query = 'SELECT "value" FROM Amplitude WHERE "location" = \'R'+str(b)+'\' and time > \''+DT+'\'+297m and time < \''+DT+'\'+5h  ' 
        result = client.query(query)
        points = list(result.get_points())
        value =  np.append(value,np.array(list(map(operator.itemgetter('value'), points))))
    length = len(points)
    value=np.reshape(value, (300,-1))
#    aa=0
#times  =  map(operator.itemgetter('time'),  points)

    ttt=0
    p=np.zeros((n,m))
    em=np.zeros((n,m))
    px=np.zeros((n,m))
    pz=np.zeros((n,m))
    Vx=np.zeros((n,m))
    Vz=np.zeros((n,m))

    for ttt in range(length):
        p[pml:pml+Nx:1,pml]=value[0:300,length-ttt-1]


        Vz[3:m-4,3:n-4]=(ddz1*Vz[3:m-4,3:n-4]-dt*((p[4:m-3,3:n-4]-p[3:m-4,3:n-4])*1.171875-(p[5:m-2,3:n-4]-p[2:m-5,3:n-4])*0.065104166666667+(p[6:m-1,3:n-4]-p[1:m-6,3:n-4])*0.0046875)/d[3:m-4,3:n-4]/dz)/ddz2

        Vx[3:m-4,3:n-4]=(ddx1*Vx[3:m-4,3:n-4]-dt*((p[3:m-4,4:n-3]-p[3:m-4,3:n-4])*1.171875-(p[3:m-4,5:n-2]-p[3:m-4,2:n-5])*0.065104166666667+(p[3:m-4,6:n-1]-p[3:m-4,1:n-6])*0.0046875)/d[3:m-4,3:n-4]/dx)/ddx2

        pz[3:m-4,3:n-4]=(ddz1*pz[3:m-4,3:n-4]-K[3:m-4,3:n-4]*dt*((Vz[3:m-4,3:n-4]-Vz[2:m-5,3:n-4])*1.171875-(Vz[4:m-3,3:n-4]-Vz[1:m-6,3:n-4])*0.065104166666667+(Vz[5:m-2,3:n-4]-Vz[0:m-7,3:n-4])*0.0046875)/dz)/ddz2

        px[3:m-4,3:n-4]=(ddx1*px[3:m-4,3:n-4]-K[3:m-4,3:n-4]*dt*((Vx[3:m-4,3:n-4]-Vx[3:m-4,2:n-5])*1.171875-(Vx[3:m-4,4:n-3]-Vx[3:m-4,1:n-6])*0.065104166666667+(Vx[3:m-4,5:n-2]-Vx[3:m-4,0:n-7])*0.0046875)/dx)/ddx2

        p[3:m-4,3:n-4]=px[3:m-4,3:n-4]+pz[3:m-4,3:n-4]
        em=np.maximum(em, p)

    #stack=np.multiply(stack,np.transpose(em[pml:pml+Nx,pml:pml+Nx]))
    plt.imshow(np.transpose(em[pml:pml+Nx,pml:pml+Nx]))
    plt.show(block=False)
    aa=1
    plt.pause(0.1)
#plt.clf()



print (length)
