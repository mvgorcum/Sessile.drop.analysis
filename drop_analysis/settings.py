import toml
from PyQt5 import QtWidgets, uic, QtGui
import os
from pathlib import Path
from pkg_resources import resource_filename
import appdirs

class settings(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(settings, self).__init__(parent)
        uic.loadUi(resource_filename('drop_analysis', 'Settings.ui'), self)
        self.appname='drop_analysis'
        self.appauthor = "mvgorcum"
        self.configpath=Path(appdirs.user_config_dir(self.appname))
        defaultconfig=toml.load(resource_filename("drop_analysis", "config.toml"))
        if self.configpath.joinpath('config.toml').exists():
            userconfig=toml.load(self.configpath.joinpath('config.toml'))
        else:
            userconfig={}
        self.config={**defaultconfig,**userconfig}
        self.config['opencvcamera']['bufferpath']=appdirs.user_cache_dir(self.appname, self.appauthor)
        self.okcancelbuttons.accepted.connect(self._saveconfig)
        self.autodetectresolution.clicked.connect(self._detectres)
        self.fittype.activated[str].connect(self._showhidepolyorder)
        self.tryframerate.clicked.connect(self._tryframerate)
        self.ChangeBufferPath.clicked.connect(self._changebufferpath)
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
        self.fittype.addItem("Ellipse","Ellipse")
        self.fittype.setCurrentIndex(self.fittype.findData(self.config['sessiledrop']['fittype']))
        self.polyfitorder.setValue(self.config['sessiledrop']['polyfitorder'])
        self.defaultfitheight.setValue(self.config['sessiledrop']['defaultfitpixels'])
        self.BufferPathDisplay.setText(self.config['opencvcamera']['bufferpath'])

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
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText('Error opening camera, is the Live Camera disabled?')
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()
            return {}
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FPS, self.framerate.value())
            actualframerate = int(cap.get(cv2.CAP_PROP_FPS))
            self.framerate.setValue(actualframerate)
            self.config['opencvcamera']['framerate']=actualframerate

        else:
            errorpopup=QtWidgets.QMessageBox()
            errorpopup.setText('Error opening camera, is the Live camera disabled?')
            errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
            errorpopup.exec_()

    def _saveconfig(self):
        self.config['opencvcamera']['framerate']=self.framerate.value()
        self.config['opencvcamera']['resolution']=self.chooseresolution.currentData()
        self.config['opencvcamera']['bufferpath']=self.BufferPathDisplay.toPlainText()
        self.config['edgedetection']['subpixelscheme']=self.subpixelmethod.currentData()
        self.config['sessiledrop']['fittype']=self.fittype.currentData()
        self.config['sessiledrop']['polyfitorder']=self.polyfitorder.value()
        self.config['sessiledrop']['defaultfitpixels']=self.defaultfitheight.value()
        if not self.configpath.exists():
            self.configpath.mkdir(parents=True)
        with open(self.configpath.joinpath('config.toml'),'w+') as configfile:
            toml.dump(self.config,configfile)

    def _changebufferpath(self):
        SaveFileName, _ =QtWidgets.QFileDialog.getSaveFileName(self,'Buffer file location', '', "Buffer file (*.h5)")
        if SaveFileName=='':
            return
        if Path(SaveFileName).suffix =='':
            SaveFileName=SaveFileName+'.h5'
        self.config['opencvcamera']['bufferpath']=SaveFileName
        self.BufferPathDisplay.setText(self.config['opencvcamera']['bufferpath'])



def detect_resolutions():
    """
    Using the list of common resolutions (downloaded from https://en.wikipedia.org/wiki/List_of_common_resolutions (CC-BY-SA 3.0))
    we try to set all resolutions and find all successfull resolutions and return that as a dict
    """
    import pandas as pd
    import cv2
    resolutions = {}
    resolutionlist=pd.read_csv(resource_filename('drop_analysis.data', 'common_resolutions.csv'),
                                                 skiprows=1)
    try:
        cap = cv2.VideoCapture(0)
    except:
        errorpopup=QtWidgets.QMessageBox()
        errorpopup.setText('Error opening camera, is the Live Camera disabled?')
        errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
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
        errorpopup=QtWidgets.QMessageBox()
        errorpopup.setText('Error opening camera, is the Live camera disabled?')
        errorpopup.setStandardButtons(QtWidgets.QMessageBox.Ok)
        errorpopup.exec_()
    return resolutions
