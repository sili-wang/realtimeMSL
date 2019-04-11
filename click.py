import numpy as np
import matplotlib as ml
import matplotlib.pyplot as plt
import itertools 
import math
import time
import subprocess
import sys
from _thread import start_new_thread
from threading import Event, Thread, Lock
lock = Lock()
event = Event()
SAMPLE_INTERVAL = 0.1
IP = '172.22.114.74'
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

z0=0
x0=0
ttt=0

def zero():  
    while 1:
        event.wait()
        data_time=str(int(time.time()*1e9))
        data_chunk = ""
        for b in range(pml,pml+Nx):
              data_value = str(0)
              location=str(b)
              data_chunk += "Amplitude,location=R%s value=%s %s\n" % (location, data_value, data_time)
        url = "http://%s:8086/write?db=microseismic" % (IP)
        http_post = "curl -i -XPOST \'%s\' -u sili:sensorweb --data-binary \'%s\'" % (url, data_chunk)
        subprocess.call(http_post, shell=True)
        time.sleep(SAMPLE_INTERVAL)

def forward(z0,x0):
    lock.acquire()
    event.clear()
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
        
        Seis[ttt,:]=p[pml+1,pml:pml+Nx]
        data_time=str(int(time.time()*1e9))
        data_chunk = ""
        for b in range(pml,pml+Nx):
              data_value = str(p[pml+3,b])
              location=str(b)
              data_chunk += "Amplitude,location=R%s value=%s %s\n" % (location, data_value, data_time)
        url = "http://%s:8086/write?db=microseismic" % (IP)
        http_post = "curl -i -XPOST \'%s\' -u sili:sensorweb --data-binary \'%s\'" % (url, data_chunk)
        subprocess.call(http_post, shell=True)
    event.set()
    lock.release()


try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk
def showxy(event):
    '''
    show x, y coordinates of mouse click position
    event.x, event.y relative to ulc of widget (here root) 
    '''
    # xy relative to ulc of root
    #xy = 'root x=%s  y=%s' % (event.x, event.y)
    # optional xy relative to blue rectangle
    xy = 'rectangle x=%s  y=%s' % (event.x-x1, event.y-y1)
    root.title(xy)
    rx = event.x-x1+45
    ry = event.y-y1+45
    cv.create_rectangle( 50, 50, 350, 350, fill="brown", tag='rectangle')
    cv.create_rectangle( rx, ry, rx+5, ry+5, fill="green", tag='rectangle')
    z0 = event.y-y1
    x0 = event.x-x1
    #start_new_thread( forward, (z0,x0) )
    threads.append(Thread(target=forward, args=(z0,x0)))
    threads[-1].start()






root = tk.Tk()
root.title("Mouse click within blue rectangle ...")
# create a canvas for drawing
w = 400
h = 400
cv = tk.Canvas(root, width=w, height=h, bg='white')
cv.pack()
# draw a blue rectangle shape with 
# upper left corner coordinates x1, y1
# lower right corner coordinates x2, y2
x1 = 50
y1 = 50
x2 = 350
y2 = 350
cv.create_rectangle(x1, y1, x2, y2, fill="brown", tag='rectangle')
# bind left mouse click within shape rectangle
#start_new_thread( zero, () )
threads = []
threads.append(Thread(target=zero, args=()))
event.set()
threads[-1].start()
cv.tag_bind('rectangle', '<Button-1>', showxy)
root.mainloop()
