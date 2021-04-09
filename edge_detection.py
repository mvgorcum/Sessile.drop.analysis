"""
Created on Tue Dec 20 16:20:35 2016

@author: M.van.Gorcum
"""
import numpy as np
import scipy as sp

def subpixel_detection(image,thresh,mode):
    """
    edge detection, allowing for two subpixel detection methods
    """
    erffitsize=np.int(40)
    framesize=image.shape
    edgeleft=np.zeros(framesize[0])
    edgeright=np.zeros(framesize[0])
    for y in range(framesize[0]-1): #edge detection, go line by line on horizontal
        edgeleft[y]=np.argmax(image[y,0:framesize[1]]<thresh) #edge detection on pixel scale
        edgeright[y]=np.int(framesize[1]-np.argmax(image[y,range(framesize[1]-1,0,-1)]<thresh))
        if mode == 'Linear':
            leftsubpxcorr,rightsubpxcorr=linear_subpixel(edgeleft[y],edgeright[y],image[y,:],thresh)
        elif mode == 'Errorfunction':
            leftsubpxcorr,rightsubpxcorr=errorfunc_subpixel(edgeleft[y],edgeright[y],image[y,:],erffitsize)
        else:
            leftsubpxcorr=0
            rightsubpxcorr=0
        edgeleft[y]+=leftsubpxcorr
        edgeright[y]+=rightsubpxcorr
    return edgeleft, edgeright

def linear_subpixel(edgeleft,edgeright,imagerow,thresh):
    """
    Linear interpolation between two pixels left and right of the detected edge, finding the subpixel position of threshold value
    """
    if edgeleft!=0:
        #subpixel correction with using corr=(threshold-intensity(edge-1))/(intensity(edge)-intensity(edge-1))
        leftsubpxcorr=(thresh-np.float64(imagerow[np.int(edgeleft-1)]))/(np.float64(imagerow[np.int(edgeleft)])-np.float64(imagerow[np.int(edgeleft-1)]))-1 
    else:
        leftsubpxcorr=0
    if edgeright!=len(imagerow):
        rightsubpxcorr=(thresh-np.float64(imagerow[np.int(edgeright-1)]))/(np.float64(imagerow[np.int(edgeright)])-np.float64(imagerow[np.int(edgeright-1)]))-1
    else:
        rightsubpxcorr=0
    return leftsubpxcorr,rightsubpxcorr

def errorfunc_subpixel(edgeleft,edgeright,imagerow,erffitsize):
    """
    Subpixel detection by fitting an error function on the 'erffitsize' pixels around the detected edge
    """
    def errorfunction(x,xdata,y): #define errorfunction to fit with a least squares fit.
        return x[0]*(1+sp.special.erf(xdata*x[1]+x[2]))+x[3] - y
    if (edgeleft-erffitsize)>=0  and (edgeleft-erffitsize)<=len(imagerow):
        fitparts=np.array(imagerow[range(np.int(edgeleft)-erffitsize,np.int(edgeleft)+erffitsize)]) #take out part of the image around the edge to fit the error function
        guess=(max(fitparts)-min(fitparts))/2,-.22,0,min(fitparts) #initial guess for error function
        lstsqrsol=sp.optimize.least_squares(errorfunction,guess,args=(np.array(range(-erffitsize,erffitsize)),fitparts)) #least sqaures fit
        leftsubpxcorr=-lstsqrsol.x[2]/lstsqrsol.x[1] #add the subpixel correction
    else:
        leftsubpxcorr=0
    if (edgeright-erffitsize)>=0  and (edgeright+erffitsize)<len(imagerow):
        fitparts=np.array(imagerow[range(np.int(edgeright)-erffitsize,np.int(edgeright)+erffitsize)])
        guess=(max(fitparts)-min(fitparts))/2,.22,0,min(fitparts)
        lstsqrsol=sp.optimize.least_squares(errorfunction,guess,args=(np.array(range(-erffitsize,erffitsize)),fitparts))
        rightsubpxcorr=-lstsqrsol.x[2]/lstsqrsol.x[1]
    else:
        rightsubpxcorr=0
    return leftsubpxcorr,rightsubpxcorr

        
