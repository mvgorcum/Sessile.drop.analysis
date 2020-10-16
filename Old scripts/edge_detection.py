# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 16:20:35 2016

@author: M.van.Gorcum
"""
import numpy as np
import scipy as sp

def linear_subpixel_detection(image,thresh):
    framesize=image.shape
    edgeleft=np.zeros(framesize[0])
    edgeright=np.zeros(framesize[0])
    for y in range(framesize[0]-1): #edge detection, go line by line on horizontal
        edgeleft[y]=np.argmax(image[y,0:framesize[1]]<thresh) #edge detection on pixel scale
        if edgeleft[y]!=0:
            subpxcorr=(thresh-np.float_(image[y,np.int(edgeleft[y]-1)]))/(np.float_(image[y,np.int(edgeleft[y])])-np.float_(image[y,np.int(edgeleft[y]-1)])) #subpixel correction with using corr=(threshold-intensity(edge-1))/(intensity(edge)-intensity(edge-1))
            edgeleft[y]=edgeleft[y]+subpxcorr-1 #add the correction and shift 1 pixel left, to plot on the edge properly
        edgeright[y]=np.int(framesize[1]-np.argmax(image[y,range(framesize[1]-1,0,-1)]<thresh))
        #same scheme for right edge, except the edge detection is done flipped, since np.argmax gives the first instance of the maximum value
        if edgeright[y]!=framesize[1]:
            subpxcorr=(thresh-np.float_(image[y,np.int(edgeright[y]-1)]))/(np.float_(image[y,np.int(edgeright[y])])-np.float_(image[y,np.int(edgeright[y]-1)]))
            edgeright[y]=edgeright[y]+subpxcorr-1
    return edgeleft, edgeright;


def errorfunction_subpixel_detection(image,thresh):
    erffitsize=np.int(40)
    def errorfunction(x,xdata,y): #define errorfunction to fit with a least squares fit.
        return x[0]*(1+sp.special.erf(xdata*x[1]+x[2]))+x[3] - y;
    framesize=image.shape
    edgeleft=np.zeros(framesize[0])
    edgeright=np.zeros(framesize[0])
    for y in range(framesize[0]-1): #edge detection, go line by line on horizontal
        edgeleft[y]=np.argmax(image[y,0:framesize[1]]<thresh) #edge detection on pixel scale
        if (edgeleft[y]-erffitsize)>=0  and (edgeleft[y]-erffitsize)<=framesize[0]:
            fitparts=np.array(image[y,range(np.int(edgeleft[y])-erffitsize,np.int(edgeleft[y])+erffitsize)]) #take out part of the image around the edge to fit the error function
            guess=(max(fitparts)-min(fitparts))/2,-.22,0,min(fitparts) #initial guess for error function
            lstsqrsol=sp.optimize.least_squares(errorfunction,guess,args=(np.array(range(-erffitsize,erffitsize)),fitparts)) #least sqaures fit
            edgeleft[y]=edgeleft[y]-lstsqrsol.x[2]/lstsqrsol.x[1] #add the subpixel correction
        edgeright[y]=np.int(framesize[1]-np.argmax(image[y,range(framesize[1]-1,0,-1)]<thresh))#same scheme for right edge, except the edge detection is done flipped, since np.argmax gives the first instance of the maximum value
        if (edgeright[y]-erffitsize)>=0  and (edgeright[y]-erffitsize)<=framesize[0]:
            fitparts=np.array(image[y,range(np.int(edgeright[y])-erffitsize,np.int(edgeright[y])+erffitsize)])
            guess=(max(fitparts)-min(fitparts))/2,.22,0,min(fitparts)
            lstsqrsol=sp.optimize.least_squares(errorfunction,guess,args=(np.array(range(-erffitsize,erffitsize)),fitparts))
            edgeright[y]=edgeright[y]-lstsqrsol.x[2]/lstsqrsol.x[1]
        elif edgeright[y]==framesize[1]:
            edgeright[y]=0

    return edgeleft, edgeright;
