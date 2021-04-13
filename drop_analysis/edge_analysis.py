def analysis(edgeleft,edgeright,baseinput,framesize,k=100,PO=2):
    """
    Analyzes the detected edge of the drop with the set baseline to
    give the contact angle, contact line position, and drop volume
    k represents the number of pixels up from the baseline to fit, PO is the 
    order of the polyfit used to fit the edge of the drop
    Returns contactpoints left and right, theta left and right, and drop volume
    """
    from shapely.geometry import LineString
    import numpy as np

    baseline=LineString(baseinput) 
    rightline=LineString(np.column_stack((edgeright,(range(0,framesize[0]))))) 
    leftline=LineString(np.column_stack((edgeleft,(range(0,framesize[0])))))
    leftcontact=baseline.intersection(leftline)
    #print(leftcontact)
    rightcontact=baseline.intersection(rightline)
    fitpointsleft=edgeleft[range(np.int(np.floor(leftcontact.y)),np.int(np.floor(leftcontact.y)-k),-1)]
    if any(fitpointsleft==0):
        fitpointsleft=np.delete(fitpointsleft,range(np.argmax(fitpointsleft==0),k))
    fitpointsright=edgeright[range(np.int(np.floor(rightcontact.y)),np.int(np.floor(rightcontact.y)-k),-1)]
    if any(fitpointsright==0):
        fitpointsright=np.delete(fitpointsright,range(np.argmax(fitpointsright==0),k))
        
    leftfit=np.polyfit(range(0,fitpointsleft.shape[0]),fitpointsleft,PO)
    leftvec=np.array([1,leftfit[PO-1]]) 
    
    rightfit=np.polyfit(range(0,fitpointsright.shape[0]),fitpointsright,PO)
    rightvec=np.array([1,rightfit[PO-1]]) 
    
    basevec=np.array([-(baseinput[1,1]-baseinput[0,1])/baseinput[1,0],1]) 
    thetal=np.arccos(np.dot(basevec,leftvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(leftvec,leftvec))))*180/np.pi
    thetar=180-np.arccos(np.dot(basevec,rightvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(rightvec,rightvec))))*180/np.pi
    contactpointright=rightfit[PO]
    contactpointleft=leftfit[PO]
    dropvolume=0
    for height in range (0,min(np.int(np.floor(leftcontact.y)),np.int(np.floor(rightcontact.y)))):
        dropvolume=dropvolume+np.pi*np.square((edgeright[height]-edgeleft[height])/2)
    #using cylindrical slice we calculate the remaining volume
    slantedbasediff=max(np.floor(leftcontact.y),np.floor(rightcontact.y))-min(np.floor(leftcontact.y),np.floor(rightcontact.y))
    #we assume that the radius is constant over the range of the slanted baseline, for small angles this is probably accurate, but for larger angles this can result in a significant error.
    baseradius=(edgeright[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))]-edgeleft[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))])/2
    dropvolume=dropvolume+.5*np.pi*np.square(baseradius)*slantedbasediff
    
    rightfitcurve=np.polyval(rightfit,np.arange(k))
    leftfitcurve=np.polyval(leftfit,np.arange(k))
    debug=np.array([leftfitcurve,leftcontact.y-np.arange(k),rightfitcurve,rightcontact.y-np.arange(k)])
    results={'thetaleft':thetal, 'thetaright':thetar, 'contactpointleft':contactpointleft,'contactpointright':contactpointright,'volume':dropvolume}
    
    return results, debug
