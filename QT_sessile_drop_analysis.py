from PyQt5 import QtWidgets, uic, QtGui
import cv2
import pyqtgraph as pg
import sys
from pathlib import Path
from edge_detection import linear_subpixel_detection as linedge
import numpy as np
from time import sleep
import threading

pg.setConfigOptions(imageAxisOrder='row-major')


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        uic.loadUi('Mainwindow.ui', self)
        self.VideoItem = pg.ImageItem()
        self.VideoWidget.addItem(self.VideoItem)
        self.actionOpen.triggered.connect(self.openCall)
        self.StartStopButton.clicked.connect(self.StartStop)
        self.CameraToggleButton.clicked.connect(self.CameraToggle)
        

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
        
        cap = cv2.VideoCapture(0)
        cv2.waitKey(25)
        if not cap.isOpened(): 
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Error opening video stream')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()
            raise Exception('Error opening video stream')
        while(cap.isOpened()):
    
            ret, org_frame = cap.read()
            self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            if not self.CameraToggleButton.isChecked():
                print('stopping video read')
                cap.release()
                break
            if self.StartStopButton.isChecked():
                print('we should analyse the data now')
            
    
    def VideoRead(self):
        cap = cv2.VideoCapture(self.VideoFile)
        while(cap.isOpened()):
            ret, org_frame = cap.read()
            cv2.waitKey(25)
            if not self.StartStopButton.isChecked():
                cap.release()
                break
            EdgeLeft,EdgeRight=linedge(org_frame)
            self.VideoItem.setImage(cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB),autoRange=True)

    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()
    
 

]

        