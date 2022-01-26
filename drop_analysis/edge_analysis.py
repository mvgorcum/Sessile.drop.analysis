def analysis(edgeleft,edgeright,baseinput,framesize,k=100,PO=3,fittype='polyfit'):
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
    rightcontact=baseline.intersection(rightline)
    fitpointsleft=edgeleft[range(np.int(np.floor(leftcontact.y)),np.int(np.floor(leftcontact.y)-k),-1)]
    if any(fitpointsleft==0):
        fitpointsleft=np.delete(fitpointsleft,range(np.argmax(fitpointsleft==0),k))
    fitpointsright=edgeright[range(np.int(np.floor(rightcontact.y)),np.int(np.floor(rightcontact.y)-k),-1)]
    if any(fitpointsright==0):
        fitpointsright=np.delete(fitpointsright,range(np.argmax(fitpointsright==0),k))
    
    if fittype=='Polyfit':
        results, debug = analysepolyfit(fitpointsleft,fitpointsright,leftcontact,rightcontact,baseinput,baseline,k,PO)
    elif fittype=='Ellipse':
        results, debug = analysellipse(fitpointsleft,fitpointsright,leftcontact,rightcontact,baseinput,baseline,k,framesize)
    else:
        print('Unkown fittype')
        
    dropvolume=volumecalc(leftcontact,rightcontact,edgeleft,edgeright)
    results['volume']=dropvolume
    
    return results, debug

def volumecalc(leftcontact,rightcontact,edgeleft,edgeright):
    import numpy as np
    dropvolume=0
    for height in range (0,min(np.int(np.floor(leftcontact.y)),np.int(np.floor(rightcontact.y)))):
        dropvolume=dropvolume+np.pi*np.square((edgeright[height]-edgeleft[height])/2)
    #uing cylindrical slice we calculate the remaining volume
    slantedbasediff=max(np.floor(leftcontact.y),np.floor(rightcontact.y))-min(np.floor(leftcontact.y),np.floor(rightcontact.y))
    #we assume that the radius is constant over the range of the slanted baseline, for small angles this is probably accurate, but for larger angles this can result in a significant error.
    baseradius=(edgeright[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))]-edgeleft[np.int(min(np.floor(leftcontact.y),np.floor(rightcontact.y)))])/2
    dropvolume=dropvolume+.5*np.pi*np.square(baseradius)*slantedbasediff
    return dropvolume

def analysepolyfit(fitpointsleft,fitpointsright,leftcontact,rightcontact,baseinput,baseline,k,PO):
    from shapely.geometry import LineString
    import numpy as np
    leftfit=np.polyfit(range(0,fitpointsleft.shape[0]),fitpointsleft,PO)
    leftvec=np.array([1,leftfit[PO-1]]) 
    
    rightfit=np.polyfit(range(0,fitpointsright.shape[0]),fitpointsright,PO)
    rightvec=np.array([1,rightfit[PO-1]]) 
    
    basevec=np.array([-(baseinput[1,1]-baseinput[0,1])/baseinput[1,0],1]) 
    thetal=np.arccos(np.dot(basevec,leftvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(leftvec,leftvec))))*180/np.pi
    thetar=180-np.arccos(np.dot(basevec,rightvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(rightvec,rightvec))))*180/np.pi

    
    
    fitcurvevar=np.arange(k+1)-1
    rightfitcurve=np.polyval(rightfit,fitcurvevar)
    leftfitcurve=np.polyval(leftfit,fitcurvevar)
    debug={'leftfit':np.array([leftfitcurve,leftcontact.y-fitcurvevar]),'rightfit':np.array([rightfitcurve,rightcontact.y-fitcurvevar])}
    
    # calculate contact points based on fitted edge intersection with baseline
    rightline=LineString(np.column_stack((rightfitcurve,rightcontact.y-fitcurvevar))) 
    leftline=LineString(np.column_stack((leftfitcurve,leftcontact.y-fitcurvevar)))
    contactpointright=baseline.intersection(rightline)
    contactpointleft=baseline.intersection(leftline)
    results={'thetaleft':thetal, 'thetaright':thetar, 'contactpointleft':contactpointleft.x,'contactpointright':contactpointright.x}
    
    return results,debug

def analysellipse(fitpointsleft,fitpointsright,leftcontact,rightcontact,baseinput,baseline,k,framesize):
    from ellipse import LsqEllipse
    from shapely.geometry import LineString
    import numpy as np
    yvarleft=range(np.int(np.floor(leftcontact.y)),np.int(np.floor(leftcontact.y)-k),-1)
    yvarright=range(np.int(np.floor(rightcontact.y)),np.int(np.floor(rightcontact.y)-k),-1)
    edge=np.append(fitpointsleft,fitpointsright)
    yvart=np.append(yvarleft,yvarright)
    totalfitpoints=np.array(list(zip(edge, yvart)))
    # fit the ellipse
    reg = LsqEllipse().fit(totalfitpoints)

    #pointsfitted=reg.return_fit(1000)
    a,b,c,d,e,f=reg.coefficients
    y=np.linspace(min(np.int(np.floor(leftcontact.y)),np.int(np.floor(rightcontact.y)))-k,max(np.int(np.floor(leftcontact.y)),np.int(np.floor(rightcontact.y)))+k,framesize[0]*10)
    
    #split ellipse in two parts with a vertical cut, to find the contact points
    #xellipse1&2 are just the function for ellipse solved for x(y)
    xellipse1=-(d + b * y + np.sqrt((d + b * y)**2 - 4 * a * (f + y*(e + c*y))))/(2*a)
    xellipse2=-(d + b * y - np.sqrt((d + b * y)**2 - 4 * a * (f + y*(e + c*y))))/(2*a)
    ellipseline1=LineString(np.column_stack((xellipse1,y)))
    ellipseline2=LineString(np.column_stack((xellipse2,y)))
    contact1=baseline.intersection(ellipseline1)
    contact2=baseline.intersection(ellipseline2)

    # determine which contact point is left and right
    if contact1.x<contact2.x:
        rightcontact=contact2
        leftcontact=contact1
        #d/dy of xellipse1&2
        sloperight=(-b - (2*b*(d + b*contact2.y) - 4*a*(e + 2*c*contact2.y))/(2*np.sqrt((d + b*contact2.y)**2 - 4*a*(f + contact2.y*(e + c*contact2.y)))))/(2*a)
        slopeleft= (-b + (2*b*(d + b*contact1.y) - 4*a*(e + 2*c*contact1.y))/(2*np.sqrt((d + b*contact1.y)**2 - 4*a*(f + contact1.y*(e + c*contact1.y)))))/(2*a)

    else:
        rightcontact=contact1
        leftcontact=contact2
        #d/dy of xellipse1&2
        slopeleft= (-b - (2*b*(d + b*contact2.y) - 4*a*(e + 2*c*contact2.y))/(2*np.sqrt((d + b*contact2.y)**2 - 4*a*(f + contact2.y*(e + c*contact2.y)))))/(2*a)
        sloperight=(-b + (2*b*(d + b*contact1.y) - 4*a*(e + 2*c*contact1.y))/(2*np.sqrt((d + b*contact1.y)**2 - 4*a*(f + contact1.y*(e + c*contact1.y)))))/(2*a)

    rightvec=np.array([1,sloperight])
    leftvec=np.array([1,slopeleft])
    basevec=np.array([-(baseinput[1,1]-baseinput[0,1])/baseinput[1,0],1]) 

    thetal=np.arccos(np.dot(basevec,leftvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(leftvec,leftvec))))*180/np.pi
    thetar=180-np.arccos(np.dot(basevec,rightvec)/(np.sqrt(np.dot(basevec,basevec))*np.sqrt(np.dot(rightvec,rightvec))))*180/np.pi
    
    ellipsepointsfitted=reg.return_fit(1000)
    
    
    
    
    debug={'leftfit':np.array([ellipsepointsfitted[:,0],ellipsepointsfitted[:,1]]),'rightfit':np.array([[],[]])}
    results={'thetaleft':thetal, 'thetaright':thetar, 'contactpointleft':leftcontact.x,'contactpointright':rightcontact.x}
    return results,debug
