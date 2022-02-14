# Python sessile drop analysis
[![Element Android Matrix room #Sessile.Drop.Analysis:matrix.vgorcum.com](https://img.shields.io/matrix/Sessile.Drop.Analysis:matrix.vgorcum.com.svg?label=%23Sessile.Drop.Analysis:matrix.vgorcum.com&logo=matrix&server_fqdn=matrix.org)](https://matrix.to/#/#Sessile.Drop.Analysis:matrix.vgorcum.com)

Made by Mathijs van Gorcum during his PhD at the Physics of Fluids group of the University of Twente.

Python program to analyze sessile drops by measuring contact angle, drop volume and contact line position (as function of time or framenumber).  
This program can capture images or movies from a camera or import image sequences (in the form of an movie file, a tiffstack or a single image) and measures the contact angle, drop volume and the contact line position.  
The program assumes an image of a drop on the surface, where the drop is dark, and the background is light.
A crop (to increase calculation speed, and cut off any irrelevant parts) and a baseline must be set on the view of the image. The Edgepixels to fit setting increases the amount of pixels up from the baseline used to measure the contact angle and contact line position.  
We use a subpixel edge detection, either fast (with a linear interpolation between two pixels around the edge) or slow and more precise (by fitting an error function around the edge). To find the contact line position and the contact angle the detected edge is fitted with a configurable order polynomial fit, and the slope of the baseline is also used to calculate the contact angles. Note that the drop volume assume cylindrical symmetry and if there is a needle present, the volume of the needle is added for as much as it is in view of the crop.

## Screenshot

![](https://github.com/mvgorcum/Sessile.drop.analysis/blob/master/Screenshot.png)

## Install and running
This program has an installer for windows available in the [releases assets on github](https://github.com/mvgorcum/Sessile.drop.analysis/releases), or is installable from pypi.org with `pip install drop-analysis`.

To install the program from source run `pip install .` in the sessile.drop.analysis folder. To run the program after installing simply run drop_analysis in the terminal.

## Prerequisites
If you don't use the precomiled releases nor `pip install` it you'll need:
The script requires numpy, pandas, scipy, pyqt5, opencv-python, fast-histogram, lsq-ellipse, imageio, shapely, pyqtgraph >=0.11.0, openpyxl, toml, h5py, json, and appdirs.

## Support
If you have any questions feel free to join the [#Sessile.Drop.Analysis:matrix.vgorcum.com](https://matrix.to/#/#Sessile.Drop.Analysis:matrix.vgorcum.com) matrix room or open an issue on github.

## Some details
* The code is written for Python 3.9
* The edge detection uses only a horizontal subpixel correction, and when fitting the errorfunction, 40 pixels left and right of the edge are used.  
* To find the contact angle and contact point a polyfit is used, but the fit is made flipping the x and y coordinates, because polyfits don't perform well for vertical lines (ie at contact angles of 90 degrees).  
* The threshold is calculated using otsu's method, for the fast edge detection the value is used explicitly while for the error function fitting the value is only used to find an approximate edge, to fit the errorfunction around.  
* The program calculates the speed in pixels/frame, and the volume in pixels^3, so be sure to convert it.

## Contributing
Feel free to send pull requests, critique my awful code or point out any issues.

## License
This project is licensed under the GPLv3 license - see the [LICENSE](https://github.com/mvgorcum/Sessile.drop.analysis/blob/master/LICENSE) file for details.  
This means the software can be freely used, for private, academic, or commercial purposes. If this program is distributed you are required to use a compatible open source license and must share the sourcecode of your version.
