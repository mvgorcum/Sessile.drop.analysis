from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSignal

import cv2
import pyqtgraph as pg
import sys
import imageio
from pathlib import Path
from skimage.filters import threshold_otsu
from edge_detection import linear_subpixel_detection as linedge
from edge_analysis import analysis
import numpy as np
import pandas as pd
import threading
from time import sleep
import datetime
import magic

pg.setConfigOptions(imageAxisOrder='row-major')



class FrameSupply:
    """
    Main class that can supply frames for further analysis.
    """

    def __init__(self):
        self.frameready = False
        self.is_running = False
        self.framebuffer=[]
        self.nframes=0
        self.framenumber=0

    def run(self):
        """
        Start the frame supply. Required to get frames.
        """
        pass

    def getnextframe(self):
        """
        Get the last frame from the frame supply buffer.
        Only possible if frameready is true.
        """
        pass
    def getframesize(self):
        """
        Get the width and height of the frame.
        """
        pass

class OpencvReadVideo(FrameSupply):
    """
    Read videofile with OpenCV
    """
    def __init__(self,VideoFile):
        super().__init__()
        self.VideoFile=VideoFile
        self.is_running = False
        self.gotcapturetime=False
    
    def start(self):
        self.cap = cv2.VideoCapture(self.VideoFile)
        self.is_running = True
        self.nframes=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
    def stop(self):
        """
        Stop the feed
        """
        self.cap.release()
    
    def getfirstframe(self):
        ret, org_frame = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES,0)
        return cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),0
    
    def getnextframe(self):
        self.framenumber = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret, org_frame = self.cap.read()
        if ret:
            return cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),self.framenumber
        else:
            self.is_running=False
            self.stop()
            return -1,-1
        
    def getframesize(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    

class ImageReader(FrameSupply):
    """
    Read videofile with OpenCV
    """
    def __init__(self,ImageFile):
        super().__init__()
        self.ImageFile=ImageFile
        self.is_running = False
        self.gotcapturetime=False
        self.framenumber=0
        
    def start(self):
        self.is_running = True
        self.IOReader=imageio.get_reader(self.ImageFile)
        self.nframes=self.IOReader.get_length()
        
    def stop(self):
        """
        Stop the feed
        """
        self.is_running = False
        self.IOReader.close()
    
    def getfirstframe(self):
        org_frame=self.IOReader.get_data(0)
        return org_frame, 0
        
    def getnextframe(self):
        if self.framenumber<self.nframes:
            org_frame = self.IOReader.get_data(self.framenumber)
            self.framenumber+=1
            return org_frame,self.framenumber
        else:
            return -1,-1
        
    def getframesize(self):
        org_frame=self.IOReader.get_data(0)
        size=org_frame.shape
        return size[1],size[0]


class OpencvCamera(FrameSupply):
    """
    Camera operated using OpenCV
    """

    def __init__(self):
        super().__init__()
        self.framecaptime = []
        self.imaging_thread = []
        self.keep_running = False
        self.is_running = False
        self.gotcapturetime=True

    def start(self):
        """
        Start the camera
        """
        self.keep_running = True
        self.imaging_thread = threading.Thread(target=self._aquire)
        self.imaging_thread.start()

    def stop(self):
        """
        Stop the camera
        """
        self.keep_running = False
        

    def getnextframe(self):
        """
        Get the last frame
        :return:
        """
        self.nframes=len(self.framebuffer)
        if len(self.framebuffer)>=1:
            
            return self.framebuffer.pop(0),self.framecaptime.pop(0)
        else:
            return -1,-1
        
    def getframesize(self):
        if not 'self.cap' in locals():
            sleep(0.5)
            return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        else:
            return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def _aquire(self):
        if self.is_running:
            print("already running")
            return
        self.is_running = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened(): 
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Error opening video stream')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()
            self.cap.release()
            self.is_running = False
            self.keep_running = False
        while self.keep_running:
            ret, org_frame = self.cap.read()
            self.framebuffer.append(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB))
            self.framecaptime.append(np.datetime64(datetime.datetime.now()))
            self.frameready = True
        self.cap.release()
        self.is_running = False


filetypemap={'image/tiff':ImageReader,'image/png':ImageReader,'video/x-msvideo':OpencvReadVideo}



class MainWindow(QtWidgets.QMainWindow):
    updateVideo = pyqtSignal(np.ndarray)
    updateLeftEdge = pyqtSignal(np.ndarray,np.ndarray)
    updateRightEdge = pyqtSignal(np.ndarray,np.ndarray)
    updatePlotLeft = pyqtSignal(np.ndarray,np.ndarray)
    updatePlotRight = pyqtSignal(np.ndarray,np.ndarray)
    updateLeftEdgeFit = pyqtSignal(np.ndarray,np.ndarray)
    updateRightEdgeFit = pyqtSignal(np.ndarray,np.ndarray)
    updateFrameCount=pyqtSignal(int,int)
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('Mainwindow.ui', self)
        
        
        self.RootVidPlot=self.VideoWidget.getPlotItem()
        self.RootVidPlot.setAspectLocked(True)
        self.RootVidPlot.hideAxis('bottom')
        self.RootVidPlot.hideAxis('left')
        self.RootVidPlot.invertY(True)
        
        self.VideoItem = pg.ImageItem()
        self.RootVidPlot.addItem(self.VideoItem)
        self.LeftEdgeItem=pg.PlotCurveItem(pen=pg.mkPen(color='#ff7f0e', width=2))
        self.RightEdgeItem=pg.PlotCurveItem(pen=pg.mkPen(color='#1f77b4', width=2))
        self.LeftEdgeFit=pg.PlotCurveItem(pen=pg.mkPen(color='#ff7f0e', width=4))
        self.RightEdgeFit=pg.PlotCurveItem(pen=pg.mkPen(color='#1f77b4', width=4))
        
        self.RootVidPlot.addItem(self.LeftEdgeItem)
        self.RootVidPlot.addItem(self.RightEdgeItem)
        self.RootVidPlot.addItem(self.RightEdgeFit)
        self.RootVidPlot.addItem(self.LeftEdgeFit)
        self.updateVideo.connect(self.VideoItem.setImage)
        self.updateLeftEdge.connect(self.LeftEdgeItem.setData)
        self.updateRightEdge.connect(self.RightEdgeItem.setData)
        self.updateLeftEdgeFit.connect(self.LeftEdgeFit.setData)
        self.updateRightEdgeFit.connect(self.RightEdgeFit.setData)
        
        self.ThetaLeftPlot=pg.ScatterPlotItem(pen='#ff7f0e',brush='#ff7f0e',symbol='o')
        self.ThetaRightPlot=pg.ScatterPlotItem(pen='#1f77b4',brush='#1f77b4',symbol='o')
        self.PlotItem=self.PlotWidget.getPlotItem()
        self.updatePlotLeft.connect(self.ThetaLeftPlot.setData)
        self.updatePlotRight.connect(self.ThetaRightPlot.setData)
        
        self.BaseLine=pg.LineSegmentROI([(15,90),(100,90)],pen='#d62728')
        self.CropRoi=pg.RectROI([10,10],[110,110],scaleSnap=True)
        self.CropRoi.addScaleHandle([0,0],[1,1])
        self.VideoWidget.addItem(self.CropRoi)
        self.VideoWidget.addItem(self.BaseLine)
        
        
        self.actionOpen.triggered.connect(self.openCall)
        self.actionSave.triggered.connect(self.SaveResult)
        self.StartStopButton.clicked.connect(self.StartStop)
        self.CameraToggleButton.clicked.connect(self.CameraToggle)
        
        self.FrameSource=FrameSupply()
        self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])

        self.MaybeSave=False
        self.kInputSpinbox.setValue(self.kInputSlider.value())
        self.kInputSlider.valueChanged.connect(lambda: self.kInputSpinbox.setValue(self.kInputSlider.value()))	
        self.kInputSpinbox.valueChanged.connect(lambda: self.kInputSlider.setValue(self.kInputSpinbox.value()))	
        
        self.updateFrameCount.connect(lambda f,n: self.FrameCounterText.setText('Frame: '+str(f)+'/'+str(n)))
    
    def closeEvent(self, event):
        if self.FrameSource.is_running:
            self.FrameSource.stop()
            



    def openCall(self):
        if self.FrameSource.is_running:
            self.FrameSource.stop()
        home_dir = '/data/github/Sessile.drop.analysis/Sample/'
        VideoFile, _ = QtGui.QFileDialog.getOpenFileName(self,'Open file', home_dir)
        mimetype=magic.from_file(VideoFile,mime=True)
        self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])
        self.PlotItem.clear()
        if any(mimetype in key for key in filetypemap):
            self.FrameSource=filetypemap[mimetype](VideoFile)
            self.FrameSource.start()
            FrameWidth,FrameHeight=self.FrameSource.getframesize()
            self.CropRoi.setPos([FrameWidth*.1,FrameHeight*.1])
            self.CropRoi.setSize([FrameWidth*.8,FrameHeight*.8])
            self.BaseLine.setPos([FrameWidth*.2,FrameHeight*.7])
            firstframe,_=self.FrameSource.getfirstframe()
            self.VideoItem.setImage(firstframe,autoRange=True)
        else:
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Unkown filetype')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()
        
        
    def StartStop(self):
        if self.StartStopButton.isChecked():
            self.StartStopButton.setText('Stop Measurement')
            self.PlotItem.setLabel('left',text='Contact angle [°]')
            if self.FrameSource.gotcapturetime:
                self.PlotItem.setLabel('bottom',text='Time [s]')
            else:
                self.PlotItem.setLabel('bottom',text='Frame number')
            AnalysisThread = threading.Thread(target=self.RunAnalysis)
            AnalysisThread.start()
            
        elif not self.StartStopButton.isChecked():
            self.StartStopButton.setText('Start Measurement')
    
    def CameraToggle(self):
        if self.CameraToggleButton.isChecked():
            self.FrameSource=OpencvCamera()
            self.FrameSource.start()
            FrameWidth,FrameHeight=self.FrameSource.getframesize()
            self.CropRoi.setPos([FrameWidth*.1,FrameHeight*.1])
            self.CropRoi.setSize([FrameWidth*.8,FrameHeight*.8])
            self.BaseLine.setPos([FrameWidth*.2,FrameHeight*.7])
            CameraThread = threading.Thread(target=self.CameraCapture)
            CameraThread.start()
            self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])
            self.PlotItem.clear()
    
    def CameraCapture(self):
        while self.CameraToggleButton.isChecked():
            if self.StartStopButton.isChecked():
                sleep(0.5)
            else:
                org_frame, _ = self.FrameSource.getnextframe()
                if not np.all(org_frame==-1):
                    self.updateVideo.emit(org_frame)
                else:
                    sleep(0.001)
        self.FrameSource.stop()
    
    def RunAnalysis(self):                
        self.PlotItem.addItem(self.ThetaLeftPlot)
        self.PlotItem.addItem(self.ThetaRightPlot)
        while self.StartStopButton.isChecked():
            org_frame,framecaptime = self.FrameSource.getnextframe()
            if not np.all(org_frame==-1):
                #get crop and save coordinate transformation
                self.updateVideo.emit(org_frame)
                cropcoords=self.CropRoi.getArraySlice(org_frame, self.VideoItem, returnSlice=False)
                verticalCropOffset=0.5+cropcoords[0][0][0]
                horizontalCropOffset=0.5+cropcoords[0][1][0]

                cropped=org_frame[cropcoords[0][0][0]:cropcoords[0][0][1],cropcoords[0][1][0]:cropcoords[0][1][1]]
                #get baseline positions and extrapolate to the edge of the crop
                _,basearray=self.BaseLine.getArrayRegion(org_frame, self.VideoItem, returnSlice=False, returnMappedCoords=True)
                baseinput=[[basearray[0,0]-horizontalCropOffset,basearray[1,0]-verticalCropOffset],[basearray[0,-1]-horizontalCropOffset,basearray[1,-1]-verticalCropOffset]]
                del basearray
                rightbasepoint=np.argmax([baseinput[0][0],baseinput[1][0]])
                baseslope=np.float(baseinput[rightbasepoint][1]-baseinput[1-rightbasepoint][1])/(baseinput[rightbasepoint][0]-baseinput[1-rightbasepoint][0])
                base=np.array([[0,baseinput[0][1]-baseslope*baseinput[0][0]],[org_frame.shape[1],baseslope*org_frame.shape[1]+baseinput[0][1]-baseslope*baseinput[0][0]]])
                if len(org_frame.shape)==3:
                    gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
                else:
                    gray = np.asarray(cropped)
                thresh=threshold_otsu(gray,np.iinfo(type(gray.flat[0])).max)
                CroppedEdgeLeft,CroppedEdgeRight=linedge(gray,thresh)
                EdgeLeft=CroppedEdgeLeft+horizontalCropOffset
                EdgeRight=CroppedEdgeRight+horizontalCropOffset
                contactpointleft, contactpointright, thetal, thetar, dropvolume, debuginfo = analysis(EdgeLeft,EdgeRight,base,cropped.shape,k=self.kInputSpinbox.value(),PO=2)
                newrow={'thetaleft':thetal, 'thetaright':thetar, 'contactpointleft':contactpointleft,'contactpointright':contactpointright,'volume':dropvolume,'time':framecaptime}
                self.MeasurementResult=self.MeasurementResult.append(newrow,ignore_index=True)
                if self.FrameSource.gotcapturetime:
                    plottime=self.MeasurementResult['time']-self.MeasurementResult.iloc[0]['time']
                    #convert from nanoseconds to seconds
                    plottime=plottime.to_numpy().astype('float')*10**-9
                else:
                    plottime=self.MeasurementResult['time'].to_numpy()
                plotleft=self.MeasurementResult['thetaleft'].to_numpy()
                plotright=self.MeasurementResult['thetaright'].to_numpy()
                self.MeasurementResult=self.MeasurementResult.append(newrow,ignore_index=True)
                self.updateLeftEdge.emit(EdgeLeft,np.arange(0,len(EdgeLeft))+verticalCropOffset)
                self.updateRightEdge.emit(EdgeRight,np.arange(0,len(EdgeRight))+verticalCropOffset)
                self.updatePlotLeft.emit(plottime,plotleft)
                self.updatePlotRight.emit(plottime,plotright)
                self.updateLeftEdgeFit.emit(debuginfo[0,:],verticalCropOffset+debuginfo[1,:])
                self.updateRightEdgeFit.emit(debuginfo[2,:],verticalCropOffset+debuginfo[3,:])
                self.MaybeSave=True
                self.updateFrameCount.emit(self.FrameSource.framenumber,self.FrameSource.nframes)
            else:
                sleep(0.001)
            if (not self.FrameSource.is_running and len(self.FrameSource.framebuffer)<1):
                break
            
    def SaveResult(self):
        if  len(self.MeasurementResult.index)>0:
            if not self.FrameSource.gotcapturetime:
                self.MeasurementResult=self.MeasurementResult.rename(columns={"time": "framenumber"})
            SaveFileName, _ =QtGui.QFileDialog.getSaveFileName(self,'Save file', '', "Excel Files (*.xlsx);;All Files (*)")
            self.MeasurementResult.to_excel(SaveFileName)
            self.MaybeSave=False
        else:
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Nothing to save')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()
