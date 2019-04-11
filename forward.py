import numpy as np
import matplotlib as ml
import matplotlib.pyplot as plt
import itertools 
import math
import time
import subprocess
import sys
from thread import start_new_thread


def send_data(buf):
    try:
        http_post = "curl -i -XPOST \'http://172.22.114.74:8086/write?db=microseismic\' -u sili:sensorweb --data-binary \'"
        for b in buf:
            http_post += "\namplitude,type=PSVirPower value="
            http_post += str(b[1]) + " " + str(int(b[0]*1e9))
            #http_post += "\n"
        http_post += "\'"
        # print http_post
        subprocess.call(http_post, shell=True)
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print(e)


pi=3.1416
dt=0.0005
tt= np.arange(-0.04,0.04,dt)
fm=50
A=1
tt= np.multiply(tt*pi*fm,tt*pi*fm)
wave=np.zeros(1000)
wave[0:160]=np.multiply(A*(1-2*tt),np.exp(-tt))


v0=3000
Nz=300
Nx=300
dz=4
dx=4
pml=50
m= Nz+2*pml
n= Nx+2*pml
d=2000*np.ones((n,m))
ddx=np.loadtxt("ddx")
ddz=np.loadtxt("ddz")
K=np.loadtxt("K")
ddx1=1-0.5*dt*ddx[3:m-4,3:n-4]
ddx2=1+0.5*dt*ddx[3:m-4,3:n-4]
ddz1=1-0.5*dt*ddz[3:m-4,3:n-4]
ddz2=1+0.5*dt*ddz[3:m-4,3:n-4]
z0=150
x0=150

ttt=0


p=np.zeros((n,m))
px=np.zeros((n,m))
pz=np.zeros((n,m))
Vx=np.zeros((n,m))
Vz=np.zeros((n,m))
Seis=np.zeros((1000,Nx))
for ttt in range(1000):
  p[z0+pml-1,x0+pml-1]=p[z0+pml-1,x0+pml-1]+wave[ttt]


  Vz[3:m-4,3:n-4]=(ddz1*Vz[3:m-4,3:n-4]-dt*((p[4:m-3,3:n-4]-p[3:m-4,3:n-4])*1.171875-(p[5:m-2,3:n-4]-p[2:m-5,3:n-4])*0.065104166666667+(p[6:m-1,3:n-4]-p[1:m-6,3:n-4])*0.0046875)/d[3:m-4,3:n-4]/dz)/ddz2

  Vx[3:m-4,3:n-4]=(ddx1*Vx[3:m-4,3:n-4]-dt*((p[3:m-4,4:n-3]-p[3:m-4,3:n-4])*1.171875-(p[3:m-4,5:n-2]-p[3:m-4,2:n-5])*0.065104166666667+(p[3:m-4,6:n-1]-p[3:m-4,1:n-6])*0.0046875)/d[3:m-4,3:n-4]/dx)/ddx2

  pz[3:m-4,3:n-4]=(ddz1*pz[3:m-4,3:n-4]-K[3:m-4,3:n-4]*dt*((Vz[3:m-4,3:n-4]-Vz[2:m-5,3:n-4])*1.171875-(Vz[4:m-3,3:n-4]-Vz[1:m-6,3:n-4])*0.065104166666667+(Vz[5:m-2,3:n-4]-Vz[0:m-7,3:n-4])*0.0046875)/dz)/ddz2

  px[3:m-4,3:n-4]=(ddx1*px[3:m-4,3:n-4]-K[3:m-4,3:n-4]*dt*((Vx[3:m-4,3:n-4]-Vx[3:m-4,2:n-5])*1.171875-(Vx[3:m-4,4:n-3]-Vx[3:m-4,1:n-6])*0.065104166666667+(Vx[3:m-4,5:n-2]-Vx[3:m-4,0:n-7])*0.0046875)/dx)/ddx2



  p[3:m-4,3:n-4]=px[3:m-4,3:n-4]+pz[3:m-4,3:n-4]

  Seis[ttt,:]=p[pml+3,pml:pml+Nx]


plt.imshow(Seis)
plt.show()




#np.savetxt('text',px)
