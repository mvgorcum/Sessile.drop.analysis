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
        self.running = False

    def run(self):
        """
        Start the frame supply. Required to get frames.
        """
        pass

    def getlastframe(self):
        """
        Get the last frame from the frame supply buffer.
        Only possible if frameready is true.
        """
        pass


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
        

    def getlastframe(self):
        """
        Get the last frame
        :return:
        """
        if len(self.framebuffer)>=1:
            return self.framebuffer.pop()
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
        self.LeftEdgeItem=pg.PlotCurveItem()
        self.RightEdgeItem=pg.PlotCurveItem()
        self.VideoWidget.addItem(self.LeftEdgeItem)
        self.VideoWidget.addItem(self.RightEdgeItem)
        
    def openCall(self):
        home_dir = '/data/github/Sessile.drop.analysis/Sample/'
        VideoFile, _ = QtGui.QFileDialog.getOpenFileName(self,'Open file', home_dir)  
        FirstFrameCap = cv2.VideoCapture(VideoFile)
        Success, FirstFrame = FirstFrameCap.read()
        if Success:
            self.VideoItem.setImage(cv2.cvtColor(FirstFrame, cv2.COLOR_BGR2RGB),autoRange=True)
            self.ReadVideoFile=True
            FirstFrameCap.release()
            self.VideoFile=VideoFile
    
    def StartStop(self):
        # Check if camera toggle is on, read live feed if it is
        if self.CameraToggleButton.isChecked():
            if self.StartStopButton.isChecked():
                self.StartStopButton.setText('Stop Measurement')
            elif not self.StartStopButton.isChecked():
                self.StartStopButton.setText('Start Measurement')
        elif not self.CameraToggleButton.isChecked():  
            if self.StartStopButton.isChecked():
                self.StartStopButton.setText('Stop Measurement')
                self.VideoRead()
            elif not self.StartStopButton.isChecked():
                self.StartStopButton.setText('Start Measurement')
    
    def CameraToggle(self):
        if self.CameraToggleButton.isChecked():
            CameraThread = threading.Thread(target=self.CameraCapture)
            CameraThread.start()
    
    def CameraCapture(self):
        cameraobject=OpencvCamera()
        cameraobject.start()
        sleep(1)

        while True:
            org_frame = cameraobject.getlastframe()
            if not np.all(org_frame==-1):
                self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)
                if self.StartStopButton.isChecked():
                    print('we should analyse the data now')
            if not self.CameraToggleButton.isChecked():
                cameraobject.stop()
                break

            
    
    def VideoRead(self):
        cap = cv2.VideoCapture(self.VideoFile)
        while(cap.isOpened()):
            ret, org_frame = cap.read()
            cv2.waitKey(25)
            if not self.StartStopButton.isChecked():
                cap.release()
                break
            gray = cv2.cvtColor(org_frame, cv2.COLOR_BGR2GRAY)
            thresh, _ =cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
            EdgeLeft,EdgeRight=linedge(gray,thresh)
            self.LeftEdgeItem.setData(EdgeLeft+1,np.arange(0,len(EdgeLeft)),pen='r')
            self.RightEdgeItem.setData(EdgeRight,np.arange(0,len(EdgeRight)),pen='r')
            self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)

    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()
    
