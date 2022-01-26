from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSignal, Qt

import cv2
import pyqtgraph as pg
import sys
from pathlib import Path
from .otsu import otsu
import numpy as np
import pandas as pd
import threading
from time import sleep
from pkg_resources import resource_filename
import mimetypes

from . import FrameSupply
from . import settings
from .edge_detection import subpixel_detection as edgedetection
from .edge_analysis import analysis

pg.setConfigOptions(imageAxisOrder='row-major')

filetypemap={'image/tiff':FrameSupply.ImageReader,'image/jpeg':FrameSupply.ImageReader,'image/png':FrameSupply.ImageReader,
             'video/x-msvideo':FrameSupply.OpencvReadVideo,'video/mp4':FrameSupply.OpencvReadVideo,'video/avi':FrameSupply.OpencvReadVideo,
             'application/x-hdf':FrameSupply.Hdf5Reader}

class MainWindow(QtWidgets.QMainWindow):
    updateVideo = pyqtSignal(np.ndarray)
    updateLeftEdge = pyqtSignal(np.ndarray,np.ndarray)
    updateRightEdge = pyqtSignal(np.ndarray,np.ndarray)
    updatePlotLeft = pyqtSignal(np.ndarray,np.ndarray)
    updatePlotRight = pyqtSignal(np.ndarray,np.ndarray)
    updateLeftEdgeFit = pyqtSignal(np.ndarray,np.ndarray)
    updateRightEdgeFit = pyqtSignal(np.ndarray,np.ndarray)
    updateFrameCount=pyqtSignal(int,int)
    updateFitHeightLine=pyqtSignal(np.ndarray,np.ndarray)
    def __init__(self, *args, **kwargs):
        """
        Initialize the main window, set up all plots, and connect to defined buttons.
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(resource_filename('drop_analysis', 'Mainwindow.ui'), self)
        self.setWindowIcon(QtGui.QIcon(resource_filename('drop_analysis.data', 'icon.ico')))
        self.setWindowTitle('Drop Analysis')

        self.RootVidPlot=self.VideoWidget.getPlotItem()
        self.RootVidPlot.setAspectLocked(True)
        self.RootVidPlot.hideAxis('bottom')
        self.RootVidPlot.hideAxis('left')
        self.RootVidPlot.invertY(True)

        self.VideoItem = pg.ImageItem()
        self.RootVidPlot.addItem(self.VideoItem)
        self.LeftEdgeFit=pg.PlotCurveItem(pen=pg.mkPen(color='#2ca02c', width=4))
        self.RightEdgeFit=pg.PlotCurveItem(pen=pg.mkPen(color='#d62728', width=4))
        self.LeftEdgeItem=pg.PlotCurveItem(pen=pg.mkPen(color='#ff7f0e', width=2))
        self.RightEdgeItem=pg.PlotCurveItem(pen=pg.mkPen(color='#1f77b4', width=2))
        self.FitHeightLine=pg.PlotCurveItem(pen=pg.mkPen(color='#d62728', width=1,style=Qt.DashLine))

        self.RootVidPlot.addItem(self.RightEdgeFit)
        self.RootVidPlot.addItem(self.LeftEdgeFit)
        self.RootVidPlot.addItem(self.LeftEdgeItem)
        self.RootVidPlot.addItem(self.RightEdgeItem)
        self.RootVidPlot.addItem(self.FitHeightLine)
        self.updateVideo.connect(self.VideoItem.setImage)
        self.updateLeftEdgeFit.connect(self.LeftEdgeFit.setData)
        self.updateRightEdgeFit.connect(self.RightEdgeFit.setData)
        self.updateLeftEdge.connect(self.LeftEdgeItem.setData)
        self.updateRightEdge.connect(self.RightEdgeItem.setData)
        self.updateFitHeightLine.connect(self.FitHeightLine.setData)

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

        self.BaseLine.sigRegionChanged.connect(self._updateFitHeightLine)
        self.actionOpen.triggered.connect(self.openCall)
        self.actionSaveData.triggered.connect(self.SaveResult)
        self.actionSettings.triggered.connect(self.configSettings)
        self.StartStopButton.clicked.connect(self.StartStop)
        self.CameraToggleButton.clicked.connect(self.CameraToggle)
        self.VidRecordButton.clicked.connect(self.recordVid)
        self.VidRecordButton.hide()
        self.actionSaveVideo.triggered.connect(self.SaveVideo)
        self.actionExportVideo.triggered.connect(self.ExportVideo)

        self.FrameSource=FrameSupply.FrameSupply()
        self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])

        self.MaybeSave=False
        self.settings=settings.settings(self)

        self.kInputSlider.setValue(self.settings.config['sessiledrop']['defaultfitpixels'])
        self.kInputSpinbox.setValue(self.kInputSlider.value())
        self.kInputSlider.valueChanged.connect(lambda: self._updateFitHeightLine('slider'))
        self.kInputSpinbox.valueChanged.connect(lambda: self._updateFitHeightLine('spinbox'))

        self.updateFrameCount.connect(lambda f,n: self.FrameCounterText.setText('Frame: '+str(f)+'/'+str(n)))

    def _updateFitHeightLine(self,kset=''):
        if kset=='slider':
            self.kInputSpinbox.setValue(self.kInputSlider.value())
        elif kset=='spinbox':
            self.kInputSlider.setValue(self.kInputSpinbox.value())
        _,basearray=self.BaseLine.getArrayRegion(self.VideoItem.image, self.VideoItem, returnSlice=False, returnMappedCoords=True)
        baseinput=[[basearray[0,0],basearray[1,0]-self.kInputSpinbox.value()],[basearray[0,-1],basearray[1,-1]-self.kInputSpinbox.value()]]
        plotlinex=np.array([basearray[0,0],basearray[0,-1]])
        plotliney=np.array([basearray[1,0]-self.kInputSpinbox.value(),basearray[1,-1]-self.kInputSpinbox.value()])
        self.updateFitHeightLine.emit(plotlinex,plotliney)

        
    def closeEvent(self, event):
        if self.FrameSource.is_running:
            self.FrameSource.stop()

    def recordVid(self):
        if self.VidRecordButton.isChecked():
            self.FrameSource.record=True
        else:
            self.FrameSource.record=False


    def openCall(self):
        if self.FrameSource.is_running:
            self.FrameSource.stop()
        VideoFile, _ = QtWidgets.QFileDialog.getOpenFileName(self,'Open file')
        mimetype=mimetypes.guess_type(VideoFile)[0]
        self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])
        self.PlotItem.clear()
        if mimetype is None or not any(mimetype in key for key in filetypemap):
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText('Unkown filetype')
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()
        else:
            self.FrameSource=filetypemap[mimetype](VideoFile)
            self.FrameSource.start()
            FrameWidth,FrameHeight=self.FrameSource.getframesize()
            self.CropRoi.setPos([FrameWidth*.1,FrameHeight*.1])
            self.CropRoi.setSize([FrameWidth*.8,FrameHeight*.8])
            self.BaseLine.setPos([FrameWidth*.2,FrameHeight*.7])
            firstframe,_=self.FrameSource.getfirstframe()
            self.VideoItem.setImage(firstframe,autoRange=True)


    def StartStop(self):
        if self.StartStopButton.isChecked():
            self.StartStopButton.setText('Stop Measurement')
            self.PlotItem.setLabel('left',text='Contact angle [°]')
            if self.FrameSource.gotcapturetime:
                self.PlotItem.setLabel('bottom',text='Time [s]')
            else:
                self.PlotItem.setLabel('bottom',text='Frame number')
            self.PlotItem.addItem(self.ThetaLeftPlot)
            self.PlotItem.addItem(self.ThetaRightPlot)
            AnalysisThread = threading.Thread(target=self.RunAnalysis)
            AnalysisThread.start()

        elif not self.StartStopButton.isChecked():
            self.StartStopButton.setText('Start Measurement')

    def CameraToggle(self):
        if self.CameraToggleButton.isChecked():
            bufferpath=Path(self.settings.config['opencvcamera']['bufferpath'])
            bufferpath.parent.mkdir(parents=True,exist_ok=True)
            if bufferpath.exists():
                bufferpath.unlink()
            self.VidRecordButton.show()
            self.FrameSource=FrameSupply.OpencvCamera()
            self.FrameSource.bufferpath=bufferpath
            sleep(0.1)
            self.FrameSource.setResolution(self.settings.config['opencvcamera']['resolution'])
            self.FrameSource.setFramerate(self.settings.config['opencvcamera']['framerate'])
            self.FrameSource.start()
            FrameWidth,FrameHeight=self.FrameSource.getframesize()
            self.CropRoi.setPos([FrameWidth*.1,FrameHeight*.1])
            self.CropRoi.setSize([FrameWidth*.8,FrameHeight*.8])
            self.BaseLine.setPos([FrameWidth*.2,FrameHeight*.7])
            CameraThread = threading.Thread(target=self.CameraCapture)
            CameraThread.start()
            self.MeasurementResult=pd.DataFrame(columns=['thetaleft', 'thetaright', 'contactpointleft','contactpointright','volume','time'])
            self.PlotItem.clear()
        else:

            self.VidRecordButton.hide()

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
                baseslope=np.float64(baseinput[rightbasepoint][1]-baseinput[1-rightbasepoint][1])/(baseinput[rightbasepoint][0]-baseinput[1-rightbasepoint][0])
                base=np.array([[0,baseinput[0][1]-baseslope*baseinput[0][0]],[org_frame.shape[1],baseslope*org_frame.shape[1]+baseinput[0][1]-baseslope*baseinput[0][0]]])
                if len(org_frame.shape)==3:
                    gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)
                else:
                    gray = np.asarray(cropped)
                thresh=otsu(gray)
                CroppedEdgeLeft,CroppedEdgeRight=edgedetection(gray,thresh,self.settings.config['edgedetection']['subpixelscheme'])
                EdgeLeft=CroppedEdgeLeft+horizontalCropOffset
                EdgeRight=CroppedEdgeRight+horizontalCropOffset
                results, debuginfo = analysis(EdgeLeft,EdgeRight,base,cropped.shape,k=self.kInputSpinbox.value(),PO=self.settings.config['sessiledrop']['polyfitorder'],fittype=self.settings.config['sessiledrop']['fittype'])
                results.update({'time':framecaptime})
                self.MeasurementResult=self.MeasurementResult.append(results,ignore_index=True)
                if self.FrameSource.gotcapturetime:
                    plottime=self.MeasurementResult['time']-self.MeasurementResult.iloc[0]['time']
                    #convert from nanoseconds to seconds
                    plottime=plottime.to_numpy().astype('float')*10**-9
                else:
                    plottime=self.MeasurementResult['time'].to_numpy()
                plotleft=self.MeasurementResult['thetaleft'].to_numpy()
                plotright=self.MeasurementResult['thetaright'].to_numpy()
                self.updateLeftEdge.emit(EdgeLeft,np.arange(0,len(EdgeLeft))+verticalCropOffset)
                self.updateRightEdge.emit(EdgeRight,np.arange(0,len(EdgeRight))+verticalCropOffset)
                self.updatePlotLeft.emit(plottime,plotleft)
                self.updatePlotRight.emit(plottime,plotright)
                self.updateLeftEdgeFit.emit(debuginfo['leftfit'][0,:],verticalCropOffset+debuginfo['leftfit'][1,:])
                self.updateRightEdgeFit.emit(debuginfo['rightfit'][0,:],verticalCropOffset+debuginfo['rightfit'][1,:])
                self.MaybeSave=True
                self.updateFrameCount.emit(self.FrameSource.framenumber,self.FrameSource.nframes)
            else:
                sleep(0.001)
            if (not self.FrameSource.is_running and len(self.FrameSource.framebuffer)<1):
                break

    def SaveResult(self):
        if len(self.MeasurementResult.index)>0:
            if not self.FrameSource.gotcapturetime:
                self.MeasurementResult=self.MeasurementResult.rename(columns={"time": "framenumber"})
            SaveFileName, selectedtype =QtWidgets.QFileDialog.getSaveFileName(self,'Save file', '', "CSV Files (*.csv);;Excel Files (*.xlsx)")
            if SaveFileName=='':
                return
            if selectedtype=='CSV Files (*.csv)':
                if Path(SaveFileName).suffix=='':
                    SaveFileName=SaveFileName+'.csv'
                self.MeasurementResult.to_csv(SaveFileName,index=False)
            elif selectedtype=='Excel Files (*.xlsx)':
                if Path(SaveFileName).suffix=='':
                    SaveFileName=SaveFileName+'.xlsx'
                self.MeasurementResult.to_excel(SaveFileName,index=False)

            self.MaybeSave=False
        else:
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText('Nothing to save')
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()

    def configSettings(self):
        self.settings.show()

    def SaveVideo(self):
        if not self.VidRecordButton.isChecked():
            if hasattr(self.FrameSource, 'bufferpath') and Path(self.FrameSource.bufferpath).exists():
                SaveFileName, _ =QtWidgets.QFileDialog.getSaveFileName(self,'Save file', '', "Recorded frames (*.h5)")
                if SaveFileName=='':
                    return
                if Path(SaveFileName).suffix=='':
                    SaveFileName=SaveFileName+'.h5'
                Path(self.FrameSource.bufferpath).rename(SaveFileName)
            else:
                errorpopup=QtWidgets.QMessageBox()
                errorpopup.setText('No video has been recorded')
                errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
                errorpopup.exec_()
        else:
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText("Can't save video while recording is running")
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()

    def ExportVideo(self):
        if not self.VidRecordButton.isChecked():
            if hasattr(self.FrameSource, 'bufferpath') and Path(self.FrameSource.bufferpath).exists():
                exportsource=FrameSupply.Hdf5Reader(self.FrameSource.bufferpath)
                exportsource.start()
            elif self.CameraToggleButton.isChecked() or not Path(self.FrameSource.bufferpath).exists():
                errorpopup=QtWidgets.QMessageBox()
                errorpopup.setText('No video has been recorded')
                errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
                errorpopup.exec_()
            else:
                exportsource=self.FrameSource
            exportsource.framenumber=int(0)
            SaveFileName, _ =QtWidgets.QFileDialog.getSaveFileName(self,'Export Video', '', "Recorded frames (*.mp4)")
            if SaveFileName=='':
                return
            if Path(SaveFileName).suffix =='':
                SaveFileName=SaveFileName+'.mp4'
            fourcc=cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
            resolution=exportsource.getframesize()
            fps=exportsource.framerate
            writer=cv2.VideoWriter(SaveFileName,fourcc,fps,(int(resolution[0]),int(resolution[1])))
            totalframes=exportsource.nframes
            progress=QtWidgets.QProgressDialog("Saving Video...", "Abort", 0,totalframes , self)
            progress.setWindowModality(Qt.WindowModal)
            sleep(0.1)
            for i in range(totalframes):
                frame,_=exportsource.getnextframe()
                writer.write(np.uint8(frame))
                progress.setValue(i)
                if progress.wasCanceled():
                    break

            progress.setValue(totalframes)
            writer.release()
        else:
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText("Can't export video while recording is running")
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()

