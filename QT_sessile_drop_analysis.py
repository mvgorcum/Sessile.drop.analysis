from PyQt5 import QtWidgets, uic, QtGui
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
            return self.framebuffer.pop()
        else:
            return -1

    def _aquire(self):
        self.cap = cv2.VideoCapture(0)
        cv2.waitKey(25)
        if self.is_running:
            print("already running")
            return
        self.is_running = True
        while self.keep_running:
            if not self.cap.isOpened(): 
                errorpopup=QtGui.QMessageBox()
                errorpopup.setText('Error opening video stream')
                errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
                errorpopup.exec_()
                raise Exception('Error opening video stream')
            ret, org_frame = self.cap.read()
            self.framebuffer.append(org_frame)
            self.framecaptime.append(datetime.datetime.now())
            cv2.waitKey(25)
            self.frameready = True
        self.cap.release()
        self.is_running = False


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        uic.loadUi('Mainwindow.ui', self)
        self.VideoItem = pg.ImageItem()
        self.VideoWidget.addItem(self.VideoItem)
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
        
        
#        FirstFrameCap = cv2.VideoCapture(VideoFile)
#        Success, FirstFrame = FirstFrameCap.read()
#        if Success:
#            self.VideoItem.setImage(cv2.cvtColor(FirstFrame, cv2.COLOR_BGR2RGB),autoRange=True)
#            self.ReadVideoFile=True
#            FirstFrameCap.release()
#            self.VideoFile=VideoFile
    
    def StartStop(self):
        
        # Check if camera toggle is on, read live feed if it is
        if self.StartStopButton.isChecked():
            self.StartStopButton.setText('Stop Measurement')
            AnalysisThread = threading.Thread(target=self.RunAnalysis)
            AnalysisThread.start()
        elif not self.StartStopButton.isChecked():
            self.StartStopButton.setText('Start Measurement')
    
    def CameraToggle(self):
        if self.CameraToggleButton.isChecked():
            CameraThread = threading.Thread(target=self.CameraCapture)
            CameraThread.start()
    
    def CameraCapture(self):
        self.FrameSource=OpencvCamera()
        self.FrameSource.start()

        while True:
            if not self.StartStopButton.isChecked():
                org_frame = self.FrameSource.getnextframe()
                if not np.all(org_frame==-1):
                    self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)
            else:
                sleep(0.5)
            if not self.CameraToggleButton.isChecked():
                self.FrameSource.stop()
                break

            
    
    def RunAnalysis(self):
        while self.StartStopButton.isChecked():
            org_frame = self.FrameSource.getnextframe()
            if not np.all(org_frame==-1):
                gray = cv2.cvtColor(org_frame, cv2.COLOR_BGR2GRAY)
                thresh, _ =cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
                EdgeLeft,EdgeRight=linedge(gray,thresh)
                self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)

    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()
    
