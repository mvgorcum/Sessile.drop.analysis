# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 12:47:56 2016

@author: Mathijs van Gorcum
requires skimage, imageio, tkinter, and shapely
"""

import matplotlib.pyplot as plt
import numpy as np
import imageio
import os
from edge_detection import linear_subpixel_detection as edge
from skimage.viewer.canvastools import RectangleTool
from skimage.viewer.canvastools import LineTool
from skimage.viewer import ImageViewer
from skimage import io
from shapely.geometry import LineString
import tkinter as tk
from tkinter import filedialog

#some tunable variables, maybe make input?
k=70
PO=3
thresh=70

#userinput for file
root = tk.Tk()
root.withdraw()
filename = filedialog.askopenfilename()

filext=os.path.splitext(filename)[1]

#check the file type
if filename.lower().endswith('.avi') or filename.lower().endswith('.mp4'):
    filetype=0
    global vid
    vid = imageio.get_reader(filename,)
    nframes = vid.get_meta_data()['nframes']
elif filename.lower().endswith(('.tiff', '.tif')):
    tiffinfo=io.MultiImage(filename)
    if len(tiffinfo)>1:
        filetype=1
        nframes=len(tiffinfo)
    else:
        import glob
        filetype=2
        filename=glob.glob(os.path.split(filename)[0]+os.sep+'*'+filext)
        filename.sort()
        nframes=len(filename)
elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
    import glob
    filetype=2
    filename=glob.glob(os.path.split(filename)[0]+os.sep+'*'+filext)
    filename.sort()
    nframes=len(filename)
else:
    print('unknown filetype')


#function to read a specific frame from the movie, stack, or image sequence
def getcurrframe(filename,framenr,filetype):
    def movie():
        image=vid.get_data(framenr)[:,:,0]
        return image
    def tifstack():
        stack=io.imread(filename)
        image=stack[framenr,:,:]
        return image
    def images():
        image=io.imread(filename[framenr])
        return image
    filetypes={0 : movie,
           1 : tifstack,
           2 : images
           }
    image=filetypes[filetype]()
    return image


image = getcurrframe(filename,0,filetype)

#preallocate crop coordinates, maybe unescecarry?
coords=[0,0,0,0]

#show the image and ask for a crop from the user, using skimage.viewer canvastools
viewer = ImageViewer(image)
rect_tool = RectangleTool(viewer, on_enter=viewer.closeEvent) #actually call the imageviewer
viewer.show() #don't forget to show it
coords=np.array(rect_tool.extents)
coords=np.array(np.around(coords),dtype=int)

#crop the image
cropped=image[coords[2]:coords[3],coords[0]:coords[1]]
framesize=cropped.shape

baseinput=np.array([0,0,0,0])
#userinput for the baseline, on which we'll find the contact angles, using skimage.viewer
viewer = ImageViewer(cropped)
line_tool=LineTool(viewer,on_enter=viewer.closeEvent)
viewer.show()
baseinput=line_tool.end_points
#extend the baseline to the edge of the frame (in case the drop grows)
rightbasepoint=np.argmax([baseinput[0,0],baseinput[1,0]])
baseslope=np.float(baseinput[rightbasepoint,1]-baseinput[1-rightbasepoint,1])/(baseinput[rightbasepoint,0]-baseinput[1-rightbasepoint,0])
base=np.array([[0,baseinput[0,1]-baseslope*baseinput[0,0]],[framesize[1],baseslope*framesize[1]+baseinput[0,1]-baseslope*baseinput[0,0]]])

#preallocation of edges, angles and contact points
edgeleft=np.zeros(framesize[0])
edgeright=np.zeros(framesize[0])
thetal=np.zeros(nframes)
thetar=np.zeros(nframes)
contactpointright=np.zeros(nframes)
contactpointleft=np.zeros(nframes)
dropvolume=np.zeros(nframes)

#loop over frames
for framenr in range (0,nframes):
    image = getcurrframe(filename,framenr,filetype) #get current frame
    cropped=np.array(image[round(coords[2]):round(coords[3]),round(coords[0]):round(coords[1])]) #crop frame
    edgeleft, edgeright=edge(cropped,thresh) #find the edge with edge function in edge_detection.py
    baseline=LineString(base) #using shapely we construct baseline
    rightline=LineString(np.column_stack((edgeright,(range(framesize[0]))))) #and the lines of the edges
    leftline=LineString(np.column_stack((edgeleft,(range(framesize[0])))))
    leftcontact=baseline.intersection(leftline) #we find the intersectionpoint of the baseline with the edge
    rightcontact=baseline.intersection(rightline)
    #Detect small drops that are lower than 'k' pixels
    #This may break if the drop grows outside the frame on one side. Maybe fix later?
    fitpointsleft=edgeleft[range(np.int(np.floor(leftcontact.y)),np.int(np.floor(leftcontact.y)-k),-1)]
    if any(fitpointsleft==0):
        fitpointsleft=np.delete(fitpointsleft,range(np.argmax(fitpointsleft==0),k))
    #polyfit the edges around the baseline, but flipped, because polyfitting a vertical line is bad
    leftfit=np.polyfit(range(fitpointsleft.shape[0]),fitpointsleft,PO)
    leftvec=np.array([1,leftfit[PO-1]]) #vector for angle calculation
    fitpointsright=edgeright[range(np.int(np.floor(leftcontact.y)),np.int(np.floor(leftcontact.y)-k),-1)]
    if any(fitpointsright==0):
        fitpointsright=np.delete(fitpointsright,range(np.argmax(fitpointsright==0),k))
    #polyfit the edges around the baseline, but flipped, because polyfitting a vertical line is bad
    rightfit=np.polyfit(range(fitpointsright.shape[0]),fitpointsright,PO)
    rightvec=np.array([1,rightfit[PO-1]]) #vector for angle calculation
    basevec=np.array([-baseslope,1]) #base vector for angle calculation (allows for a sloped basline if the camera was tilted)

    #calculate the angles using the dot product.
    thetal[framenr]=np.arccos(np.dot(basevec,leftvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(leftvec,leftvec))))*180/np.pi
    thetar[framenr]=180-np.arccos(np.dot(basevec,rightvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(rightvec,rightvec))))*180/np.pi

    #save the contact point (the point where the polyfit intersects the baseline)
    contactpointright[framenr]=rightfit[PO]
    contactpointleft[framenr]=leftfit[PO]
    for height in range (0,min(np.int(np.floor(leftcontact.y)),np.int(np.floor(rightcontact.y)))):
        dropvolume[framenr]=dropvolume[framenr]+np.pi*np.square((edgeright[height]-edgeleft[height])/2) #volume of each slice in pixels^3, without taking a possible slanted baseline into account
    #using cylindrical slice we calculate the remaining volume
    slantedbasediff=max(np.floor(leftcontact.y),np.floor(rightcontact.y))-min(np.floor(leftcontact.y),np.floor(rightcontact.y))
    #we assume that the radius is constant over the range of the slanted baseline, for small angles this is probably accurate, but for larger angles this is probably wrong.
    baseradius=(edgeright[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))]-edgeleft[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))])/2
    dropvolume[framenr]=dropvolume[framenr]+.5*np.pi*np.square(baseradius)*slantedbasediff

#%%

#debug output, showing the image, baseline and the detected edge
plt.imshow(image[round(coords[2]):round(coords[3]),round(coords[0]):round(coords[1])],cmap='gray',interpolation="nearest")
plt.plot(edgeleft,range(framesize[0]))
plt.plot(edgeright,range(framesize[0]))
plt.plot([base[0,0],base[1,0]],[base[0,1],base[1,1]])
plt.show()
#%%

#calculate the speed of the contact line if there are enough frames
if nframes>100:
    fitsamplesize=40
    leftspeed=np.zeros(nframes)
    rightspeed=np.zeros(nframes)
    for framenr in range(fitsamplesize,nframes-fitsamplesize-1):
        rightposfit=np.polyfit(range(-fitsamplesize,fitsamplesize),contactpointright[range(framenr-fitsamplesize,framenr+fitsamplesize)],1)
        leftposfit=np.polyfit(range(-fitsamplesize,fitsamplesize),contactpointleft[range(framenr-fitsamplesize,framenr+fitsamplesize)],1)
        leftspeed[framenr]=leftposfit[0]
        rightspeed[framenr]=rightposfit[0]
    for fillinrest in range(fitsamplesize):
        leftspeed[fillinrest]=leftspeed[fitsamplesize]
        rightspeed[fillinrest]=rightspeed[fitsamplesize]
    for fillinrest in range(nframes-fitsamplesize-1,nframes-1):
        leftspeed[fillinrest]=leftspeed[nframes-fitsamplesize-1]
        rightspeed[fillinrest]=rightspeed[nframes-fitsamplesize-1]

    #plot the speed of the contact line
    fig = plt.figure()
    ax = plt.gca()
    ax.scatter(-leftspeed[range(fitsamplesize,nframes-fitsamplesize)],thetal[range(fitsamplesize,nframes-fitsamplesize)])
    ax.scatter(rightspeed[range(fitsamplesize,nframes-fitsamplesize)],thetar[range(fitsamplesize,nframes-fitsamplesize)])
    ax.set_xscale('log')
