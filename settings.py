import toml
from PyQt5 import QtWidgets, uic, QtGui

class settings(QtGui.QDialog):
    def __init__(self, parent=None):
        super(settings, self).__init__(parent)
        uic.loadUi('Settings.ui', self)
        self.config=toml.load("config.toml")
        self.okcancelbuttons.accepted.connect(self.saveconfig)
        self.autodetectresolution.clicked.connect(self.detectres)
    def detectres(self):
        print(self.blaat)
        self.resolutions=detect_resolutions()
        print(self.resolutions)
    
    def saveconfig(self):
        print('ok')


        



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
        for resolution in resolutionlist.iterrows():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution.W)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution.H)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            resolutions[str(width)+"x"+str(height)] = [width,height]
    else:
        errorpopup=QtGui.QMessageBox()
        errorpopup.setText('Error opening camera, is the Live camera disabled?')
        errorpopup.setStandardButtons(QtGui.QMessageBox.Ok)
        errorpopup.exec_()
    return resolutions