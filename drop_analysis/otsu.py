import numpy as np
from fast_histogram import histogram1d
def otsu(gray):
    bitdepth=2**(gray[0,0].itemsize*8)
    histogramCounts=histogram1d(gray.flatten(),bins=bitdepth-1,range=[0,bitdepth-1])
    total = sum(histogramCounts)
    top = bitdepth-1
    sumB = 0
    wB = 0
    maximum = 0.0
    sum1 = np.dot(range(0,top), histogramCounts)
    for i,count in enumerate(histogramCounts):
        if count>0:
            wF = total - wB
            if (wB > 0 and wF > 0):
                mF = (sum1 - sumB) / wF
                val = wB * wF * ((sumB / wB) - mF) * ((sumB / wB) - mF)
                if ( val >= maximum ):
                    level = i
                    maximum = val
            elif wF==0:
                break
            wB = wB +count
            sumB = sumB + i * count
    return level
 
