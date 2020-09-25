def analysis(edgeleft,edgeright,baseinput,framesize):
    """
    Analizes the detected edge of the drop with the set baseline to
    give the contact angle, contact line position, and drop volume
    """
    from shapely.geometry import LineString
    import numpy as np
    #extend the baseline to the edge of the frame (in case the drop grows)

    baseline=LineString(base) #using shapely we construct baseline
