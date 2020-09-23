from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSignal

import cv2
import pyqtgraph as pg
import sys
from pathlib import Path
from edge_detection import linear_subpixel_detection as linedge
import numpy as np
import threading
from time import sleep
import datetime

pg.setConfigOptions(imageAxisOrder='row-major')


class FrameSupply:
    """
    Main class that can supply frames for further analysis.
    """

    def __init__(self):
        self.frameready = False
        self.is_running = False

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

class OpencvReadVideo(FrameSupply):
    """
    Read videofile with OpenCV
    """
    def __init__(self,VideoFile):
        super().__init__()
        self.VideoFile=VideoFile
        self.is_running = False
    
    def start(self):
        self.cap = cv2.VideoCapture(self.VideoFile)
        self.is_running = True
        
        
    def stop(self):
        """
        Stop the feed
        """
        self.cap.release()
        
    def getnextframe(self):
        ret, org_frame = self.cap.read()
        if ret:
            return org_frame
        else:
            self.is_running=False
            self.stop()
            return -1

class OpencvCamera(FrameSupply):
    """
    Camera operated using OpenCV
    """

    def __init__(self):
        super().__init__()
        self.framebuffer = []
        self.framecaptime = []
        self.imaging_thread = []
        self.keep_running = False
        self.is_running = False

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
        if len(self.framebuffer)>=1:
            
            return self.framebuffer.pop(0)
        else:
            return -1

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
            self.framebuffer.append(org_frame)
            self.framecaptime.append(datetime.datetime.now())
            self.frameready = True
        self.cap.release()
        self.is_running = False


class MainWindow(QtWidgets.QMainWindow):
    updateVideo = pyqtSignal(np.ndarray)
    updateLeftEdge = pyqtSignal(np.ndarray,np.ndarray)
    updateRightEdge = pyqtSignal(np.ndarray,np.ndarray)
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('Mainwindow.ui', self)
        
        self.VideoItem = pg.ImageView(parent=self.VideoWidget)
        self.LeftEdgeItem=pg.PlotCurveItem(pen='c')
        self.RightEdgeItem=pg.PlotCurveItem(pen='c')
        self.VideoItem.addItem(self.LeftEdgeItem)
        self.VideoItem.addItem(self.RightEdgeItem)
        self.updateVideo.connect(self.VideoItem.setImage)
        self.updateLeftEdge.connect(self.LeftEdgeItem.setData)
        self.updateRightEdge.connect(self.RightEdgeItem.setData)
        
        self.BaseLine=pg.LineSegmentROI([(10,10),(100,10)],pen='r')
        self.VideoItem.addItem(self.BaseLine)
        
        self.actionOpen.triggered.connect(self.openCall)
        self.StartStopButton.clicked.connect(self.StartStop)
        self.CameraToggleButton.clicked.connect(self.CameraToggle)
        
        self.FrameSource=FrameSupply()

    def openCall(self):
        if self.FrameSource.is_running:
            self.FrameSource.stop()
        home_dir = '/data/github/Sessile.drop.analysis/Sample/'
        VideoFile, _ = QtGui.QFileDialog.getOpenFileName(self,'Open file', home_dir)  
        self.FrameSource=OpencvReadVideo(VideoFile)
        self.FrameSource.start()
        self.VideoItem.setImage(cv2.cvtColor(self.FrameSource.getnextframe(), cv2.COLOR_BGR2RGB),autoRange=True)
        
        
    def StartStop(self):
        if self.StartStopButton.isChecked():
            self.StartStopButton.setText('Stop Measurement')
            AnalysisThread = threading.Thread(target=self.RunAnalysis)
            AnalysisThread.start()
        elif not self.StartStopButton.isChecked():
            self.StartStopButton.setText('Start Measurement')
    
    def CameraToggle(self):
        if self.CameraToggleButton.isChecked():
            self.FrameSource=OpencvCamera()
            self.FrameSource.start()
            CameraThread = threading.Thread(target=self.CameraCapture)
            CameraThread.start()
    
    def CameraCapture(self):
        while self.CameraToggleButton.isChecked():
            if self.StartStopButton.isChecked():
                sleep(0.5)
            else:
                org_frame = self.FrameSource.getnextframe()
                if not np.all(org_frame==-1):
                    self.updateVideo.emit(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB))
                else:
                    sleep(0.0001)
        self.FrameSource.stop()
    
    def RunAnalysis(self):
        while self.StartStopButton.isChecked():
            org_frame = self.FrameSource.getnextframe()
            if not np.all(org_frame==-1):
                gray = cv2.cvtColor(org_frame, cv2.COLOR_BGR2GRAY)
                thresh, _ =cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
                EdgeLeft,EdgeRight=linedge(gray,thresh)
                self.updateVideo.emit(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB))
                self.updateLeftEdge.emit(EdgeLeft+0.5,np.arange(0,len(EdgeLeft))+0.5)
                self.updateRightEdge.emit(EdgeRight+0.5,np.arange(0,len(EdgeRight))+0.5)
            else:
                sleep(0.001)


    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()
    
