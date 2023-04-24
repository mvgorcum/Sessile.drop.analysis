# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(620, 460)
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(SettingsDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.edgedetection = QtWidgets.QWidget()
        self.edgedetection.setObjectName("edgedetection")
        self.formLayout = QtWidgets.QFormLayout(self.edgedetection)
        self.formLayout.setObjectName("formLayout")
        self.subpixellabel = QtWidgets.QLabel(self.edgedetection)
        self.subpixellabel.setObjectName("subpixellabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.subpixellabel)
        self.subpixelmethod = QtWidgets.QComboBox(self.edgedetection)
        self.subpixelmethod.setObjectName("subpixelmethod")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.subpixelmethod)
        self.tabWidget.addTab(self.edgedetection, "")
        self.opencvcamera = QtWidgets.QWidget()
        self.opencvcamera.setObjectName("opencvcamera")
        self.formLayout_2 = QtWidgets.QFormLayout(self.opencvcamera)
        self.formLayout_2.setObjectName("formLayout_2")
        self.frameratelabel = QtWidgets.QLabel(self.opencvcamera)
        self.frameratelabel.setObjectName("frameratelabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.frameratelabel)
        self.FramerateLayout = QtWidgets.QHBoxLayout()
        self.FramerateLayout.setObjectName("FramerateLayout")
        self.framerate = QtWidgets.QDoubleSpinBox(self.opencvcamera)
        self.framerate.setProperty("value", 30.0)
        self.framerate.setObjectName("framerate")
        self.FramerateLayout.addWidget(self.framerate)
        self.tryframerate = QtWidgets.QPushButton(self.opencvcamera)
        self.tryframerate.setObjectName("tryframerate")
        self.FramerateLayout.addWidget(self.tryframerate)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.FramerateLayout)
        self.resolutionlabel = QtWidgets.QLabel(self.opencvcamera)
        self.resolutionlabel.setObjectName("resolutionlabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.resolutionlabel)
        self.ResulutionLayout = QtWidgets.QHBoxLayout()
        self.ResulutionLayout.setObjectName("ResulutionLayout")
        self.chooseresolution = QtWidgets.QComboBox(self.opencvcamera)
        self.chooseresolution.setObjectName("chooseresolution")
        self.ResulutionLayout.addWidget(self.chooseresolution)
        self.autodetectresolution = QtWidgets.QPushButton(self.opencvcamera)
        self.autodetectresolution.setObjectName("autodetectresolution")
        self.ResulutionLayout.addWidget(self.autodetectresolution)
        self.formLayout_2.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.ResulutionLayout)
        self.resolutionlabel_2 = QtWidgets.QLabel(self.opencvcamera)
        self.resolutionlabel_2.setObjectName("resolutionlabel_2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.resolutionlabel_2)
        self.BufferpathLayout = QtWidgets.QHBoxLayout()
        self.BufferpathLayout.setObjectName("BufferpathLayout")
        self.BufferPathDisplay = QtWidgets.QLineEdit(self.opencvcamera)
        self.BufferPathDisplay.setReadOnly(True)
        self.BufferPathDisplay.setObjectName("BufferPathDisplay")
        self.BufferpathLayout.addWidget(self.BufferPathDisplay)
        self.ChangeBufferPath = QtWidgets.QPushButton(self.opencvcamera)
        self.ChangeBufferPath.setObjectName("ChangeBufferPath")
        self.BufferpathLayout.addWidget(self.ChangeBufferPath)
        self.formLayout_2.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.BufferpathLayout)
        self.tabWidget.addTab(self.opencvcamera, "")
        self.sessiledrop = QtWidgets.QWidget()
        self.sessiledrop.setObjectName("sessiledrop")
        self.formLayout_3 = QtWidgets.QFormLayout(self.sessiledrop)
        self.formLayout_3.setObjectName("formLayout_3")
        self.heightlabel = QtWidgets.QLabel(self.sessiledrop)
        self.heightlabel.setObjectName("heightlabel")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.heightlabel)
        self.defaultfitheight = QtWidgets.QSpinBox(self.sessiledrop)
        self.defaultfitheight.setMaximum(10000)
        self.defaultfitheight.setProperty("value", 40)
        self.defaultfitheight.setObjectName("defaultfitheight")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.defaultfitheight)
        self.fittypelabel = QtWidgets.QLabel(self.sessiledrop)
        self.fittypelabel.setObjectName("fittypelabel")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.fittypelabel)
        self.FittypeLayout = QtWidgets.QHBoxLayout()
        self.FittypeLayout.setObjectName("FittypeLayout")
        self.fittype = QtWidgets.QComboBox(self.sessiledrop)
        self.fittype.setObjectName("fittype")
        self.FittypeLayout.addWidget(self.fittype)
        self.polyfitorderlabel = QtWidgets.QLabel(self.sessiledrop)
        self.polyfitorderlabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.polyfitorderlabel.setObjectName("polyfitorderlabel")
        self.FittypeLayout.addWidget(self.polyfitorderlabel)
        self.polyfitorder = QtWidgets.QSpinBox(self.sessiledrop)
        self.polyfitorder.setObjectName("polyfitorder")
        self.FittypeLayout.addWidget(self.polyfitorder)
        self.formLayout_3.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.FittypeLayout)
        self.tabWidget.addTab(self.sessiledrop, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.okcancelbuttons = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.okcancelbuttons.setOrientation(QtCore.Qt.Horizontal)
        self.okcancelbuttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.okcancelbuttons.setObjectName("okcancelbuttons")
        self.verticalLayout.addWidget(self.okcancelbuttons)

        self.retranslateUi(SettingsDialog)
        self.tabWidget.setCurrentIndex(1)
        self.okcancelbuttons.accepted.connect(SettingsDialog.accept) # type: ignore
        self.okcancelbuttons.rejected.connect(SettingsDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Settings"))
        self.subpixellabel.setText(_translate("SettingsDialog", "Subpixel method:"))
        self.subpixelmethod.setToolTip(_translate("SettingsDialog", "Select subpixel edge detection method"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.edgedetection), _translate("SettingsDialog", "Edge Detection"))
        self.frameratelabel.setText(_translate("SettingsDialog", "Framerate:"))
        self.tryframerate.setText(_translate("SettingsDialog", "Try framerate"))
        self.resolutionlabel.setText(_translate("SettingsDialog", "Resolution:"))
        self.autodetectresolution.setText(_translate("SettingsDialog", "Autodetect"))
        self.resolutionlabel_2.setText(_translate("SettingsDialog", "Buffer Path:"))
        self.ChangeBufferPath.setText(_translate("SettingsDialog", "Change Path"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.opencvcamera), _translate("SettingsDialog", "Opencv Camera"))
        self.heightlabel.setText(_translate("SettingsDialog", "Default height:"))
        self.fittypelabel.setText(_translate("SettingsDialog", "Fit type:"))
        self.polyfitorderlabel.setText(_translate("SettingsDialog", "Order:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sessiledrop), _translate("SettingsDialog", "Sessile Drops"))