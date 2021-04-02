import toml
from PyQt5 import QtWidgets, uic, QtGui
import os

class settings(QtGui.QDialog):
    def __init__(self, parent=None):
        super(settings, self).__init__(parent)
        uic.loadUi('Settings.ui', self)
        self.config=toml.load("config.toml")
        self.okcancelbuttons.accepted.connect(self._saveconfig)
        self.autodetectresolution.clicked.connect(self._detectres)
        self.fittype.activated[str].connect(self._showhidepolyorder)
        self.tryframerate.clicked.connect(self._tryframerate)
        self._setguioptions()

    def _detectres(self):
        resolutions=detect_resolutions()
        self.chooseresolution.clear()
        for name,resolution in resolutions.items():
            self.chooseresolution.addItem(name,resolution)


    def _setguioptions(self):
        self.subpixelmethod.addItem('Linear interpolation',"Linear")
        self.subpixelmethod.addItem('Error function fit',"Errorfunction")
        self.subpixelmethod.setCurrentIndex(self.subpixelmethod.findData(self.config['edgedetection']['subpixelscheme']))
        self.chooseresolution.addItem(str(self.config['opencvcamera']['resolution'][0])+'x'+str(self.config['opencvcamera']['resolution'][1]),self.config['opencvcamera']['resolution'])
        self.framerate.setValue(self.config['opencvcamera']['framerate'])
        self.fittype.addItem("Polyfit","Polyfit")
        self.fittype.setCurrentIndex(self.fittype.findData(self.config['sessiledrop']['fittype']))
        self.polyfitorder.setValue(self.config['sessiledrop']['polyfitorder'])
        self.defaultfitheight.setValue(self.config['sessiledrop']['defaultfitpixels'])

    def _showhidepolyorder(self):
        if self.fittype.currentText() == "Polyfit":
            self.polyfitorder.show()
            self.polyfitorderlabel.show()
        else:
            self.polyfitorder.hide()
            self.polyfitorderlabel.hide()
    
    def _tryframerate(self):
        import cv2
        try:
            cap = cv2.VideoCapture(0)
        except:
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Error opening camera, is the Live Camera disabled?')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()
            return {}
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FPS, self.framerate.value())
            actualframerate = int(cap.get(cv2.CAP_PROP_FPS))
            self.framerate.setValue(actualframerate)
            self.config['opencvcamera']['framerate']=actualframerate

        else:
            errorpopup=QtGui.QMessageBox()
            errorpopup.setText('Error opening camera, is the Live camera disabled?')
            errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
            errorpopup.exec_()

    def _saveconfig(self):
        self.config['opencvcamera']['framerate']=self.framerate.value()
        self.config['opencvcamera']['resolution']=self.chooseresolution.currentData()
        self.config['edgedetection']['subpixelscheme']=self.subpixelmethod.currentData()
        self.config['sessiledrop']['fittype']=self.fittype.currentData()
        self.config['sessiledrop']['polyfitorder']=self.polyfitorder.value()
        self.config['sessiledrop']['defaultfitpixels']=self.defaultfitheight.value()
        with open("config.toml",'w') as configfile:
            toml.dump(self.config,configfile)

      
def detect_resolutions():
    """
    Using the list of common resolutions (downloaded from https://en.wikipedia.org/wiki/List_of_common_resolutions (CC-BY-SA 3.0))
    we try to set all resolutions and find all successfull resolutions and return that as a dict
    """
    import pandas as pd
    import cv2
    resolutions = {}
    resolutionlist=pd.read_csv('common_resolutions.csv',skiprows=1)
    try:
        cap = cv2.VideoCapture(0)
    except:
        errorpopup=QtGui.QMessageBox()
        errorpopup.setText('Error opening camera, is the Live Camera disabled?')
        errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
        errorpopup.exec_()
        return {}
    if cap.isOpened():
        for _, resolution in resolutionlist.iterrows():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution.W)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution.H)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            resolutions[str(width)+"x"+str(height)] = [width,height]
    else:
        errorpopup=QtGui.QMessageBox()
        errorpopup.setText('Error opening camera, is the Live camera disabled?')
        errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
        errorpopup.exec_()
    return resolutions